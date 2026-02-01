import socket
import threading
import msvcrt
import sys


class Server:
    def __init__(self, port=9000):
        self.port = port
        self.clients = []  # list of connected sockets
        self.running = True
        self.sock = None

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(2)
        self.sock.settimeout(1.0)  # timeout to check for quit
        print(f"Relay listening on port {self.port}")
        print("Press Q to quit")

        # Start keyboard listener thread
        threading.Thread(target=self.keyboard_listener, daemon=True).start()

        while len(self.clients) < 2 and self.running:
            try:
                conn, addr = self.sock.accept()
                self.clients.append(conn)
                print(f"Client connected: {addr}")
            except socket.timeout:
                continue

        if not self.running:
            self.shutdown()
            return

        print("Two clients connected. Relaying messages...")

        # Start relay threads for both directions
        threading.Thread(target=self.relay, args=(0, 1), daemon=True).start()
        threading.Thread(target=self.relay, args=(1, 0), daemon=True).start()

        # Wait for quit
        while self.running:
            threading.Event().wait(0.5)

        self.shutdown()

    def keyboard_listener(self):
        """Listen for Q key to quit"""
        while self.running:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').upper()
                if key == 'Q':
                    print("\nShutting down server...")
                    self.running = False
                    break

    def shutdown(self):
        """Clean up connections"""
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        if self.sock:
            self.sock.close()
        print("Server stopped")
        sys.exit(0)

    def relay(self, from_idx, to_idx):
        """Forward messages from one client to the other"""
        while self.running:
            try:
                data = self.clients[from_idx].recv(4096)
                if not data:
                    break
                self.clients[to_idx].send(data)
            except:
                break
        if self.running:
            print("Connection closed")
            self.running = False


def run_server(port=9000):
    server = Server(port)
    server.run()
