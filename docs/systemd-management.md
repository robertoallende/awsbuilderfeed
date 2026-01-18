# BuilderFeed Systemd Service Management

This guide covers managing BuilderFeed as a systemd service on Raspberry Pi.

## Architecture

BuilderFeed runs as two systemd services:

```
prefect-server.service  →  Prefect UI & API (localhost:4200)
        ↓
builderfeed.service     →  Flow deployments (fetch & tweet)
```

The `builderfeed` service depends on `prefect-server` and starts automatically after it.

## Installation

```bash
sudo ./scripts/install-services.sh
```

This will:
- Copy service files to `/etc/systemd/system/`
- Enable services to start on boot
- Start both services

## Uninstallation

```bash
sudo ./scripts/uninstall-services.sh
```

## Common Commands

### Check Status

```bash
# Both services
systemctl status prefect-server builderfeed

# Individual service
systemctl status builderfeed
systemctl status prefect-server
```

### View Logs

```bash
# Follow builderfeed logs (live)
journalctl -u builderfeed -f

# Follow prefect-server logs (live)
journalctl -u prefect-server -f

# View last 100 lines
journalctl -u builderfeed -n 100

# View logs since boot
journalctl -u builderfeed -b

# View logs from specific time
journalctl -u builderfeed --since "1 hour ago"
journalctl -u builderfeed --since "2024-01-19 10:00:00"
```

### Start / Stop / Restart

```bash
# Restart builderfeed (prefect-server stays running)
sudo systemctl restart builderfeed

# Restart both services
sudo systemctl restart prefect-server builderfeed

# Stop both services
sudo systemctl stop builderfeed prefect-server

# Start both services
sudo systemctl start prefect-server builderfeed
```

### Enable / Disable Auto-Start

```bash
# Disable auto-start on boot
sudo systemctl disable builderfeed prefect-server

# Re-enable auto-start on boot
sudo systemctl enable builderfeed prefect-server
```

## Prefect Web UI

Access the Prefect dashboard at: **http://localhost:4200**

From the UI you can:
- View flow runs and their status
- See upcoming scheduled runs
- Inspect logs for individual runs
- Manually trigger flows

## Troubleshooting

### Service won't start

Check logs for errors:
```bash
journalctl -u builderfeed -n 50 --no-pager
journalctl -u prefect-server -n 50 --no-pager
```

### Port 4200 already in use

Another process is using the port. Find and stop it:
```bash
sudo lsof -i :4200
```

### Flows not running

1. Check builderfeed service is active:
   ```bash
   systemctl status builderfeed
   ```

2. Verify Prefect server is accessible:
   ```bash
   curl http://localhost:4200/api/health
   ```

3. Check the Prefect UI for failed runs at http://localhost:4200

### After code changes

Restart the builderfeed service to pick up changes:
```bash
sudo systemctl restart builderfeed
```

## Service File Locations

- Service definitions: `/etc/systemd/system/prefect-server.service` and `/etc/systemd/system/builderfeed.service`
- Source files: `./systemd/` directory in the project

If you modify the service files in `./systemd/`, reinstall them:
```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart prefect-server builderfeed
```

## Environment Variables

The services load environment from the project's `.env` file via python-dotenv. Twitter API credentials are configured there.

To update credentials:
1. Edit `.env` file
2. Restart the service: `sudo systemctl restart builderfeed`
