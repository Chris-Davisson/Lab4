import socket
import threading
import random
import tkinter as tk
from chat.gui import gui
from chat.crypto import Cryptography
import hashlib


class App:
    def __init__(self, root):
        self.root = root
        self.gui = gui(self.root)
        self.port = random.randint(10000, 65535)
        self.friends = {}
        self.messages = {}
        self.crypto = None
        self.status = False
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

        self.sock = None
        self.conn = None
        self.running = False
        self.friend_counter = 0

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
    def DHE(self, n = 2048):
        if not self.status:
            self.gui.log("You have ")
        self.gui.log("Begining DHE key exchange...")
        p = None
        g = None
        if n == 2048:
            p = Cryptography.DH_PRIME
            g = Cryptography.DH_GENERATOR
            self.gui.log(f"P = hard coded 2048 bit\ng = {Cryptography.DH_GENERATOR}")
            self.gui.log("\n")
        else:
            p = Cryptography.generate_prime(11) # ToDo. repace 11 with your choice of bits
            g = 2
            self.gui.log(f"P = {p}\ng = {g}")
            self.gui.log("\n")
        a = Cryptography.generate_DHE_key(p)
        public_key = Cryptography.compute_public_key(g , p , a)

        self.gui.log(f"a = {a}")
        self.gui.log("\n")




        


    def RSA(self):
        print()

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
