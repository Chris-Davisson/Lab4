.PHONY: server chat chat2 all

server:
	python -m control server -p 1234

chat:
	python -m control client

chat2:
	python -m control client

all:
ifeq ($(OS),Windows_NT)
	start cmd /k "python -m control server -p 1234"
	timeout /t 1 >nul
	start cmd /k "python -m control client"
	start cmd /k "python -m control client"
else
	python -m control server -p 1234 &
	sleep 1
	python -m control client &
	python -m control client &
endif
