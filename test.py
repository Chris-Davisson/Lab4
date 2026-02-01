# test.py
import subprocess
import sys
import time


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    port = 1234

    # Start server in new window
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k",
                      f"python -m control server -p {port}"])
    time.sleep(1)

    # Start n chat clients
    for _ in range(n):
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k",
                          "python -m control client"])


if __name__ == "__main__":
    main()
