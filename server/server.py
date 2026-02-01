import socket
import threading
import sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container, Vertical


class ServerApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #users-section {
        height: 1fr;
        border: solid green;
        padding: 1;
    }

    #conversations-section {
        height: 1fr;
        border: solid blue;
        padding: 1;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, server: "Server"):
        super().__init__()
        self.server = server

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="users-section"):
                yield Static("Connected Users", classes="section-title")
                yield DataTable(id="users-table")
            with Container(id="conversations-section"):
                yield Static("Active Conversations", classes="section-title")
                yield DataTable(id="conversations-table")
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"Relay Server - Port {self.server.port}"

        users_table = self.query_one("#users-table", DataTable)
        users_table.add_columns("Name", "IP", "Port")

        conv_table = self.query_one("#conversations-table", DataTable)
        conv_table.add_columns("User 1", "User 2")

        threading.Thread(target=self.server.run_server_loop, daemon=True).start()

    def refresh_users(self) -> None:
        table = self.query_one("#users-table", DataTable)
        table.clear()
        with self.server.lock:
            for name, info in self.server.clients.items():
                table.add_row(name, info["ip"], str(info["port"]))

    def refresh_conversations(self) -> None:
        table = self.query_one("#conversations-table", DataTable)
        table.clear()
        seen = set()
        with self.server.lock:
            for user1, user2 in self.server.pairs.items():
                pair = tuple(sorted([user1, user2]))
                if pair not in seen:
                    seen.add(pair)
                    table.add_row(pair[0], pair[1])

    def action_quit(self) -> None:
        self.server.running = False
        self.server.shutdown()
        self.exit()


