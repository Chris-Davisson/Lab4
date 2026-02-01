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
        self.friends = {}
        self.friend_counter = 0
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
        self.gui.on_address_selected = self.on_address_selected
        self.gui.connect_relay = self.connect_relay
        self.gui.my_port_entry.insert(0, str(self.port))
        self.update_self_address()

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
                self.root.after(0, lambda: self.gui.log("Listen timed out"))
                self.root.after(0, lambda: self.gui.set_listen_mode())
            except OSError:
                pass

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
                self.root.after(0, lambda: self.save_address(host, port))
                self.receive_loop()
            except Exception as e:
                self.root.after(0, lambda: self.gui.log(f"Connection failed: {e}"))

        threading.Thread(target=do_connect, daemon=True).start()

    def connect_relay(self):
        host = self.gui.relay_host_entry.get()
        port_str = self.gui.relay_port_entry.get()
        if not host or not port_str:
            self.gui.log("Enter relay host and port")
            return
        port = int(port_str)

        def do_connect():
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.connect((host, port))
                self.running = True
                self.root.after(0, lambda: self.gui.log(f"Connected to relay {host}:{port}"))
                self.root.after(0, lambda: self.gui.set_status(True))
                self.status = True
                self.root.after(0, lambda: self.gui.set_disconnect_mode())
                self.receive_loop()
            except Exception as e:
                self.root.after(0, lambda: self.gui.log(f"Relay connection failed: {e}"))

        threading.Thread(target=do_connect, daemon=True).start()

    def save_address(self, ip, port):
        for name, (saved_ip, saved_port) in self.friends.items():
            if saved_ip == ip and saved_port == port:
                return
        self.friend_counter += 1
        name = f"Friend{self.friend_counter}"
        self.add_friend(name, ip, port)

    def receive_loop(self):
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                msg = data.decode("utf-8")

                if msg.startswith("CRYPTO:"):
                    crypto_msg = json.loads(msg[7:])
                    self.handle_protocol_msg(crypto_msg)
                else:
                  self.root.after(0, lambda m=msg: self.gui.log(f"Friend: {m}"))
            except:
                break
        self.running = False
        self.root.after(0, lambda: self.gui.log("Disconnected"))
        self.root.after(0, lambda: self.gui.set_status(False))
        self.status = False
        self.root.after(0, lambda: self.gui.set_listen_mode())

    def send_message(self):
        msg = self.gui.msg_entry.get()
        if msg and self.conn:
            self.conn.send(msg.encode("utf-8"))
            name = self.gui.name_entry.get() or "Me"
            self.gui.log(f"{name}: {msg}")
            self.gui.msg_entry.delete(0, tk.END)

    def cancel_listen(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.gui.log("Listen cancelled")
        self.gui.set_listen_mode()

    def disconnect(self):
        self.running = False
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.sock:
            self.sock.close()
            self.sock = None
        self.gui.log("Disconnected")
        self.gui.set_status(False)
        self.status = False
        self.gui.set_listen_mode()

    def set_port(self):
        try:
            new_port = int(self.gui.my_port_entry.get())
            if 1 <= new_port <= 65535:
                self.port = new_port
                self.update_self_address()
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

    #Perform the DHE key exchange
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

        A = Cryptography.compute_public_key( g, self.dhe_private, self.dhe_p)

        # Write private key to Shared Keys section
        self.gui.keys_display.config(state=tk.NORMAL)
        self.gui.keys_display.delete(1.0, tk.END)
        self.gui.keys_display.insert(tk.END, f"a = {hex(self.dhe_private)}\n")
        self.gui.keys_display.config(state=tk.DISABLED)

        self.gui.log(f"a = {self.dhe_private}")
        self.gui.log("\n")

        msg = json.dumps({
            "type": "DHE_INIT",
            "p": str(self.dhe_p),
            "g": g,
            "A": str(A)
        })

        self.conn.send(f"CRYPTO:{msg}".encode("utf-8"))
        self.gui.log(f"send DHE init. Waiting for response")
        self.gui.log("\n")

    def handle_protocol_msg(self, msg):
        #==================== DHE =======================
        if msg["type"] == "DHE_INIT":
            p = int(msg["p"])
            g = msg["g"]
            A = int(msg["A"])

            b = Cryptography.generate_DHE_key(p)
            B = Cryptography.compute_public_key(g, b, p)

            # Compute Shared secret
            shared = Cryptography.compute_shared_secret(A, b, p)
            # If AES then hash
            self.shared_secret = hashlib.sha256(shared.to_bytes(256, 'big')).digest()

            def update_keys():
                self.gui.keys_display.config(state=tk.NORMAL)
                self.gui.keys_display.delete(1.0, tk.END)
                self.gui.keys_display.insert(tk.END, f"b = {hex(b)}\n")
                self.gui.keys_display.insert(tk.END, f"shared = {self.shared_secret.hex()}\n")
                self.gui.keys_display.config(state=tk.DISABLED)
            self.root.after(0, update_keys)

            # Send reply with our public key
            reply = json.dumps({
                "type": "DHE_REPLY",
                "B": str(B)
            })
            self.conn.send(f"CRYPTO:{reply}".encode("utf-8"))
            self.root.after(0, lambda: self.gui.log("DHE complete (responder)"))
        elif msg["type"] == "DHE_REPLY":
            B = int(msg["B"])
            shared = Cryptography.compute_shared_secret(B, self.dhe_private, self.dhe_p)
            self.shared_secret = hashlib.sha256(shared.to_bytes(256, 'big')).digest()

            def update_keys():
                self.gui.keys_display.config(state=tk.NORMAL)
                self.gui.keys_display.delete(1.0, tk.END)
                self.gui.keys_display.insert(tk.END, f"a = {hex(self.dhe_private)}\n")
                self.gui.keys_display.insert(tk.END, f"shared = {self.shared_secret.hex()}\n")
                self.gui.keys_display.config(state=tk.DISABLED)
            self.root.after(0, update_keys)
            self.root.after(0, lambda: self.gui.log("DHE complete (initiator)"))
        

        #  ==================== RSA =======================
        elif msg["type"]=="RSA_PUBKEY":
            n, e = int(msg["n"]), msg["e"]
            secret = secrets.randbelow(n-1)
            c = pow(secret, e, n)
            reply = f"CRYPTO:{json.dumps({'type': 'RSA_SECRET', 'c': str(c)})}"
            self.conn.send(reply.encode())
            self.shared_secret = hashlib.sha256(secret.to_bytes(256, 'big')).digest()

            def update_keys():
                self.gui.keys_display.config(state=tk.NORMAL)
                self.gui.keys_display.delete(1.0, tk.END)
                self.gui.keys_display.insert(tk.END, f"shared = {self.shared_secret.hex()}\n")
                self.gui.keys_display.config(state=tk.DISABLED)
            self.root.after(0, update_keys)
            self.root.after(0, lambda: self.gui.log("RSA complete (responder)"))

        elif msg["type"] == "RSA_SECRET":
            c = int(msg["c"])
            n, d = self.rsa_private
            secret = pow(c, d, n)
            self.shared_secret = hashlib.sha256(secret.to_bytes(256, 'big')).digest()

            def update_keys():
                self.gui.keys_display.config(state=tk.NORMAL)
                self.gui.keys_display.delete(1.0, tk.END)
                self.gui.keys_display.insert(tk.END, f"shared = {self.shared_secret.hex()}\n")
                self.gui.keys_display.config(state=tk.DISABLED)
            self.root.after(0, update_keys)
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


    def update_self_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"

        self.friends["self"] = [local_ip, self.port]
        self.update_address_dropdown()

    def add_friend(self, name, ip, port):
        self.friends[name] = [ip, port]
        self.update_address_dropdown()

    def update_address_dropdown(self):
        names = list(self.friends.keys())
        self.gui.addr_combo["values"] = names
        if names and not self.gui.addr_combo.get():
            self.gui.addr_combo.set(names[0])

    def on_address_selected(self):
        name = self.gui.addr_combo.get()
        if name and name in self.friends:
            ip, port = self.friends[name]
            self.gui.host_entry.delete(0, tk.END)
            self.gui.host_entry.insert(0, ip)
            self.gui.port_entry.delete(0, tk.END)
            self.gui.port_entry.insert(0, str(port))

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
