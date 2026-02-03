.PHONY: server chat setup-windows

server:
	python -m control server -p 1234

chat:
	python -m control client

setup-windows:
	setup.bat
