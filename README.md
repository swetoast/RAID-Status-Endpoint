# RAID Status Endpoint

This is a Flask application that provides an endpoint to check the status of RAID volumes on a server.

## Features

- **RAID Volume Detail**: The application can fetch and display detailed information about each RAID volume, including resync status, state, number of active disks, working disks, failed disks, and spare disks.
- **HTTPS Support**: The application supports HTTPS if a valid certificate and key are provided.

## Usage

1. Install the required Python packages: Flask, os, re, configparser.
2. Configure the application by editing the 'raid_endpoint.conf' file. You can specify the host, port, whether to use HTTPS, and paths to your SSL certificate and key.
3. Run the application with Python. If you've enabled HTTPS and the certificate or key are not found, the application will run without HTTPS.

## Endpoints

- `/raid_status`: Returns a JSON object with the status of each RAID volume.

## Configuration

This configuration is read from a file named raid_endpoint.conf. The configuration parameters are:

    HOST: The hostname where the Flask app will run.
    PORT: The port on which the Flask app will listen.
    USE_HTTPS: A boolean value indicating whether to use HTTPS or not.
    CERTIFICATE_PATH: The path to the SSL certificate file (used if USE_HTTPS is True).
    KEY_PATH: The path to the SSL key file (used if USE_HTTPS is True).


[DEFAULT]
HOST = 127.0.0.1
PORT = 5001
USE_HTTPS = false
CERTIFICATE_PATH = /path/to/cert.crt
KEY_PATH = /path/to/key.key

## Note

This application uses the `mdadm` command to fetch RAID details, so it must be run on a system that has `mdadm` installed and RAID volumes configured.

## Home Assistant Integration

You can set up a Home Assistant RESTful sensor to interact with the Raid Status Endpoint script:

```yaml
sensor:
  - platform: rest
    resource: http://IP_ADRESS:PORT/raid_status
    name: Raid Status
    json_attributes:
      - resync_status
      - state
      - active_disks
      - working_disks
      - failed_disks
      - spare_disks
```
or if you have more then one raid configuration in your system

```yaml
sensor:
  - platform: rest
    name: RAID Status
    resource: http://IP_ADRESS:PORT/raid_status
    json_attributes:
      - md0
      - md1
      - md2
  - platform: template
    sensors:
      raid_md0_state:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["state"] }}'
      raid_md0_active_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["active_disks"] }}'
      raid_md0_failed_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["failed_disks"] }}'
      raid_md0_resync_status:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["resync_status"] }}'
      raid_md0_spare_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["spare_disks"] }}'
      raid_md0_working_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md0"]["working_disks"] }}'
      raid_md1_state:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["state"] }}'
      raid_md1_active_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["active_disks"] }}'
      raid_md1_failed_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["failed_disks"] }}'
      raid_md1_resync_status:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["resync_status"] }}'
      raid_md1_spare_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["spare_disks"] }}'
      raid_md1_working_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md1"]["working_disks"] }}'
      raid_md2_state:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["state"] }}'
      raid_md2_active_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["active_disks"] }}'
      raid_md2_failed_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["failed_disks"] }}'
      raid_md2_resync_status:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["resync_status"] }}'
      raid_md2_spare_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["spare_disks"] }}'
      raid_md2_working_disks:
        value_template: '{{ states.sensor.raid_status.attributes["md2"]["working_disks"] }}'

```
