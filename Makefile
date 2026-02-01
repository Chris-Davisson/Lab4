.PHONY: server server-headless chat chat2 all

server:
	python -m control server -p 1234

server-headless:
	python -m control server -p 1234 --headless

chat:
	python -m control client

chat2:
	python -m control client

all:
	start cmd /k "python -m control server -p 1234"
	timeout /t 1 >nul
	start cmd /k "python -m control client"
	start cmd /k "python -m control client"

