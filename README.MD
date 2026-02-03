# Lab 4 Chat App

Christopher Davisson  
CSCD 534 - Advanced Network Security  
Lab 4

## What is this

A P2P chat application with DHE and RSA key exchange. Can work locally (pure P2P) or through a relay server for clients behind NAT.

## Requirements

- Python 3.10+
- No external dependencies (just standard library)

## How to run

### Client (GUI)

```bash
python -m control client
```

Or just:

```bash
python -m control
```

### Server (Relay)

```bash
python -m control server -p 1234
```

Replace 1234 with whatever port you want.

### Quick test

```bash
make all
```

This starts a server and two clients.

## Usage

### Local P2P (same network)

1. Open two clients
2. On Client A: set your port, click "Listen"
3. On Client B: enter Client A's IP and port, click "Connect"
4. Chat

### Via Relay Server

1. Start the server somewhere reachable
2. On both clients: enter relay host/port, click "Relay"
3. Register with a name
4. Request list of users
5. Click on a user to start chatting

### Key Exchange

Once connected (either way):

- Click "DHE" to do Diffie-Hellman key exchange
- Click "RSA" to do RSA key transport
- Dropdown next to DHE lets you pick bit size (32, 64, 2048)
- 32 and 64 are for demo only, use 2048 for real

Shared secret shows up in the "Shared Keys" panel.

## File Structure

```
├── Makefile
├── README.MD
├── __init__.py
├── chat
│   ├── __init__.py
│   ├── chat.py
│   ├── crypto.py
│   ├── gui.py
│   └── names.txt
├── control.py
├── pyproject.toml
├── server
│   ├── __init__.py
│   └── server.py
└── white_paper.pdf

## Known Issues

- Changing your name after registering breaks things on the server
- If someone tries to chat with you while you're already in a chat, it boots you from the first one
- Messages are plaintext (by design, per assignment)

## License

[MIT License](https://mit-license.org/)

Copyright (c) 2025 Christopher Davisson