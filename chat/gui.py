"""
Defining the tkinter GUI

"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class gui:
    def __init__(self, root):
        root.title("P2P Chat")
        self.connect = None
        self.listen = None
        self.cancel_listen = None
        self.disconnect = None
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

        self.connect_btn = ttk.Button(
            header, text="Connect", command=lambda: self.connect() if self.connect else None
        )
        self.connect_btn.pack(side=tk.LEFT, padx=2)

        self.listen_btn = ttk.Button(
            header, text="Listen", command=lambda: self.listen() if self.listen else None
        )
        self.listen_btn.pack(side=tk.LEFT, padx=2)

        self.DHE_btn = ttk.Button(
            header, text="DHE", command=lambda: self.DHE() if self.DHE else None
        )
        self.DHE_btn.pack(side=tk.LEFT, padx=2)

        self.RSA_btn = ttk.Button(
            header, text="RSA", command=lambda: self.RSA() if self.RSA else None
        )
        self.RSA_btn.pack(side=tk.LEFT, padx=2)

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
        left_panel.rowconfigure(0, weight=0)
        left_panel.rowconfigure(1, weight=0)
        left_panel.rowconfigure(2, weight=0)
        left_panel.rowconfigure(3, weight=0)
        left_panel.rowconfigure(4, weight=1)
        left_panel.columnconfigure(0, weight=1)

        # Name section
        name_frame = ttk.LabelFrame(left_panel, text="My Name")
        name_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.name_entry = tk.Entry(name_frame, width=15)
        self.name_entry.insert(0, "Me")
        self.name_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # My Port section
        port_frame = ttk.LabelFrame(left_panel, text="My Port")
        port_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        self.my_port_entry = tk.Entry(port_frame, width=10)
        self.my_port_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.set_port_btn = ttk.Button(
            port_frame, text="Set", command=lambda: self.set_port() if self.set_port else None
        )
        self.set_port_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.set_port = None

        # Relay section
        relay_frame = ttk.LabelFrame(left_panel, text="Relay Server")
        relay_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        ttk.Label(relay_frame, text="Host:").pack(side=tk.LEFT, padx=(5, 2), pady=5)
        self.relay_host_entry = tk.Entry(relay_frame, width=12)
        self.relay_host_entry.pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Label(relay_frame, text="Port:").pack(side=tk.LEFT, padx=(5, 2), pady=5)
        self.relay_port_entry = tk.Entry(relay_frame, width=6)
        self.relay_port_entry.pack(side=tk.LEFT, padx=2, pady=5)

        # Saved addresses section
        addr_frame = ttk.LabelFrame(left_panel, text="Saved Addresses")
        addr_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))

        self.addr_combo = ttk.Combobox(addr_frame, state="readonly", width=20)
        self.addr_combo.pack(padx=5, pady=5, fill=tk.X)
        self.addr_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_address_selected() if self.on_address_selected else None,
        )
        self.on_address_selected = None

        # Shared keys section
        keys_frame = ttk.LabelFrame(left_panel, text="Shared Keys")
        keys_frame.grid(row=4, column=0, sticky="nsew")
        keys_frame.rowconfigure(0, weight=1)
        keys_frame.columnconfigure(0, weight=1)

        self.keys_display = scrolledtext.ScrolledText(
            keys_frame, state=tk.DISABLED, width=25, height=8
        )
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
        self.msg_entry.bind(
            "<Return>", lambda e: self.send_message() if self.send_message else None
        )

        ttk.Button(
            input_frame,
            text="Send",
            command=lambda: self.send_message() if self.send_message else None,
        ).pack(side=tk.RIGHT)

        root.protocol("WM_DELETE_WINDOW", lambda: self.close() if self.close else None)

    def log(self, txt):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, txt + "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def set_listen_mode(self):
        self.listen_btn.config(
            text="Listen", command=lambda: self.listen() if self.listen else None
        )

    def set_cancel_mode(self):
        self.listen_btn.config(
            text="Cancel", command=lambda: self.cancel_listen() if self.cancel_listen else None
        )

    def set_disconnect_mode(self):
        self.listen_btn.config(
            text="Disconnect", command=lambda: self.disconnect() if self.disconnect else None
        )

    def set_status(self, connected):
        if connected:
            self.status_label.config(text="Connected", style="Green.TLabel")
        else:
            self.status_label.config(text="Disconnected", style="Red.TLabel")
