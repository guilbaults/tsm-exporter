import requests
import json
import argparse
import time
import ConfigParser

from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client import start_http_server


class IBM_API:
    def __init__(self, auth, control_center_url):
        self.auth = auth
        self.control_center_url = control_center_url

    def fix_ibm_api(self, hdr, items_json):
        headers = {}
        for header in hdr:
            headers[header['id']] = header['def']

        items = []
        for item in items_json:
            info = {}
            for key in item.keys():
                if key in headers:
                    info[headers[key]] = item[key]
            items.append(info)
        return items

    def query(self, q_string, server_name):
        r = requests.post('{}/oc/api/cli/issueCommand/{}'.format(
                          self.control_center_url, server_name),
                          data=q_string,
                          auth=self.auth,
                          verify=False,
                          headers={'OC-API-VERSION': '1.0',
                                   'content-type': 'text/plain'})

        j = json.loads(r.text)
        return self.fix_ibm_api(j[0][0]['hdr'], j[0][0]['items'])


class TSMCollector(object):
    def __init__(self, servers):
        self.servers = servers

    def collect(self):
        tape_drive_state = GaugeMetricFamily(
            'tsm_tape_drive_state', 'Tape drive status',
            labels=['server', 'drive'])
        tape_status = GaugeMetricFamily(
            'tsm_tape_status', 'Files count', labels=['server', 'status'])
        for server in self.servers:
            for drive in tsm.query('query drive format=detailed', server):
                if drive['Drive State'] == 'EMPTY':
                    drive_state = 0
                elif drive['Drive State'] == 'LOADED':
                    drive_state = 1
                else:
                    print(drive['Drive State'])
                    drive_state = -1
                tape_drive_state.add_metric([server, drive['Drive Name']],
                                            drive_state)

            libvolume = tsm.query('query libvolume', server)
            tapes_status = {}
            for tape in libvolume:
                if tape['Status']['def'] in tapes_status:
                    tapes_status[tape['Status']['def']] += 1
                else:
                    tapes_status[tape['Status']['def']] = 1

            for status in tapes_status.keys():
                tape_status.add_metric([server, status], tapes_status[status])

        yield tape_drive_state
        yield tape_status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prometheus collector for TSM stats')
    parser.add_argument("config", type=str, help="Config file path")
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.config)

    tsm = IBM_API(
        (config.get('tsm', 'username'), config.get('tsm', 'password')),
        config.get('tsm', 'url'))

    start_http_server(int(config.get('exporter', 'port')))
    REGISTRY.register(TSMCollector(config.get('tsm', 'servers').split(',')))
    while True:
        time.sleep(1)
