'''
Defining the tkinter GUI

'''

import tkinter as tk
from tkinter import ttk, scrolledtext

class app:
    def __init__(self, root):
        root.title("P2P Chat")        
        self.connect = None
        self.listen = None
        self.crypto_change = None
        self.register = None
        self.close = None
        self. DHE = None
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
        
        self.connect_btn = ttk.Button(header, text="Connect", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=2)
        
        self.listen_btn = ttk.Button(header, text="Listen", command=self.listen)
        self.listen_btn.pack(side=tk.LEFT, padx=2)

        self.DHE_btn = ttk.Button(header, text='DHE', command=self.DHE)
        self.DHE_btn.pack(side=tk.LEFT,padx=2)

        self.RSA_btn = ttk.Button(header, text='RSA', command=self.RSA)
        self.RSA_btn.pack(side=tk.LEFT,padx=2)
        
        style = ttk.Style()
        style.configure("Red.TLabel", foreground="red")
        style.configure("Green.TLabel", foreground="green")
        self.status_label = ttk.Label(header, text="Disconnected", style="Red.TLabel")
        self.status_label.pack(side=tk.RIGHT)

        # Main content frame
        content_frame = ttk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)  # left panel
        content_frame.columnconfigure(1, weight=3)  # chat display
        content_frame.rowconfigure(0, weight=1)

        # Left panel (split vertically)
        left_panel = ttk.Frame(content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel.rowconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)

        # Saved addresses section
        addr_frame = ttk.LabelFrame(left_panel, text="Saved Addresses")
        addr_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        addr_frame.rowconfigure(0, weight=1)
        addr_frame.columnconfigure(0, weight=1)

        self.addr_listbox = tk.Listbox(addr_frame, width=25)
        self.addr_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Shared keys section
        keys_frame = ttk.LabelFrame(left_panel, text="Shared Keys")
        keys_frame.grid(row=1, column=0, sticky="nsew")
        keys_frame.rowconfigure(0, weight=1)
        keys_frame.columnconfigure(0, weight=1)

        self.keys_display = scrolledtext.ScrolledText(keys_frame, state=tk.DISABLED, width=25, height=8)
        self.keys_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Chat display with Q button
        chat_frame = ttk.Frame(content_frame)
        chat_frame.grid(row=0, column=1, sticky="nsew")
        chat_frame.rowconfigure(1, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, height=20)
        self.chat_display.grid(row=1, column=0, sticky="nsew")

        # Message input
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.msg_entry = tk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(input_frame, text="Send", command=self.send_message).pack(side=tk.RIGHT)
        
        root.protocol("WM_DELETE_WINDOW", self.close)