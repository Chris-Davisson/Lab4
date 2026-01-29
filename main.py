'''
Main entry point for the applicaiton. we are not going to over complicate this. no cli, tui, etc... no switching to node and browser or java and whatever else.

ok we're gonna do this p2p with a directory. we dont want to look it up so I'm going to make the solution dead simple then improve. 

P1 → Register 
P2 → Register
P1 → P2 after getting the ip and port for the other one. 

Actually, we just do ip and port in the bar like filezilla. we can also keep the list and maybe implement the register later. as its own server

'''

import tkinter as tk
from tkinter import ttk, scrolledtext
from app import app

class App:
    friends = {}

    
    def __init__(self, root):
        self.root = root
        self.gui = app(self.root)

        app.connect = self.connect
        app.listen = self.listen 
        app.crypto_change = self.crypto_change 
        app.register = self.register 
        app.close = self.close 
        app.DHE = self.DHE
        app.RSA = self.RSA 
        app.send_message = self.send_message

        self.sock = None
        self.conn = None
        self.running = False

# Event listeners

    def listen(self):
        print("listen")

    def connect(self):
        print("connect")

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

if __name__== "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()