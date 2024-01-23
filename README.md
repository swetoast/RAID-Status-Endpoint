# RAID Status Endpoint

This is a Flask application that provides an API endpoint to get the status of RAID volumes.

## Features

- **RAID Detail Retrieval**: Retrieves RAID details including resync status, state, active disks, working disks, failed disks, and spare disks.
- **Free Space Retrieval**: Retrieves the free space of the volume.
- **API Endpoint**: Provides a route `/raid_status/<volume>` to get the status of a RAID volume.

## Installation

1. Clone this repository.
2. Install the required Python packages: Flask, re, configparser, subprocess, traceback, os.

## Configuration

Configure the application by modifying the `raid_endpoint.conf` file in the same directory as the script. The configuration includes the host, port, whether to use HTTPS, and paths to the certificate and key files if HTTPS is used.

## Usage

Run the script to start the Flask application.

## API Endpoints

- `GET /raid_status/<volume>`: Returns a JSON object with the status of the specified RAID volume. The status includes resync status, state, active disks, working disks, failed disks, spare disks, and free space.

## Home Assistant Integration

This application can be integrated with Home Assistant using the REST sensor. Here's an example configuration:

```yaml
sensor:
  - platform: rest
    resource: http://IP_ADDRESS:PORT/raid_status/VOLUME_NAME
    name: RAID Status
    value_template: '{{ value_json.state }}'
    json_attributes_path: "$.attributes"
    json_attributes:
      - resync_status
      - active_disks
      - failed_disks
      - used_space
      - resync_speed
```
## Support

If you find these lists useful, please consider giving me a star on GitHub!
