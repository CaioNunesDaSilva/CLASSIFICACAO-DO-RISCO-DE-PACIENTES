from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from constantes import SOCKET_ENDERECO, SOCKET_PORTA, BUFFER

if __name__ == "__main__":
    CLIENTES = []
    CONEXOES = []

    while True:
        comando = input("SERVIDOR ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            exit()
            print("AINDA A USUARIOS CONECTADOS, AGUARDE...")

        else:
            print("COMANDO INVALIDO")

