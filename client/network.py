import requests, json, base64
from nacl.public import PublicKey

def network_error():
    raise Exception('The server returned an error or timed out.')

SERVER_URL = 'http://localhost:5000'
def url(path):
    return SERVER_URL + '/' + path


# initial key registration with the server
# return new phone number
def register_key(dev_id, pubkey):
    b64_pubkey = base64.b64encode(pubkey.__bytes__())
    try:
        r = requests.post(url('regkey'), {'dev_id': dev_id, 'pubkey': b64_pubkey})
        if r.status_code == 200:
            return r.text
        else:
            return None
    except:
        network_error()

        
# get messages from pn, identifying with dev_id
# return json message response
def get_messages(dev_id, to_pn, from_pn):
    try:
        r = requests.get(url('getmsg'), {'dev_id': dev_id, 'from_pn': from_pn, 'to_pn': to_pn})
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return None
    except:
        network_error()

        
# get the public key for this pn
def get_key(pn):
    try:
        r = requests.get(url('getkey'), {'pn': pn})
        if r.status_code == 200:
            pubkey = PublicKey(base64.b64decode(r.text))
            return pubkey
        else:
            return None
    except:
        network_error()
        

def send_message(dev_id, to_pn, from_pn, enc_msg):
    b64_enc_msg = base64.b64encode(enc_msg).decode('utf-8')
    try:
        r = requests.post(url('sendmsg'), {'dev_id': dev_id, 'to_pn': to_pn, 'from_pn': from_pn, 'msg': b64_enc_msg})
    except:
        network_error()
    return True


def new_key(pn, dev_id, pubkey):
    b64_pubkey = base64.b64encode(pubkey.__bytes__())
    try:
        r = requests.post(url('newkey'), {'dev_id': dev_id, 'pn': pn, 'pubkey': b64_pubkey})
    except:
        network_error()
    return True
