import json
import requests


def request(url, _params, _headers):
    response = requests.get(url, params=_params, headers=_headers)
    json_res = json.loads(response.text)

    return json_res

def requestPOST(url, _body, _headers):
    response = requests.post(url, json=_body, headers=_headers)
    json_res = json.loads(response.text)

    return json_res