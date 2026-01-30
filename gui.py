'''
Defining the tkinter GUI

'''

import tkinter as tk
from tkinter import ttk, scrolledtext

class gui:
    def __init__(self, root):
        root.title("P2P Chat")        
        self.connect = None
        self.listen = None
        self.crypto_change = None
        self.register = None
        self.close = None
        self.DHE = None
        self.RSA = None
        self.send_message = None

        header = ttk.Frame(root)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header, text="Host:").pack(side=tk.LEFT)
        self.host_entry = tk.Entry(header, width=15)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(header, text="Port:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(header, width=6)
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(side=tk.LEFT, padx=2)
        
        self.connect_btn = ttk.Button(header, text="Connect", command=lambda: self.connect() if self.connect else None)
        self.connect_btn.pack(side=tk.LEFT, padx=2)

        self.listen_btn = ttk.Button(header, text="Listen", command=lambda: self.listen() if self.listen else None)
        self.listen_btn.pack(side=tk.LEFT, padx=2)

        self.DHE_btn = ttk.Button(header, text='DHE', command=lambda: self.DHE() if self.DHE else None)
        self.DHE_btn.pack(side=tk.LEFT,padx=2)

        self.RSA_btn = ttk.Button(header, text='RSA', command=lambda: self.RSA() if self.RSA else None)
        self.RSA_btn.pack(side=tk.LEFT,padx=2)
        
        style = ttk.Style()
        style.configure("Red.TLabel", foreground="red")
        style.configure("Green.TLabel", foreground="green")
        self.status_label = ttk.Label(header, text="Disconnected", style="Red.TLabel")
        self.status_label.pack(side=tk.RIGHT)

        # Main content frame with resizable panes
        paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel (split vertically)
        left_panel = ttk.Frame(paned)
        left_panel.rowconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)

        # Saved addresses section
        addr_frame = ttk.LabelFrame(left_panel, text="Saved Addresses")
        addr_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        addr_frame.rowconfigure(0, weight=1)
        addr_frame.columnconfigure(0, weight=1)

        self.addr_listbox = scrolledtext.ScrolledText(addr_frame, width=25, height=8)
        self.addr_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Shared keys section
        keys_frame = ttk.LabelFrame(left_panel, text="Shared Keys")
        keys_frame.grid(row=1, column=0, sticky="nsew")
        keys_frame.rowconfigure(0, weight=1)
        keys_frame.columnconfigure(0, weight=1)

        self.keys_display = scrolledtext.ScrolledText(keys_frame, state=tk.DISABLED, width=25, height=8)
        self.keys_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        paned.add(left_panel, weight=1)

        # Chat display
        chat_frame = ttk.Frame(paned)
        paned.add(chat_frame, weight=3)
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, height=20)
        self.chat_display.grid(row=0, column=0, sticky="nsew")

        # Message input
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.msg_entry = tk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_message() if self.send_message else None)

        tk.Button(input_frame, text="Send", command=lambda: self.send_message() if self.send_message else None).pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", lambda: self.close() if self.close else None)

    def log(self, txt):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, txt + "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def disable_listen(self):
        self.listen_btn.config(state=tk.DISABLED)