class Server:
    def __init__(self, port=1234):
        self.port = port
        self.clients = {}  # {name: {"conn": conn, "ip": ip, "port": port}}
        self.pairs = {}
        self.running = True
        self.sock = None
        self.lock = threading.Lock()
        self.app = None  # Reference to Textual app

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        self.sock.settimeout(1.0)

        self.app = ServerApp(self)
        self.app.run()

    def run_server_loop(self):
        while self.running:
            try:
                conn, addr = self.sock.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def handle_client(self, conn, addr):
        client_name = None
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = data.decode("utf-8").strip()

                if message.startswith("REGISTER "):
                    name = message[9:].strip()
                    if name:
                        with self.lock:
                            if name in self.clients:
                                conn.send(b"ERROR Name already taken\n")
                            else:
                                self.clients[name] = {
                                    "conn": conn,
                                    "ip": addr[0],
                                    "port": addr[1]
                                }
                                client_name = name
                                conn.send(b"REGISTERED\n")
                        if client_name and self.app:
                            self.app.call_from_thread(self.app.refresh_users)
                    else:
                        conn.send(b"ERROR Invalid name\n")

                elif message == "LIST":
                    with self.lock:
                        names = [n for n in self.clients.keys() if n != client_name]
                    response = "USERS " + ",".join(names) + "\n"
                    conn.send(response.encode("utf-8"))

                elif message.startswith("CHAT_REQUEST "):
                    target_name = message[13:].strip()
                    chat_started = False
                    with self.lock:
                        if not client_name:
                            conn.send(b"ERROR Not registered\n")
                        elif target_name not in self.clients:
                            conn.send(b"ERROR User not found\n")
                        elif target_name == client_name:
                            conn.send(b"ERROR Cannot chat with yourself\n")
                        elif target_name in self.pairs:
                            conn.send(b"ERROR User is busy\n")
                        else:
                            if client_name in self.pairs:
                                old_partner = self.pairs[client_name]
                                del self.pairs[client_name]
                                if old_partner in self.pairs:
                                    del self.pairs[old_partner]
                                if old_partner in self.clients:
                                    try:
                                        self.clients[old_partner]["conn"].send(b"CHAT_ENDED\n")
                                    except:
                                        pass
                                conn.send(b"CHAT_ENDED\n")

                            self.pairs[client_name] = target_name
                            self.pairs[target_name] = client_name
                            target_conn = self.clients[target_name]["conn"]
                            conn.send(f"CHAT_STARTED {target_name}\n".encode("utf-8"))
                            target_conn.send(f"CHAT_STARTED {client_name}\n".encode("utf-8"))
                            chat_started = True
                    if chat_started and self.app:
                        self.app.call_from_thread(self.app.refresh_conversations)

                elif message == "END_CHAT":
                    chat_ended = False
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            del self.pairs[client_name]
                            if partner_name in self.pairs:
                                del self.pairs[partner_name]
                            if partner_name in self.clients:
                                try:
                                    self.clients[partner_name]["conn"].send(b"CHAT_ENDED\n")
                                except:
                                    pass
                            conn.send(b"CHAT_ENDED\n")
                            chat_ended = True
                        else:
                            conn.send(b"ERROR Not in a chat\n")
                    if chat_ended and self.app:
                        self.app.call_from_thread(self.app.refresh_conversations)

                else:
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            if partner_name in self.clients:
                                partner_conn = self.clients[partner_name]["conn"]
                                partner_conn.send(data)

        except Exception:
            pass
        finally:
            client_removed = False
            chat_ended = False
            if client_name:
                with self.lock:
                    if client_name in self.pairs:
                        partner_name = self.pairs[client_name]
                        del self.pairs[client_name]
                        if partner_name in self.pairs:
                            del self.pairs[partner_name]
                        if partner_name in self.clients:
                            try:
                                self.clients[partner_name]["conn"].send(b"CHAT_ENDED\n")
                            except:
                                pass
                        chat_ended = True
                    if client_name in self.clients:
                        del self.clients[client_name]
                        client_removed = True
            try:
                conn.close()
            except:
                pass
            if self.app:
                if client_removed:
                    self.app.call_from_thread(self.app.refresh_users)
                if chat_ended:
                    self.app.call_from_thread(self.app.refresh_conversations)

    def run_headless(self):
        """Run the server without TUI (console output only)."""
        import msvcrt

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        self.sock.settimeout(1.0)
        print(f"Relay server listening on port {self.port}")
        print("Press Q to quit")

        def keyboard_listener():
            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode("utf-8", errors="ignore").upper()
                    if key == "Q":
                        print("\nShutting down server...")
                        self.running = False
                        break

        threading.Thread(target=keyboard_listener, daemon=True).start()

        while self.running:
            try:
                conn, addr = self.sock.accept()
                print(f"Client connected: {addr}")
                threading.Thread(target=self.handle_client_headless, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break

        self.shutdown()
        print("Server stopped")

    def handle_client_headless(self, conn, addr):
        """Handle client with print-based logging."""
        client_name = None
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = data.decode("utf-8").strip()

                if message.startswith("REGISTER "):
                    name = message[9:].strip()
                    if name:
                        with self.lock:
                            if name in self.clients:
                                conn.send(b"ERROR Name already taken\n")
                            else:
                                self.clients[name] = {"conn": conn, "ip": addr[0], "port": addr[1]}
                                client_name = name
                                conn.send(b"REGISTERED\n")
                                print(f"Client registered: {name} ({addr[0]}:{addr[1]})")
                    else:
                        conn.send(b"ERROR Invalid name\n")

                elif message == "LIST":
                    with self.lock:
                        names = [n for n in self.clients.keys() if n != client_name]
                    response = "USERS " + ",".join(names) + "\n"
                    conn.send(response.encode("utf-8"))

                elif message.startswith("CHAT_REQUEST "):
                    target_name = message[13:].strip()
                    with self.lock:
                        if not client_name:
                            conn.send(b"ERROR Not registered\n")
                        elif target_name not in self.clients:
                            conn.send(b"ERROR User not found\n")
                        elif target_name == client_name:
                            conn.send(b"ERROR Cannot chat with yourself\n")
                        elif target_name in self.pairs:
                            conn.send(b"ERROR User is busy\n")
                        else:
                            if client_name in self.pairs:
                                old_partner = self.pairs[client_name]
                                del self.pairs[client_name]
                                if old_partner in self.pairs:
                                    del self.pairs[old_partner]
                                if old_partner in self.clients:
                                    try:
                                        self.clients[old_partner]["conn"].send(b"CHAT_ENDED\n")
                                    except:
                                        pass
                                conn.send(b"CHAT_ENDED\n")
                                print(f"Chat ended: {client_name} <-> {old_partner}")

                            self.pairs[client_name] = target_name
                            self.pairs[target_name] = client_name
                            target_conn = self.clients[target_name]["conn"]
                            conn.send(f"CHAT_STARTED {target_name}\n".encode("utf-8"))
                            target_conn.send(f"CHAT_STARTED {client_name}\n".encode("utf-8"))
                            print(f"Chat started: {client_name} <-> {target_name}")

                elif message == "END_CHAT":
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            del self.pairs[client_name]
                            if partner_name in self.pairs:
                                del self.pairs[partner_name]
                            if partner_name in self.clients:
                                try:
                                    self.clients[partner_name]["conn"].send(b"CHAT_ENDED\n")
                                except:
                                    pass
                            conn.send(b"CHAT_ENDED\n")
                            print(f"Chat ended: {client_name} <-> {partner_name}")
                        else:
                            conn.send(b"ERROR Not in a chat\n")

                else:
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            if partner_name in self.clients:
                                self.clients[partner_name]["conn"].send(data)

        except Exception:
            pass
        finally:
            if client_name:
                with self.lock:
                    if client_name in self.pairs:
                        partner_name = self.pairs[client_name]
                        del self.pairs[client_name]
                        if partner_name in self.pairs:
                            del self.pairs[partner_name]
                        if partner_name in self.clients:
                            try:
                                self.clients[partner_name]["conn"].send(b"CHAT_ENDED\n")
                            except:
                                pass
                        print(f"Chat ended: {client_name} <-> {partner_name}")
                    if client_name in self.clients:
                        del self.clients[client_name]
                        print(f"Client disconnected: {client_name}")
            try:
                conn.close()
            except:
                pass

    def shutdown(self):
        self.running = False
        with self.lock:
            for name, info in self.clients.items():
                try:
                    info["conn"].close()
                except:
                    pass
            self.clients.clear()
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


def run_server(port=9000, headless=False):
    server = Server(port)
    if headless:
        server.run_headless()
    else:
        server.run()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=9000)
    parser.add_argument("-x", "--headless", action="store_true", help="Run without TUI")
    args = parser.parse_args()
    run_server(args.port, args.headless)
