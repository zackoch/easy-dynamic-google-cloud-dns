import json

import requests
from dns import resolver
from google.oauth2 import service_account
from googleapiclient import discovery

with open('config_sample.json') as config_file:
    config = json.load(config_file)

api_version = config['api_version']
gcp_project = config['gcp_project']
service_account_path = config['service_account_path']
ip_api = config['ip_api']
dns_data = config['dns_data']
nameserver = config['nameserver']


def get_public_ip(ip_api_url):
    try:
        public_ip = requests.get(ip_api_url)
        public_ip.raise_for_status()
        public_ip = public_ip.text
        return str(public_ip)

    except Exception as e:
        raise SystemExit(e)


def get_record_ip(fqdn):
    try:
        res = resolver.Resolver()
        res.nameservers = [config['nameserver']]
        check = res.resolve(fqdn)
        return str(check.rrset[0])
    except Exception as e:
        raise SystemExit(e)


def update_record(project, zone, svc_account, api_endpoint, dns_fqdn, dns_type, dns_ttl, dns_ip_addr, old_dns_ip_addr):
    try:
        credentials = service_account.Credentials.from_service_account_file(svc_account)
        service = discovery.build('dns', api_endpoint, credentials=credentials)
        payload = {
            "additions": [
                {
                    "name": f"{dns_fqdn + '.'}",
                    "type": f"{dns_type}",
                    "ttl": dns_ttl,
                    "rrdatas": [
                        f"{dns_ip_addr}"
                    ]
                }
            ],
            "deletions": [
                {
                    "name": f"{dns_fqdn + '.'}",
                    "type": f"{dns_type}",
                    "ttl": dns_ttl,
                    "rrdatas": [
                        f"{old_dns_ip_addr}"
                    ]
                }
            ]
        }
        request = service.changes().create(project=project, managedZone=zone, body=payload)
        response = request.execute()

        if response['status'] == 'pending':
            return True
        else:
            return False
    except Exception as e:
        raise SystemExit(e)


if __name__ == '__main__':
    pub_ip = get_public_ip(ip_api)

    for record in dns_data:
        dns_ip = get_record_ip(record['name'])
        if dns_ip != pub_ip:
            update_record(gcp_project, record['zone'], service_account_path, api_version, record['name'],
                          record['type'], record['ttl'], pub_ip, dns_ip)
        else:
            print('already good!')
            continue
