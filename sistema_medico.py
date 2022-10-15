from sys import exit
from socket import socket, AF_INET, SOCK_STREAM

from auxiliar import codificar, descodificar, Requisicao

from constantes import SOCKET_ENDERECO, SOCKET_PORTA

if __name__ == "__main__":
    soquete = socket(AF_INET, SOCK_STREAM)
    soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))

    while True:
        comando = input("SISTEMA MEDICO ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            soquete.send(codificar(Requisicao(6)))
            soquete.close()
            exit(0)

        elif comando.upper() == "DESCONECTAR":
            soquete.send(codificar(Requisicao(6)))
            soquete.close()
            print("DESCONECTADO DO SERVIDOR")

        elif comando.upper() == "CONECTAR":
            soquete = socket(AF_INET, SOCK_STREAM)
            soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))
            print("CONEXAO REQUISITADA")

        else:
            print("COMANDO INVALIDO")
