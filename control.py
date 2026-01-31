import argparse


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="mode")

    # Server
    server_parser = subparser.add_parser("server", aliases=["s"])
    server_parser.add_argument("-p", "--port", type=int, default=9000)
    server_parser.add_argument("-x", "--headless", action="store_true")

    # Client
    client_parser = subparser.add_parser("client", aliases=["c"])
    client_parser.add_argument("--gui", action="store_true", default=True)
    client_parser.add_argument("--tui", action="store_true")

    args = parser.parse_args()

    if args.mode in ("server", "s"):
        from server.server import server

        server.run_server()
    elif args.mode in ("client", "c"):
        if args.tui:
            print("TUI mode not implemented")
        else:
            from chat.chat import main as chat_main

            chat_main()
    else:
        from chat.chat import main as chat_main

        chat_main()


if __name__ == "__main__":
    main()
