'''
Main entry point for the applicaiton. we are not going to over complicate this. no cli, tui, etc... no switching to node and browser or java and whatever else.


'''

import tkinter as tk
from tkinter import ttk, scrolledtext

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Key exchange chat")
        self.root.geometry("700x500")

        self.build_ui()

    def build_ui(self):
        header = ttk.Frame(self.root, padding=5)
        header.pack(fill=tk.X)

        ttk.Button(header, text='Listen', command = self.on_listen).pack(side=tk.LEFT, padx=2)
        ttk.Button(header, text='Connect', command = self.on_connect).pack(side=tk.LEFT, padx=2)

        
# Event listeners

    def on_listen(self):
        print("listen")

    def on_connect(self):
        print("connect")

    def on_send(self):
        print("send")
    
    def on_crypto_change(self):
        print("")

if __name__== "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()