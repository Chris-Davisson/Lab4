import socket
import threading
import msvcrt
import sys
import system

class Server:
    def __init__(self, port=9000):
        self.port = port
        self.clients = {}
        self.pairs = {}
        self.running = True
        self.sock = None
        self.lock = threading.Lock()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        self.sock.settimeout(1.0)
        print(f"Relay server listening on port {self.port}")
        print("Press Q to quit")

        threading.Thread(target=self.keyboard_listener, daemon=True).start()

        while self.running:
            try:
                conn, addr = self.sock.accept()
                print(f"Client connected: {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break

        self.shutdown()

    def handle_client(self, conn, addr):
        client_name = None
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = data.decode("utf-8").strip()

                # Handle REGISTER command
                if message.startswith("REGISTER "):
                    name = message[9:].strip()
                    if name:
                        with self.lock:
                            if name in self.clients:
                                conn.send(b"ERROR Name already taken\n")
                            else:
                                self.clients[name] = conn
                                client_name = name
                                conn.send(b"REGISTERED\n")
                                print(f"Client registered as: {name}")
                    else:
                        conn.send(b"ERROR Invalid name\n")

                # LIST command
                elif message == "LIST":
                    with self.lock:
                        # Filter out the requesting client's own name
                        names = [n for n in self.clients.keys() if n != client_name]
                    response = "USERS " + ",".join(names) + "\n"
                    conn.send(response.encode("utf-8"))

                # CHAT_REQUEST command
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
                            # Ends chat and starts new one
                            if client_name in self.pairs:
                                old_partner = self.pairs[client_name]
                                del self.pairs[client_name]
                                if old_partner in self.pairs:
                                    del self.pairs[old_partner]
                                if old_partner in self.clients:
                                    try:
                                        self.clients[old_partner].send(b"CHAT_ENDED\n")
                                    except:
                                        pass
                                conn.send(b"CHAT_ENDED\n")
                                print(f"Ended chat between {client_name} and {old_partner}")

                            # Start new chat
                            self.pairs[client_name] = target_name
                            self.pairs[target_name] = client_name
                            target_conn = self.clients[target_name]
                            conn.send(f"CHAT_STARTED {target_name}\n".encode("utf-8"))
                            target_conn.send(f"CHAT_STARTED {client_name}\n".encode("utf-8"))
                            print(f"Paired {client_name} with {target_name}")

                # END_CHAT command
                elif message == "END_CHAT":
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            del self.pairs[client_name]
                            if partner_name in self.pairs:
                                del self.pairs[partner_name]
                            if partner_name in self.clients:
                                try:
                                    self.clients[partner_name].send(b"CHAT_ENDED\n")
                                except:
                                    pass
                            conn.send(b"CHAT_ENDED\n")
                            print(f"Chat ended between {client_name} and {partner_name}")
                        else:
                            conn.send(b"ERROR Not in a chat\n")

                # Relay part
                else:
                    with self.lock:
                        if client_name and client_name in self.pairs:
                            partner_name = self.pairs[client_name]
                            if partner_name in self.clients:
                                partner_conn = self.clients[partner_name]
                                partner_conn.send(data)

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
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
                                self.clients[partner_name].send(b"CHAT_ENDED\n")
                            except:
                                pass
                        print(f"Unpaired {client_name} from {partner_name}")
                    if client_name in self.clients:
                        del self.clients[client_name]
                        print(f"Client unregistered: {client_name}")
            try:
                conn.close()
            except:
                pass

                # Q to quit

    def keyboard_listener(self):
        while self.running:
            try:
                key = input().strip().upper()
                if key == "Q":
                    print("\nShutting down")
                    self.running = False
                    break
            except EOFError:
                break

    def shutdown(self):
        with self.lock:
            for name, conn in self.clients.items():
                try:
                    conn.close()
                except:
                    pass
            self.clients.clear()
        if self.sock:
            self.sock.close()
        print("Server stopped")
        sys.exit(0)


def run_server(port=9000):
    server = Server(port)
    server.run()
