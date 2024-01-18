from flask import Flask, jsonify
import re
import configparser
import subprocess
import traceback
import os
import sys
import logging

app = Flask(__name__)

from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('raid_endpoint.log', maxBytes=10*1024*1024, backupCount=1)
logging.basicConfig(handlers=[handler], level=logging.INFO)

def sanitize_input(volume):
    if not re.match(r'^md[0-9]+$', volume):
        return False
    return True

def get_raid_detail(volume):
    if not sanitize_input(volume):
        return {'error': 'Invalid volume name'}

    try:
        output = subprocess.run(['mdadm', '--detail', '/dev/md{}'.format(volume)], capture_output=True, text=True).stdout
        match = re.search(r'Resync Status: (\d+)%', output)
        resync_status = int(match.group(1)) if match else 100

        state_match = re.search(r'State : (.*)', output)
        state = state_match.group(1) if state_match else 'Unknown'
        active_disks = int(re.search(r'Active Devices : (\d+)', output).group(1))
        working_disks = int(re.search(r'Working Devices : (\d+)', output).group(1))
        failed_disks = int(re.search(r'Failed Devices : (\d+)', output).group(1))
        spare_disks = int(re.search(r'Spare Devices : (\d+)', output).group(1))

        return {
            'resync_status': resync_status,
            'state': state,
            'active_disks': active_disks,
            'working_disks': working_disks,
            'failed_disks': failed_disks,
            'spare_disks': spare_disks
        }
    except (subprocess.CalledProcessError, re.error) as e:
        logging.error(traceback.format_exc())
        return {'error': 'An error occurred'}

def get_free_space(volume):
    if not sanitize_input(volume):
        return {'error': 'Invalid volume name'}

    try:
        output = subprocess.run(['df', '/dev/md{}'.format(volume)], capture_output=True, text=True).stdout.splitlines()[-1]
        _, total, used, free, percent, _ = output.split()
        return percent.rstrip('%')
    except (subprocess.CalledProcessError, re.error) as e:
        logging.error(traceback.format_exc())
        return {'error': 'An error occurred'}

@app.route('/raid_status/<volume>')
def raid_status(volume):
    try:
        status = get_raid_detail(volume)
        status['free_space'] = get_free_space(volume)
    except FileNotFoundError:
        logging.error(traceback.format_exc())
        status = {'error': 'Volume not found'}
    return jsonify(status)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(dir_path, 'raid_endpoint.conf')
    config.read(config_path)
    host = config.get('DEFAULT', 'HOST')
    port = config.getint('DEFAULT', 'PORT')
    use_https = config.getboolean('DEFAULT', 'USE_HTTPS')
    certificate_path = config.get('DEFAULT', 'CERTIFICATE_PATH')
    key_path = config.get('DEFAULT', 'KEY_PATH')

    raid_volumes = subprocess.run(['ls', '/dev/md*'], capture_output=True, text=True).stdout.split()

    if use_https:
        if os.path.exists(certificate_path) and os.path.exists(key_path):
            app.run(host=host, port=port, ssl_context=(certificate_path, key_path))
        else:
            app.run(host=host, port=port)
    else:
        app.run(host=host, port=port)
