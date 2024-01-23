# RAID Status Endpoint

This is a Flask application that provides an API endpoint to get the status of RAID volumes.

## Features

- **RAID Detail Retrieval**: Retrieves RAID details including resync status, state, active disks, failed disks, used space, and resync speed.
- **API Endpoint**: Provides routes `/raid_status/<volume>` and `/raid_status` to get the status of a specific RAID volume or all RAID volumes, respectively.

## Installation

1. Clone this repository.
2. Install the required Python packages: Flask, re, configparser, subprocess, os.

## Configuration

Configure the application by modifying the `raid_endpoint.conf` file in the same directory as the script. The configuration includes the host, port, whether to use HTTPS, and paths to the certificate and key files if HTTPS is used.

## Usage

Run the script to start the Flask application.

## API Endpoints

- `GET /raid_status/<volume>`: Returns a JSON object with the status of the specified RAID volume. The status includes resync status, state, active disks, failed disks, used space, and resync speed.
- `GET /raid_status`: Returns a JSON object with the status of all RAID volumes.

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
## Importing a Blueprint in Home Assistant

Follow these steps to import a blueprint in Home Assistant:

1. Navigate to `Configuration` → `Automations & Scenes` → `Blueprints`.
2. Click on the `Import Blueprint` button located at the bottom right.
3. A dialog will pop-up asking for the URL of the blueprint. Enter the URL of your blueprint. For example: `https://raw.githubusercontent.com/swetoast/RAID-Status-Endpoint/main/blueprint_raid_status.yaml`
4. Click on `Preview Blueprint`. This will load the blueprint and show a preview in the import dialog.
5. You can change the name of the blueprint if you wish, and then click `Import Blueprint`.

The blueprint can now be used for creating automations. If the blueprint goes through revisions, you may need to re-import it to get the changes.

Please note that these instructions are based on the Home Assistant user interface as of the time of writing and may vary with future updates.

