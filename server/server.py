from flask import Flask, request, Response
import psycopg2
import nacl.pwhash
import db

app = Flask(__name__)
conn = psycopg2.connect('dbname=cryptophone user=cryptophone')
cur = conn.cursor()


def error():
    return Response('', status=400)
def empty():
    return Response('', status=200)

# take dev_id and b64_pubkey
@app.route('/regkey', methods=['POST'])
def regkey():
    if 'dev_id' not in request.form or 'pubkey' not in request.form:
        return error()
    dev_id = request.form['dev_id']
    pubkey = request.form['pubkey']
    pn = db.create_user(cur, dev_id, pubkey)
    conn.commit()
    return pn


# take dev_id and from_pn
@app.route('/getmsg', methods=['GET'])
def getmsg():
    if 'dev_id' not in request.args or 'from_pn' not in request.args or 'to_pn' not in request.args:
        return error()
    
    to_id = db.get_id(cur, request.args.get('to_pn'), request.args.get('dev_id'))
    from_id = db.get_id(cur, request.args.get('from_pn'))
    msgs = db.get_msgs(cur, to_id, from_id)
    conn.commit()
    
    return msgs


# take pn
@app.route('/getkey', methods=['GET'])
def getkey():
    pn = request.args.get('pn')
    if pn is None:
        return error()
    id = db.get_id(cur, pn=pn)
    if id is None:
        return error()
    return db.get_pubkey(cur, id)


# take from dev_id, to_pn, and msg
@app.route('/sendmsg', methods=['POST'])
def sendmsg():
    if 'dev_id' not in request.form or 'to_pn' not in request.form or 'msg' not in request.form or 'from_pn' not in request.form:
        return error()
    
    dev_id = request.form['dev_id']
    to_pn = request.form['to_pn']
    msg = request.form['msg']
    from_pn = request.form['from_pn']
    from_id = db.get_id(cur, from_pn, dev_id)
    to_id = db.get_id(cur, to_pn)
    if from_id is None or to_id is None:
        return error()
    db.save_msg(cur, from_id, to_id, msg)
    conn.commit()
    return empty()

@app.route('/newkey', methods=['POST'])
def newkey():
    if 'dev_id' not in request.form or 'pn' not in request.form or 'pubkey' not in request.form:
        return error()

    dev_id = request.form['dev_id']
    pn = request.form['pn']
    b64_pubkey = request.form['pubkey']

    u_id = db.get_id(cur, pn, dev_id)
    if u_id is None:
        return error()
    db.replace_key(u_id, b64_pubkey)
    conn.commit()
    return empty()
