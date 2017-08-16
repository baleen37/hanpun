import base64
import hashlib
import hmac
import json

import requests

PROTOCOL = 'https'
HOST = 'api.bitfinex.com'


class Client:
    def __init__(self, key, secret):
        self.URL = f'{PROTOCOL}://{HOST}/'
        self.KEY = key
        self.SECRET = secret

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.SECRET.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": self.KEY,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }
