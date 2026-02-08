import socket
import threading
import random
import tkinter as tk
from chat.gui import gui
from chat.crypto import Cryptography
import hashlib
import json
import secrets


class App:
    def __init__(self, root):
        self.root = root
        self.gui = gui(self.root)
        self.port = random.randint(10000, 65535)
        self.running = False
        self.messages = {}

        self.crypto = None
        self.status = False
        self.dhe_private = None
        self.dhe_p = None
        self.sock = None
        self.conn = None
        self.shared_secret = None
        self.rsa_private = None
        self.chat_partner = None 
        self.keys = (
            {}
        )  

        self.gui.connect = self.connect
        self.gui.listen = self.listen
        self.gui.cancel_listen = self.cancel_listen
        self.gui.disconnect = self.disconnect
        self.gui.crypto_change = self.crypto_change
        self.gui.register = self.register
        self.gui.close = self.close
        self.gui.DHE = self.DHE
        self.gui.RSA = self.RSA
        self.gui.send_message = self.send_message
        self.gui.set_port = self.set_port
        self.gui.connect_relay = self.connect_relay
        self.gui.list_users = self.list_users
        self.gui.request_chat = self.request_chat
        self.gui.show_key = self.show_key
        self.gui.my_port_entry.insert(0, str(self.port))

    def _cleanup_connection(self):
        self.running = False
        self.chat_partner = None
        for sock in [self.conn, self.sock]:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
        self.conn = None
        self.sock = None

    def listen(self, timeout=30):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(1)
        self.gui.log(f"Listening on port: {self.port}")
        self.gui.set_cancel_mode()

        def accept():
            try:
                self.conn, addr = self.sock.accept()
                self.running = True
                self.root.after(0, lambda: self.gui.log(f"Connection from {addr}"))
                self.root.after(0, lambda: self.gui.set_status(True))
                self.status = True
                self.root.after(0, lambda: self.gui.set_disconnect_mode())
                self.receive_loop()
            except socket.timeout:
                if self.sock:
                    try:
                        self.sock.close()
                    except Exception:
                        pass
                    self.sock = None
                self.root.after(0, lambda: self.gui.log("Listen timed out"))
                self.root.after(0, lambda: self.gui.set_listen_mode())
            except OSError as e:
                if self.sock:
                    try:
                        self.sock.close()
                    except Exception:
                        pass
                    self.sock = None
                self.root.after(0, lambda err=e: self.gui.log(f"Listen error: {err}"))
                self.root.after(0, lambda: self.gui.set_listen_mode())

        threading.Thread(target=accept, daemon=True).start()

    def connect(self):
        host = self.gui.host_entry.get()
        port = int(self.gui.port_entry.get())

        def do_connect():
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.connect((host, port))
                self.running = True
                self.root.after(0, lambda: self.gui.log(f"Connected to {host}:{port}"))
                self.root.after(0, lambda: self.gui.set_status(True))
                self.status = True
                self.root.after(0, lambda: self.gui.set_disconnect_mode())
                self.receive_loop()
            except Exception as e:
                if self.conn:
                    try:
                        self.conn.close()
                    except Exception:
                        pass
                    self.conn = None
                self.root.after(0, lambda: self.gui.log(f"Connection failed: {e}"))

        threading.Thread(target=do_connect, daemon=True).start()

    def connect_relay(self):
        host = self.gui.relay_host_entry.get()
        port_str = self.gui.relay_port_entry.get()
        if not host or not port_str:
            self.gui.log("Enter relay host and port")
            return
        port = int(port_str)
        name = self.gui.name_entry.get().strip()
        if not name:
            self.gui.log("Enter a name before connecting to relay")
            return

        def do_connect():
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.connect((host, port))
                self.running = True
                self.root.after(0, lambda: self.gui.log(f"Connected to relay {host}:{port}"))

                # Send REGISTER
                register_msg = f"REGISTER {name}\n"
                self.conn.send(register_msg.encode("utf-8"))
                self.root.after(0, lambda: self.gui.log(f"Sent REGISTER as '{name}'"))

                self.root.after(0, lambda: self.gui.set_status(True))
                self.status = True
                self.root.after(0, lambda: self.gui.set_disconnect_mode())
                self.receive_loop()
            except Exception as e:
                if self.conn:
                    try:
                        self.conn.close()
                    except Exception:
                        pass
                    self.conn = None
                self.root.after(0, lambda: self.gui.log(f"Relay connection failed: {e}"))

        threading.Thread(target=do_connect, daemon=True).start()

    def list_users(self):
        if not self.conn or not self.status:
            self.gui.log("Not connected to server")
            return
        self.conn.send(b"LIST\n")

    def request_chat(self):
        if not self.conn or not self.status:
            self.gui.log("Not connected to server")
            return
        target = self.gui.users_combo.get()
        if not target:
            self.gui.log("Select a user to chat with")
            return
        self.conn.send(f"CHAT_REQUEST {target}\n".encode("utf-8"))
        self.gui.log(f"Requesting chat with {target}...")

    def _process_message(self, msg):
        if msg.startswith("CRYPTO:"):
            crypto_msg = json.loads(msg[7:])
            self.handle_protocol_msg(crypto_msg)
        elif msg == "REGISTERED":
            self.root.after(0, lambda: self.gui.log("Registered with server"))
        elif msg.startswith("ERROR "):
            error_msg = msg[6:]
            self.root.after(0, lambda m=error_msg: self.gui.log(f"Server error: {m}"))
        elif msg.startswith("USERS "):
            users_str = msg[6:]
            users = [u.strip() for u in users_str.split(",") if u.strip()]
            self.root.after(0, lambda u=users: self.gui.update_users(u))
            self.root.after(
                0, lambda u=users: self.gui.log(f"Online users: {', '.join(u)}")
            )
        elif msg.startswith("CHAT_STARTED "):
            partner = msg[13:].strip()
            self.chat_partner = partner
            self.root.after(0, lambda p=partner: self.gui.log(f"Chat started with {p}"))
        elif msg == "CHAT_ENDED":
            partner = self.chat_partner
            self.chat_partner = None
            self.root.after(0, lambda p=partner: self.gui.log(f"Chat ended with {p}"))
            self.root.after(0, lambda: self.gui.set_listen_mode())
        else:
            if self.chat_partner:
                self.root.after(
                    0, lambda m=msg, p=self.chat_partner: self.gui.log(f"{p}: {m}")
                )
            else:
                self.root.after(0, lambda m=msg: self.gui.log(f"Friend: {m}"))

    def receive_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    msg = msg.strip()
                    if msg:
                        self._process_message(msg)

                if buffer and "\n" not in buffer:
                    stripped = buffer.strip()
                    if stripped:
                        self._process_message(stripped)
                        buffer = ""

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                break
            except OSError as e:
                self.root.after(0, lambda err=e: self.gui.log(f"Connection error: {err}"))
                break
            except Exception as e:
                self.root.after(0, lambda err=e: self.gui.log(f"Receive error: {err}"))
                break
        self.running = False
        self.chat_partner = None
        self.root.after(0, lambda: self.gui.log("Disconnected"))
        self.root.after(0, lambda: self.gui.set_status(False))
        self.status = False
        self.root.after(0, lambda: self.gui.set_listen_mode())

    def send_message(self):
        msg = self.gui.msg_entry.get()
        if msg and self.conn:
            try:
                self.conn.send(msg.encode("utf-8"))
                name = self.gui.name_entry.get() or "Me"
                self.gui.log(f"{name}: {msg}")
                self.gui.msg_entry.delete(0, tk.END)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                self.gui.log(f"Send failed: {e}")
                self._cleanup_connection()
                self.gui.set_status(False)
                self.status = False
                self.gui.set_listen_mode()

    def cancel_listen(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.gui.log("Listen cancelled")
        self.gui.set_listen_mode()

    def disconnect(self):
        if self.chat_partner and self.conn:
            try:
                self.conn.send(b"END_CHAT\n")
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                pass
            self.gui.log(f"Ending chat with {self.chat_partner}...")
        else:
            self._cleanup_connection()
            self.gui.log("Disconnected")
            self.gui.set_status(False)
            self.status = False
            self.gui.set_listen_mode()

    def set_port(self):
        try:
            new_port = int(self.gui.my_port_entry.get())
            if 1 <= new_port <= 65535:
                self.port = new_port
                self.gui.log(f"Port set to {self.port}")
            else:
                self.gui.log("Port must be between 1 and 65535")
        except ValueError:
            self.gui.log("Invalid port number")

    def cleanup(self):
        self.running = False
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()

    def run(self):
        self.root.mainloop()

    def crypto_change(self):
        print("")

    def register(self):
        print("")

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()
        self.root.destroy()

    # Perform the DHE key exchange
    def DHE(self):
        if not self.status:
            self.gui.log("Not Connected")
            return

        self.gui.log("Begining DHE key exchange...")

        bits = int(self.gui.dhe_size.get())
        self.dhe_p, g = Cryptography.get_dh_params(bits)
        # self.dhe_p = Cryptography.DH_PRIME
        # g = Cryptography.DH_GENERATOR

        self.dhe_private = Cryptography.generate_DHE_key(self.dhe_p)

        A = Cryptography.compute_public_key(g, self.dhe_private, self.dhe_p)

        self.gui.log(f"a = {self.dhe_private}")
        self.gui.log("\n")

        msg = json.dumps({"type": "DHE_INIT", "p": str(self.dhe_p), "g": g, "A": str(A)})

        self.conn.send(f"CRYPTO:{msg}".encode("utf-8"))
        self.gui.log(f"send DHE init. Waiting for response")
        self.gui.log("\n")

    def handle_protocol_msg(self, msg):
        # ==================== DHE =======================
        if msg["type"] == "DHE_INIT":
            p = int(msg["p"])
            g = msg["g"]
            A = int(msg["A"])

            b = Cryptography.generate_DHE_key(p)
            B = Cryptography.compute_public_key(g, b, p)

            # Compute Shared secret
            shared = Cryptography.compute_shared_secret(A, b, p)
            # If AES then hash
            self.shared_secret = hashlib.sha256(shared.to_bytes(256, "big")).digest()

            partner = self.chat_partner or "Peer"
            self.keys[partner] = {"method": "DHE", "shared": self.shared_secret.hex()}
            self.root.after(0, lambda p=partner: self.gui.add_key(p, "DHE"))

            reply = json.dumps({"type": "DHE_REPLY", "B": str(B)})
            self.conn.send(f"CRYPTO:{reply}".encode("utf-8"))
            self.root.after(0, lambda: self.gui.log("DHE complete (responder)"))
        elif msg["type"] == "DHE_REPLY":
            B = int(msg["B"])
            shared = Cryptography.compute_shared_secret(B, self.dhe_private, self.dhe_p)
            self.shared_secret = hashlib.sha256(shared.to_bytes(256, "big")).digest()

            partner = self.chat_partner or "Peer"
            self.keys[partner] = {"method": "DHE", "shared": self.shared_secret.hex()}
            self.root.after(0, lambda p=partner: self.gui.add_key(p, "DHE"))
            self.root.after(0, lambda: self.gui.log("DHE complete (initiator)"))

        #  ==================== RSA =======================
        elif msg["type"] == "RSA_PUBKEY":
            n, e = int(msg["n"]), msg["e"]
            secret = secrets.randbelow(n - 1)
            c = pow(secret, e, n)
            reply = f"CRYPTO:{json.dumps({'type': 'RSA_SECRET', 'c': str(c)})}"
            self.conn.send(reply.encode())
            self.shared_secret = hashlib.sha256(secret.to_bytes(256, "big")).digest()
            partner = self.chat_partner or "Peer"
            self.keys[partner] = {"method": "RSA", "shared": self.shared_secret.hex()}
            self.root.after(0, lambda p=partner: self.gui.add_key(p, "RSA"))
            self.root.after(0, lambda: self.gui.log("RSA complete (responder)"))
        elif msg["type"] == "RSA_SECRET":
            c = int(msg["c"])
            n, d = self.rsa_private
            secret = pow(c, d, n)
            self.shared_secret = hashlib.sha256(secret.to_bytes(256, "big")).digest()
            partner = self.chat_partner or "Peer"
            self.keys[partner] = {"method": "RSA", "shared": self.shared_secret.hex()}
            self.root.after(0, lambda p=partner: self.gui.add_key(p, "RSA"))
            self.root.after(0, lambda: self.gui.log("RSA complete (initiator)"))

    def RSA(self):
        if not self.status:
            self.gui.log("Not Connected")
            return

        self.gui.log("Beginning RSA key exchange...")

        public, private = Cryptography.generate_rsa_keypair(bits=1024)
        self.rsa_private = private

        msg = f"CRYPTO:{json.dumps({'type': 'RSA_PUBKEY', 'n': str(public[0]), 'e': public[1]})}"
        self.conn.send(msg.encode())
        self.gui.log("Sent RSA public key. Waiting for response...")

    def show_key(self, entry):
        if " (" in entry and entry.endswith(")"):
            partner = entry.rsplit(" (", 1)[0]
            if partner in self.keys:
                key_info = self.keys[partner]
                self.gui.log(f"Key for {partner} ({key_info['method']}):")
                self.gui.log(f"  shared = {key_info['shared']}")

    def add_to_chat(self, text, sender=None, encryption=None, debug=False):
        line = ""
        if sender:
            line += f"[{sender}] "
        if encryption:
            line += f"({encryption}) "
        if debug:
            line += "[DEBUG] "
        line += text + "\n"

        self.gui.chat_display.config(state=tk.NORMAL)
        self.gui.chat_display.insert(tk.END, line)
        self.gui.chat_display.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
