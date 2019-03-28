#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import hmac
import time
import random
import hashlib
import binascii
import requests

# @home2 https://setq.me/1024


class Client(object):
    def __init__(self, secret_id, secret_key, host, uri, **params):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.host = host
        self.uri = uri
        self.params = params
        if sys.version_info.major > 2:
            self.Py3 = True
            self.secret_key = bytes(self.secret_key, 'utf-8')
        else:
            self.Py3 = False

    def public_params(self):
        params = {
            'Nonce': random.randint(1, 9999),
            'SecretId': self.secret_id,
            'SignatureMethod': 'HmacSHA1',
            'Timestamp': int(time.time()),
        }
        params.update(self.params)

        return params

    def sign(self, params, method='GET'):
        params = params.copy()
        params.update(self.public_params())
        p = {}
        for k in params:
            if method == 'POST' and str(params[k])[0:1] == '@':
                continue
            p[k.replace('_', '.')] = params[k]
        ps = '&'.join('%s=%s' % (k, p[k]) for k in sorted(p))

        msg = '%s%s%s?%s' % (method.upper(), self.host, self.uri, ps)
        if self.Py3:
            msg = bytes(msg, 'utf-8')

        hashed = hmac.new(self.secret_key, msg, hashlib.sha1)
        base64 = binascii.b2a_base64(hashed.digest())[:-1]
        if self.Py3:
            base64 = base64.decode()

        params['Signature'] = base64

        return params

    def send(self, params, method='GET'):
        params = self.sign(params, method)
        req_host = 'https://{}{}'.format(self.host, self.uri)
        if method == 'GET':
            resp = requests.get(req_host, params=params)
        else:
            resp = requests.post(req_host, data=params)

        return resp.json()


# View details at https://cloud.tencent.com/document/product/302/4032
class Cns:
    def __init__(self, secret_id, secret_key):
        host, uri = 'cns.api.qcloud.com', '/v2/index.php'
        self.client = Client(secret_id, secret_key, host, uri)

    def list(self, domain):
        body = {
            'Action': 'RecordList',
            'domain': domain
        }

        return self.client.send(body)

    def create(self, domain, name, _type, value):
        body = {
            'Action': 'RecordCreate',
            'domain': domain,
            'subDomain': name,
            'recordType': _type,
            'recordLine': '默认',
            'value': value
        }

        return self.client.send(body)

    def delete(self, domain, _id):
        body = {
            'Action': 'RecordDelete',
            'domain': domain,
            'recordId': _id
        }

        return self.client.send(body)


def run(secret_id, secret_key):
    env = os.environ.copy()
    cns = Cns(secret_id, secret_key)
    option = sys.argv[1]  # add|del
    domain = env['CERTBOT_DOMAIN']
    name = '_acme-challenge'
    value = env['CERTBOT_VALIDATION']

    print(' - {} {} {} {}'.format(option, domain, name, value))

    if option == 'add':
        cns.create(domain, name, 'TXT', value)
        time.sleep(10)  # Waiting for record to take effect
    elif option == 'del':
        for record in cns.list(domain)['data']['records']:
            if record['name'] == name and record['value'] == value:
                cns.delete(domain, record['id'])


if __name__ == '__main__':
    # Create your secret_id and secret_key at https://console.cloud.tencent.com/cam/capi
    secret_id = 'your secret_id'
    secret_key = 'your secret_key'

    if len(sys.argv) > 1:
        run(secret_id, secret_key)
    else:
        print('using: qcloud-dns.py add|del')
        exit(1)
