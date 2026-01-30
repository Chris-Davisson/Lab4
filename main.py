'''
Main entry point for the applicaiton. we are not going to over complicate this. no cli, tui, etc... no switching to node and browser or java and whatever else.

ok we're gonna do this p2p with a directory. we dont want to look it up so I'm going to make the solution dead simple then improve. 

P1 → Register 
P2 → Register
P1 → P2 after getting the ip and port for the other one. 

Actually, we just do ip and port in the bar like filezilla. we can also keep the list and maybe implement the register later. as its own server

'''
import socket
import threading
import tkinter as tk
from gui import gui

class App:    
    def __init__(self, root):
        self.root = root
        self.gui = gui(self.root)
        self.port = 6000
        self.friends = {"self": ["127.0.0.1" , self.port] }
        self.messages = {}
        self.crypto = None

        self.gui.connect = self.connect
        self.gui.listen = self.listen
        self.gui.crypto_change = self.crypto_change
        self.gui.register = self.register
        self.gui.close = self.close
        self.gui.DHE = self.DHE
        self.gui.RSA = self.RSA
        self.gui.send_message = self.send_message

        self.populate_friends()

        self.sock = None
        self.conn = None
        self.running = False



    def listen(self , timeout=30):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(1)
        self.gui.log(f"Listening on port: {self.port}")
        self.gui.disable_listen()

        def accept():
            try:
                self.conn, addr = self.sock.accept()
                self.running = True
                self.root.after(0, lambda: self.gui.log(f"Connection from {addr}"))
                self.root.after(0, lambda: self.gui.set_status(True))
                self.receive_loop()
            except socket.timeout:
                self.root.after(0, lambda: self.gui.log("Listen timed out"))
                self.root.after(0, lambda: self.gui.enable_listen())
        threading.Thread(target=accept, daemon=True).start()



    def connect(self):
        self.add_to_chat("connect")

    def send_message(self):
        print("send")
    
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

    def DHE(self):
        print()

    def RSA(self):
        print()

    def populate_friends(self):
        self.gui.addr_listbox.config(state=tk.NORMAL)
        for name, (ip, port) in self.friends.items():
            self.gui.addr_listbox.insert(tk.END, f"{name:<10} {ip}:{port}\n")
        self.gui.addr_listbox.config(state=tk.DISABLED)

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

if __name__== "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()