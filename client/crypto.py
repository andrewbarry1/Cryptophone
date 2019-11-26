import json
import nacl.public, nacl.secret, nacl.pwhash
from base64 import b64decode

# Read/Write encrypted data to filesystem, maintain asymmetric keys
class CryptoBox:

    @staticmethod
    def new(user_pw, genkeys=True):
        skbox = nacl.secret.SecretBox(user_pw)
        privkey = nacl.public.PrivateKey.generate()

        if genkeys:
            skbox = nacl.secret.SecretBox(user_pw)
            privkey_cypher = skbox.encrypt(privkey.__bytes__())
            akey_f = open('akey.txt', 'wb')
            akey_f.write(privkey_cypher)
            akey_f.close()
        
        return CryptoBox(user_pw, load_privkey=False), privkey.public_key
        
    
    def __init__(self, usr_pw, load_privkey=True):
        self.skbox = nacl.secret.SecretBox(usr_pw)
        if load_privkey:
            self.privkey = nacl.public.PrivateKey(self.decrypt_local('akey.txt', astext=False))

    def decrypt_local(self, path, astext=True):
        f = open(path, 'rb')
        enc = f.read()
        f.close()
        dec = self.skbox.decrypt(enc)
        if astext:
            return dec.decode('utf-8')
        else:
            return dec

    def write_enc(self, path, text, astext=True):
        f = open(path, 'wb')
        if astext:
            enc = self.skbox.encrypt(text.encode('utf-8'))
        else:
            enc = self.skbox.encrypt(text)
        f.write(enc)
        f.close()

    def enc_message(self, pubkey, msg):
        box = nacl.public.Box(self.privkey, pubkey)
        enc_msg = box.encrypt(msg.encode())
        return enc_msg
    
    def decrypt_msgs(self, msgs, pubkey):
        dec_box = nacl.public.Box(self.privkey, pubkey)
        dec_msgs = []
        for msg in msgs:
            if len(msg) == 2: # net message - it's encrypted
                b64_decode = b64decode(msg[1])
                dec_msgs.append([msg[0],1,dec_box.decrypt(b64_decode).decode('utf-8')])
            elif msg[1] == 1: # encrypted disk message
                b64_decode = b64decode(msg[2])
                dec_msgs.append([msg[0],1,dec_box.decrypt(b64_decode).decode('utf-8')])
            else: # unencrypted disk message ("sent" not "received")
                dec_msgs.append(msg)
        return dec_msgs


    def load_contacts(self):
        struct = json.loads(self.decrypt_local('contacts.txt'))
        return struct['contacts']


    def contact_lookup(self, name):
        contacts = self.load_contacts()
        if name in contacts:
            return contacts[name]
        return name
