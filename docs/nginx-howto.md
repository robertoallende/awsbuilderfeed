# Nginx Setup for BuilderFeed

This guide covers setting up nginx as a reverse proxy to expose the Prefect UI at `data.allende.nz`.

## Prerequisites

- nginx installed (`sudo apt install nginx`)
- BuilderFeed systemd services running
- DNS configured to point `data.allende.nz` to your server

## Installation

```bash
# Copy config to nginx sites-available
sudo cp systemd/nginx-builderfeed.conf /etc/nginx/sites-available/builderfeed

# Enable the site
sudo ln -s /etc/nginx/sites-available/builderfeed /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Adding HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate and auto-configure nginx
sudo certbot --nginx -d data.allende.nz

# Certbot will automatically:
# - Obtain the certificate
# - Modify the nginx config for HTTPS
# - Set up auto-renewal
```

Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Configuration File

Location: `/etc/nginx/sites-available/builderfeed`

```nginx
server {
    listen 80;
    server_name data.allende.nz;

    location / {
        proxy_pass http://127.0.0.1:4200;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

The WebSocket headers (`Upgrade`, `Connection`) enable Prefect's real-time log streaming and UI updates.

## Common Commands

```bash
# Test configuration
sudo nginx -t

# Reload configuration (no downtime)
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check status
systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log
```

## Troubleshooting

### 502 Bad Gateway

Prefect server isn't running:
```bash
systemctl status prefect-server
sudo systemctl start prefect-server
```

### 504 Gateway Timeout

Prefect is slow to respond. Increase timeout in nginx config:
```nginx
proxy_read_timeout 120;
proxy_connect_timeout 120;
proxy_send_timeout 120;
```

### WebSocket connection failed

Ensure the upgrade headers are present in the config. Check browser console for specific errors.

### Certificate renewal failed

Check certbot logs:
```bash
sudo journalctl -u certbot
```

Manually renew:
```bash
sudo certbot renew
```

## Removing the Site

```bash
# Disable site
sudo rm /etc/nginx/sites-enabled/builderfeed

# Reload nginx
sudo systemctl reload nginx

# Optionally remove config file
sudo rm /etc/nginx/sites-available/builderfeed
```
