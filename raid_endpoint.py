from flask import Flask, jsonify, redirect, url_for
import os
import re
import configparser

app = Flask(__name__)

def get_raid_detail(volume):
    if not re.match(r'^md\d+$', volume):
        return {'error': 'Invalid volume name'}

    try:
        output = os.popen(f'mdadm --detail /dev/{volume}').read()
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
    except Exception as e:
        return {'error': str(e)}

def get_free_space(volume):
    try:
        output = os.popen(f'df /dev/{volume}').readlines()[-1]
        _, total, used, free, percent, _ = output.split()
        return percent.rstrip('%')
    except Exception as e:
        return {'error': str(e)}

@app.route('/raid_status/<volume>')
def raid_status(volume):
    if os.path.exists(f'/dev/{volume}'):
        status = get_raid_detail(volume)
        status['free_space'] = get_free_space(volume)
    else:
        status = {'error': 'Volume not found'}
    return jsonify(status)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/etc/raid_endpoint.conf')
    host = config.get('DEFAULT', 'HOST')
    port = config.getint('DEFAULT', 'PORT')
    use_https = config.getboolean('DEFAULT', 'USE_HTTPS')
    certificate_path = config.get('DEFAULT', 'CERTIFICATE_PATH')
    key_path = config.get('DEFAULT', 'KEY_PATH')

    raid_volumes = os.popen('ls /dev/md* | cut -d"/" -f3').read().split()
    for volume in raid_volumes:
        if os.path.exists(f'/dev/{volume}'):
            print(f"Endpoint created: /raid_status/{volume}")

    if use_https:
        if os.path.exists(certificate_path) and os.path.exists(key_path):
            app.run(host=host, port=port, ssl_context=(certificate_path, key_path))
        else:
            print("Certificate or key not found, running without HTTPS")
            app.run(host=host, port=port)
    else:
        app.run(host=host, port=port)
