import random, json
import nacl.pwhash
from base64 import b64encode, b64decode


def create_user(cur, dev_id, pubkey):
    pn = gen_pn(cur)
    dev_id_hash = nacl.pwhash.str(dev_id.encode('utf-8')).decode('utf-8')
    cur.execute('INSERT INTO phonebook (dev_id, pn, pubkey) VALUES (%s, %s, %s)', (dev_id_hash, pn, pubkey))
    return pn

def replace_key(u_id, pubkey):
    cur.execute('UPDATE phonebook SET pubkey = %s WHERE id = %s', (pubkey, u_id))
    cur.execute('DELETE FROM messages WHERE ito = %s', (u_id,)) # these messages are garbage now


def check_id(cur, pn, dev_id):
    return get_id(cur, pn, dev_id) is not None


def get_id(cur, pn, dev_id=None):
    cur.execute('SELECT id, dev_id FROM phonebook WHERE pn=%s', (pn,))
    res = cur.fetchone()
    if res is not None:
        if dev_id is not None:
            try:
                nacl.pwhash.verify(res[1].encode('utf-8'), dev_id.encode('utf-8'))
            except:
                return None
        return res[0]
    else:
        return None


def get_pubkey(cur, id):
    cur.execute('SELECT pubkey FROM phonebook WHERE id=%s', (id,))
    res = cur.fetchone()
    if res is not None:
        return res[0]
    else:
        return None


def save_msg(cur, from_id, to_id, msg):
    cur.execute('INSERT INTO messages (ifrom, ito, msg) VALUES (%s, %s, %s)', (from_id, to_id, msg))
    


def get_msgs(cur, to_id, from_id):
    if from_id is None or to_id is None: # invalid phone numbers, fake no messages
        return '[]'
    cur.execute('SELECT timestamp, msg FROM messages WHERE ifrom = %s AND ito = %s', (from_id, to_id))
    msgs = []
    try:
        all = cur.fetchall()
    except: # ProgrammingError no data to fetch
        return json.dumps(msgs)
    if all is None:
        return msgs
    for (ts, msg) in all:
        msgs.append([int(ts.timestamp()), msg])
        cur.execute('DELETE FROM messages WHERE ifrom = %s AND ito = %s', (from_id, to_id))
    return json.dumps(msgs)


# TODO this is not okay at scale
def gen_pn(cur):
    return format(random.randrange(0, 1000000000), '09')
