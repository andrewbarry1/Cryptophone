import nacl.utils
import nacl.pwhash
import getpass, os, json, base64, time
import network # network protocol lives here
from crypto import CryptoBox, check_pw # most crypto functions live here


def needs_first_run():
    return not(os.path.isfile('id.txt'))

def first_run(user_pw):
    pw_hash = nacl.pwhash.str(user_pw)
    dev_id = base64.b64encode(nacl.utils.random(64))

    hashfile = open('pw.txt', 'wb')
    hashfile.write(pw_hash)
    hashfile.close()

    init_Crypto, pubkey = CryptoBox.new(user_pw)
    
    init_Crypto.write_enc('id.txt', dev_id, astext=False)
    msg_salt = base64.b64encode(nacl.utils.random(64)).decode('utf-8')
    init_Crypto.write_enc('messages.txt', '{"messages":{},"salt":"' + msg_salt + '"}')
    msg_salt = base64.b64encode(nacl.utils.random(64)).decode('utf-8')
    init_Crypto.write_enc('contacts.txt', '{"contacts":{},"salt":"' + msg_salt + '"}')

    phone_number = network.register_key(dev_id, pubkey)
    init_Crypto.write_enc('identity.txt', phone_number)
    return str(phone_number)


def check_password(pw):
    return check_pw(prep_pass(pw))
def prep_pass(pw):
    return pw.strip().ljust(32).encode('utf-8')


def get_threaded_conversation(Crypto, dev_id, pn, from_u):
    from_pn = Crypto.contact_lookup(from_u)
            
    pubkey = network.get_key(from_pn)

    local_msgs_txt = Crypto.decrypt_local('messages.txt')
            
    all_disk_msgs = json.loads(local_msgs_txt)
    disk_msgs = all_disk_msgs['messages']
    if from_pn in disk_msgs:
        disk_msgs = disk_msgs[from_pn]
    else:
        disk_msgs = []
                
    net_msgs = network.get_messages(dev_id, pn, from_pn)
    if net_msgs is None or pubkey is None:
        net_msgs = []
    all_msgs = disk_msgs + net_msgs
    all_disk_msgs['messages'][from_pn] = all_msgs
    Crypto.write_enc('messages.txt', json.dumps(all_disk_msgs))
    
    all_msgs_dec = Crypto.decrypt_msgs(all_msgs, pubkey)
    # sort by timestamp
    for i in range(len(all_msgs_dec)):
        j = i
        while (all_msgs_dec[j-1][0] > all_msgs_dec[j][0] and j > 0):
            swap = all_msgs_dec[j-1]
            all_msgs_dec[j-1] = all_msgs_dec[j]
            all_msgs_dec[j] = swap
            j -= 1
    return all_msgs_dec


def send_message(Crypto, dev_id, pn, to_u, contents):
    to_pn = Crypto.contact_lookup(to_u)
    pubkey = network.get_key(to_pn)

    sent_msg = [int(time.time()), 0, contents]
    all_disk_msgs = json.loads(Crypto.decrypt_local('messages.txt'))
    if to_pn in all_disk_msgs['messages']:
        all_disk_msgs['messages'][to_pn].append(sent_msg)
    else:
        all_disk_msgs['messages'][to_pn] = [sent_msg]
    Crypto.write_enc('messages.txt', json.dumps(all_disk_msgs))
    
    if pubkey is None:
        return None
    enc_msg = Crypto.enc_message(pubkey, contents)
    network.send_message(dev_id, to_pn, pn, enc_msg)


def add_contact(Crypto, name, contact_pn):
    contacts_file = json.loads(Crypto.decrypt_local('contacts.txt'))
    contacts_file['contacts'][name.strip()] = contact_pn.strip()
    Crypto.write_enc('contacts.txt', json.dumps(contacts_file))


def change_local_pw(Crypto, new_pw):
    pw_hash = nacl.pwhash.str(new_pw)
    
    hashfile = open('pw.txt', 'wb')
    hashfile.write(pw_hash)
    hashfile.close()
    
    new_Crypto, trash = CryptoBox.new(new_pw, genkeys=False) # create dummy crypto object
    id_txt = Crypto.decrypt_local('id.txt', astext=False)
    new_Crypto.write_enc('id.txt', id_txt, astext=False)
    
    akey_txt = Crypto.decrypt_local('akey.txt', astext=False)
    new_Crypto.write_enc('akey.txt', akey_txt, astext=False)
    
    messages_txt = Crypto.decrypt_local('messages.txt')
    contacts_txt = Crypto.decrypt_local('contacts.txt')
    identity_txt = Crypto.decrypt_local('identity.txt')
    new_Crypto.write_enc('messages.txt', messages_txt)
    new_Crypto.write_enc('contacts.txt', contacts_txt)
    new_Crypto.write_enc('identity.txt', identity_txt)
    Crypto.skbox = new_Crypto.skbox


def regen_keys(Crypto, pn, dev_id):
    newkeys = nacl.public.PrivateKey.generate()
    Crypto.write_enc('akey.txt', newkeys.__bytes__() , astext=False)
    network.new_key(pn, dev_id, newkeys.public_key)
    Crypto.privkey = newkeys
    # messages are now garbage, wipe them
    msg_salt = base64.b64encode(nacl.utils.random(64)).decode('utf-8')
    Crypto.write_enc('messages.txt', '{"messages":{},"salt":"' + msg_salt + '"}')



def gen_crypto(pw):
    Crypto = CryptoBox(pw)
    dev_id = Crypto.decrypt_local('id.txt')
    pn = Crypto.decrypt_local('identity.txt')
    return CryptoContainer(Crypto, dev_id, pn)


def get_conversation_list(Crypto):
    all_disk_msgs = json.loads(Crypto.decrypt_local('messages.txt'))
    keys = [k for k in all_disk_msgs['messages']]
    return keys



class CryptoContainer:
    def __init__(self, Crypto, dev_id, pn):
        self.Crypto = Crypto
        self.dev_id = dev_id
        self.pn = pn
