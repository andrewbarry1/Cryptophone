# Cryptophone

My attempt at an encrypted chat program in python(3) using libsodium.

## How to run

Client requirements
```
- PyNaCl
- requests
- PyQt5
```

Server requirements
```
- flask
- psycopg2
```

Once the server is running (`./run.sh`), start the client (`./run.sh [clear]` for the debug client, `python3 qtclient.py` for the GUI).

## WARNING
Do not use this for serious purposes

I am not an expert and I cannot in good faith claim that this program is 100% secure. Please use an alternative if you require security.
