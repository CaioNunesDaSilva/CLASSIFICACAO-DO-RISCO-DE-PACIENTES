from socket import socket, AF_INET, SOCK_STREAM
from sys import exit

from auxiliar import codificar, descodificar, Requisicao
from constantes import SOCKET_ENDERECO, SOCKET_PORTA, BUFFER, NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO


def __print_pacientes_riscos(pacientes: list):
    print("PACIENTES DE RISCO:")
    for paciente in pacientes:
        print("ID: {}".format(paciente[0][0]))
        print("RISCO: {}\n".format(paciente[0][2]))


if __name__ == "__main__":
    CONECTADO = False
    soquete = socket(AF_INET, SOCK_STREAM)
    print("INICIANDO CONEXAO")
    while not CONECTADO:
        try:
            soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))
            CONECTADO = True
            print("SISTEMA MEDICO CONECTADO")

        except:
            print("ERRO DE CONECXAO, TENTANDO NOVAMENTE")

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

        elif comando.upper() == "PROXIMO PACIENTE":
            soquete.send(codificar(Requisicao(0)))
            print("BUSCANDO PACIENTE, AGUARDE...")
            paciente = descodificar(soquete.recv(BUFFER), "LISTA")
            print("PROXIMO PACIENTE,"
                  " COM BASE NAS ULTIMAS {} MEDICOES:".format(NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO))
            print("ID: {}".format(paciente[0]))
            print("RISCO MEDIO: {}".format(paciente[1] / NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO))

        elif comando.upper() == "LISTAR PACIENTES EMERGENCIA":
            soquete.send(codificar(Requisicao(1)))
            print("BUSCANDO PACIENTES EM ESTADO DE EMERGENCIA, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR PACIENTES MUITO URGENTE":
            soquete.send(codificar(Requisicao(2)))
            print("BUSCANDO PACIENTES EM ESTADO DE MUITO URGENTE, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR PACIENTES URGENTE":
            soquete.send(codificar(Requisicao(3)))
            print("BUSCANDO PACIENTES EM ESTADO DE URGENTE, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR PACIENTES POUCO URGENTE":
            soquete.send(codificar(Requisicao(4)))
            print("BUSCANDO PACIENTES EM ESTADO DE POUCO URGENTE, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR PACIENTES NAO URGENTE":
            soquete.send(codificar(Requisicao(5)))
            print("BUSCANDO PACIENTES EM ESTADO DE NAO URGENTE, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        else:
            print("COMANDO INVALIDO")
