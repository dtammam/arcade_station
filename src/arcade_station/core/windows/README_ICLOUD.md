# iCloud Photo Sync Manager

This component manages the synchronization of screenshots to iCloud on Windows by periodically restarting iCloud services and cleaning the upload directory.

## Files

- **manage_icloud.py**: Main Python script that handles the iCloud services management
- **kill_icloud_processes.py**: Utility script to stop all iCloud-related processes

## Features

- Periodically restarts iCloud services to keep them running
- Cleans up the upload directory after photos have been synced
- Runs completely in the background as a daemon thread
- Configurable through `screenshot_config.toml`
- Uses the standard logging system
- Cleanly integrates with the startup process

## Configuration

The iCloud sync is configured in `config/screenshot_config.toml`:

```toml
[icloud_upload]
enabled = true                # Enable/disable iCloud upload management
interval_seconds = 360        # Interval between service restarts
delete_after_upload = true    # Whether to delete files after they're uploaded
upload_directory = "C:/Users/me/Pictures/Uploads"  # Directory to monitor
apple_services_path = "C:/Program Files (x86)/Common Files/Apple/Internet Services/"  # Path to Apple services
processes_to_restart = [      # iCloud processes to restart
  "iCloudServices",
  "iCloudPhotos"
]
```

## Usage

The iCloud manager starts automatically when `start_frontend_apps.py` runs if the `enabled` setting is `true`. You can also:

- Run `manage_icloud.py` directly to start in foreground mode
- Use `kill_icloud_processes.py` to stop any running iCloud processes

## Troubleshooting

- Check the logs for messages with the "ICLOUD" prefix
- Ensure the paths in the configuration file are correct
- Verify iCloud services are installed and working on your system
- Make sure the upload directory exists and is accessible
- Check if the Apple services exist at the specified path

## Implementation Details

The manager works by:

1. Loading configuration from the TOML file
2. Starting a daemon thread that runs in the background
3. Periodically stopping and restarting iCloud services 
4. Waiting for the specified interval
5. Deleting files from the upload directory if enabled
6. Repeating the cycle

This approach ensures that iCloud services are regularly refreshed, which helps prevent them from stalling and ensures photos are synced to iCloud properly. 