# RAID Status Flask Application

This is a Flask application that provides an API endpoint to get the status of RAID volumes.

## Features

- Sanitizes input to ensure only valid volume names are processed.
- Retrieves RAID detail including resync status, state, active disks, working disks, failed disks, and spare disks.
- Retrieves free space of the volume.
- Provides a route `/raid_status/<volume>` to get the status of a RAID volume.

## How to Run

1. Clone this repository.
2. Install the required Python packages: Flask, re, configparser, subprocess, traceback, os.
3. Configure the application by modifying the `raid_endpoint.conf` file in the same directory as the script. The configuration includes the host, port, whether to use HTTPS, and paths to the certificate and key files if HTTPS is used.
4. Run the script.

## API Endpoints

- `GET /raid_status/<volume>`: Returns a JSON object with the status of the specified RAID volume. The status includes resync status, state, active disks, working disks, failed disks, spare disks, and free space.

## Home Assistant Integration

You can use the Home Assistant REST sensor to get the RAID status. Here's an example configuration:

```yaml
sensor:
  - platform: rest
    resource: http://IP_ADDRESS:PORT/raid_status/VOLUME_NAME
    name: RAID Status
    value_template: '{{ value_json.state }}'
    json_attributes:
      - resync_status
      - active_disks
      - working_disks
      - failed_disks
      - spare_disks
      - free_space
