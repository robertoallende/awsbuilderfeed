# Unit 06: Raspberry Pi Deployment

## Objective

Deploy BuilderFeed as a production service on Raspberry Pi with:
- Systemd services for automatic startup and management
- Prefect server for web UI monitoring
- Nginx reverse proxy for external access

## Implementation

### Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────┐
│  nginx (data.allende.nz:80)     │
│  Reverse proxy                  │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  systemd                        │
│  ├── prefect-server.service     │◄── localhost:4200 (Prefect UI)
│  └── builderfeed.service        │◄── Flow deployments
└─────────────────────────────────┘
```

### Systemd Services

**prefect-server.service**: Runs Prefect server on localhost:4200
- Starts after network
- Auto-restarts on failure
- Provides web UI for monitoring

**builderfeed.service**: Runs deploy.py flow deployments
- Depends on prefect-server.service
- Waits 5 seconds for server startup
- Sets PREFECT_API_URL for server connection

### Nginx Configuration

Reverse proxy configuration for `data.allende.nz`:
- Proxies to localhost:4200
- WebSocket support for real-time updates
- Ready for HTTPS via Let's Encrypt

### Management Scripts

- `scripts/install-services.sh`: Copies services, enables, starts
- `scripts/uninstall-services.sh`: Stops, disables, removes services

## AI Interactions

Used Claude to:
1. Generate systemd service files with proper dependencies
2. Create nginx config with WebSocket headers for Prefect
3. Write install/uninstall scripts
4. Generate documentation for ongoing management

## Files Modified

- `systemd/prefect-server.service` (new)
- `systemd/builderfeed.service` (new)
- `systemd/nginx-builderfeed.conf` (new)
- `scripts/install-services.sh` (new)
- `scripts/uninstall-services.sh` (new)
- `docs/systemd-management.md` (new)
- `docs/nginx-howto.md` (new)
- `.gitignore` (updated - added `._*` pattern)

## Status: Complete

**Implemented:**
- Systemd service for Prefect server (localhost:4200)
- Systemd service for BuilderFeed flows (depends on server)
- Install/uninstall scripts for service management
- Nginx reverse proxy config for data.allende.nz
- Documentation for systemd and nginx management

**Verification Steps:**
1. Run `sudo ./scripts/install-services.sh`
2. Check status: `systemctl status prefect-server builderfeed`
3. View logs: `journalctl -u builderfeed -f`
4. Access Prefect UI: http://localhost:4200
5. Reboot and verify auto-start

**Useful Commands:**
```bash
# View status
systemctl status prefect-server builderfeed

# View logs
journalctl -u builderfeed -f

# Restart
sudo systemctl restart builderfeed

# Stop all
sudo systemctl stop builderfeed prefect-server
```
