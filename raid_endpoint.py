from flask import Flask, jsonify
import subprocess
import re
import configparser
import os

app = Flask(__name__)

class RaidMonitor:
    def __init__(self):
        pass

    # Function to get the contents of /proc/mdstat
    def get_mdstat(self):
        return subprocess.check_output(['cat', '/proc/mdstat']).decode('utf-8').split('\n')

    # Function to get the output of the df command for a specific device
    def get_df_output(self, device):
        return subprocess.check_output(['df', '/dev/' + device]).decode('utf-8').split('\n')[1].split()

    # Function to parse the contents of /proc/mdstat and gather RAID info
    def parse_mdstat(self):
        mdstat = self.get_mdstat()
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
                self.update_device_data(device, line, data)
        return data

    # Function to update the data for a specific device based on a line of mdstat
    def update_device_data(self, device, line, data):
        raid_status = re.search(r'\[[U_]+\]', line)
        if raid_status:
            self.update_raid_status(device, raid_status.group(0), data)
        if 'blocks' in line:
            df_output = self.get_df_output(device)
            data[device]['used_space'] = round(int(df_output[2]) / int(df_output[1]) * 100, 2)
        if 'check =' in line:
            self.update_resync_status(device, line, data)

    # Function to update the RAID status for a device
    def update_raid_status(self, device, raid_status, data):
        data[device]['failed_disks'] = raid_status.count('_')
        if '_' in raid_status:
            data[device]['raid_status'] = 'unclean'

    # Function to update the resync status for a device
    def update_resync_status(self, device, line, data):
        data[device]['resync_status'] = float(re.search(r'\d+.\d+', line).group(0))
        speed = re.search(r'speed=\d+K/sec', line)
        if speed:
            data[device]['resync_speed'] = round(int(speed.group(0).split('=')[1].split('K')[0]) / 1024, 2)
        data[device]['raid_status'] = 'checking'

class AppRunner:
    def __init__(self):
        self.config = self.read_config()

    def read_config(self):
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(dir_path, 'raid_endpoint.conf')
        config.read(config_path)
        return config

    def run_app(self):
        host = self.config.get('DEFAULT', 'HOST')
        port = self.config.getint('DEFAULT', 'PORT')
        use_https = self.config.getboolean('DEFAULT', 'USE_HTTPS')
        certificate_path = self.config.get('DEFAULT', 'CERTIFICATE_PATH')
        key_path = self.config.get('DEFAULT', 'KEY_PATH')

        if use_https:
            if os.path.exists(certificate_path) and os.path.exists(key_path):
                app.run(host=host, port=port, ssl_context=(certificate_path, key_path))
            else:
                app.run(host=host, port=port)
        else:
            app.run(host=host, port=port)

raid_monitor = RaidMonitor()
app_runner = AppRunner()

@app.route('/raid_status/<string:volume_name>', methods=['GET'])
def get_raid_info(volume_name):
    data = raid_monitor.parse_mdstat()
    if volume_name in data:
        return jsonify({
            'state': data[volume_name]['raid_status'],
            'attributes': data[volume_name]
        })
    else:
        return jsonify({'error': 'RAID configuration not found'}), 404

@app.route('/raid_status', methods=['GET'])
def get_all_raids():
    data = raid_monitor.parse_mdstat()
    return jsonify(data)

if __name__ == '__main__':
    app_runner.run_app()
