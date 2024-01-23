from flask import Flask, jsonify
import subprocess
import re
import configparser
import os

app = Flask(__name__)

def parse_mdstat():
    mdstat = subprocess.check_output(['cat', '/proc/mdstat']).decode('utf-8').split('\n')
    data = {}
    device = None
    for line in mdstat:
        if line.startswith('md'):
            device, info = line.split(' : ')
            data[device] = {
                'resync_status': 0.0,
                'active_disks': None,
                'failed_disks': 0,
                'used_space': None,
                'resync_speed': 0,
                'raid_status': 'clean'
            }
            if 'active' in info:
                data[device]['active_disks'] = len(re.findall(r'\[\d\]', info))
        elif device and line.strip():
            raid_status = re.search(r'\[[U_]+\]', line)
            if raid_status:
                raid_status = raid_status.group(0)
                data[device]['failed_disks'] = raid_status.count('_')
                if '_' in raid_status:
                    data[device]['raid_status'] = 'unclean'
            if 'blocks' in line:
                df_output = subprocess.check_output(['df', '/dev/' + device]).decode('utf-8').split('\n')[1].split()
                data[device]['used_space'] = round(int(df_output[2]) / int(df_output[1]) * 100, 2)
            if 'check =' in line:
                data[device]['resync_status'] = float(re.search(r'\d+.\d+', line).group(0))
                speed = re.search(r'speed=\d+K/sec', line)
                if speed:
                    data[device]['resync_speed'] = round(int(speed.group(0).split('=')[1].split('K')[0]) / 1024, 2)
                data[device]['raid_status'] = 'checking'
    return data

@app.route('/raid_status/<string:volume_name>', methods=['GET'])
def get_raid_info(volume_name):
    data = parse_mdstat()
    if volume_name in data:
        return jsonify({
            'state': data[volume_name]['raid_status'],
            'attributes': data[volume_name]
        })
    else:
        return jsonify({'error': 'RAID configuration not found'}), 404

@app.route('/raid_status', methods=['GET'])
def get_all_raids():
    data = parse_mdstat()
    return jsonify(data)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'raid_endpoint.conf')
    config.read(config_path)
    host = config.get('DEFAULT', 'HOST')
    port = config.getint('DEFAULT', 'PORT')
    use_https = config.getboolean('DEFAULT', 'USE_HTTPS')
    certificate_path = config.get('DEFAULT', 'CERTIFICATE_PATH')
    key_path = config.get('DEFAULT', 'KEY_PATH')

    if use_https:
        if os.path.exists(certificate_path) and os.path.exists(key_path):
            app.run(host=host, port=port, ssl_context=(certificate_path, key_path))
        else:
            app.run(host=host, port=port)
    else:
        app.run(host=host, port=port)
