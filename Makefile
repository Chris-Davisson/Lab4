.PHONY: server chat1 chat2 all

server:
	python -m control server -p 1234

chat:
	python -m control client

