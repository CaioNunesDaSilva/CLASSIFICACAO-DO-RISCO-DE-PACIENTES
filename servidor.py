from sys import exit
from threading import Thread
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM

from IA import classificar
from auxiliar import codificar, descodificar, Requisicao
from db import checar_pacientes_ativos_db, get_medicoes_nao_classificadas_from_paciente, inserir_risco_medicao

from constantes import TAXA_ATUALIZACAO_ARDUINO, SOCKET_ENDERECO, SOCKET_PORTA, BUFFER


def checagem_pacientes_ativos():
    while CHECAR_PACIENTES_ATIVOS:

        pacientes_ativos_db = checar_pacientes_ativos_db()

        for paciente in pacientes_ativos_db:
            if paciente not in PACIENTES_ATIVOS:
                PACIENTES_ATIVOS.append(paciente)
                Thread(target=analisar_medicoes, args=(paciente, )).start()

        for paciente in PACIENTES_ATIVOS:
            if paciente not in pacientes_ativos_db:
                PACIENTES_ATIVOS.remove(paciente)

        sleep(TAXA_ATUALIZACAO_ARDUINO)


def analisar_medicoes(paciente: int):
    while paciente in PACIENTES_ATIVOS:

        medicoes = get_medicoes_nao_classificadas_from_paciente(paciente)
        for medicao in medicoes:

            risco = classificar(medicao[1:])

            inserir_risco_medicao(medicao[0], risco.to_int())

        sleep(TAXA_ATUALIZACAO_ARDUINO)


def conexao_sistema_medico(conexao, endereco):
    while CONEXAO_SISTEMA_MEDICO:
        requisicao = descodificar(conexao.recv(BUFFER), Requisicao)

        if requisicao == Requisicao.DESCONECTAR:
            break

        else:
            break


if __name__ == "__main__":
    PACIENTES_ATIVOS = []
    CHECAR_PACIENTES_ATIVOS = True
    Thread(target=checagem_pacientes_ativos).start()

    CONEXAO_SISTEMA_MEDICO = True
    soquete = socket(AF_INET, SOCK_STREAM)
    soquete.bind((SOCKET_ENDERECO, SOCKET_PORTA))
    soquete.settimeout(10)
    soquete.listen()

    while True:
        comando = input("SERVIDOR ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
            PACIENTES_ATIVOS.clear()
            soquete.close()
            exit(0)
            print("TERMINANDO APLICACAO, AGUARDE...")

        elif comando.upper() == "FECHAR PACIENTES":
            CHECAR_PACIENTES_ATIVOS = False
            PACIENTES_ATIVOS.clear()
            print("SERVIDOR FECHADO PARA PACIENTES")

        elif comando.upper() == "ABRIR PACIENTES":
            CHECAR_PACIENTES_ATIVOS = True
            print("SERVIDOR ABERTO PARA PACIENTES")

        elif comando.upper() == "LISTAR PACIENTES":
            print("----------")
            for id_paciente in PACIENTES_ATIVOS:
                print("id: {}".format(id_paciente))
            print("----------")

        elif comando.upper() == "CONECTAR MEDICO":
            print("CONECTANDO COM SISTEMA MEDICO NO ENDERECO:{}, PORTA:{}".format(SOCKET_ENDERECO, SOCKET_PORTA))
            conexao, endereco = soquete.accept()
            print("SISTEMA MEDICO ENCONTRADO")
            Thread(target=conexao_sistema_medico, args=(conexao, endereco)).start()
            print("SISTEMA MEDICO CONECTADO")

        elif comando.upper() == "FECHAR MEDICO":
            CONEXAO_SISTEMA_MEDICO = False
            soquete.close()
            print("SERVIDOR FECHADO PARA SISTEMAS MEDICOS")

        elif comando.upper() == "ABRIR MEDICO":
            CONEXAO_SISTEMA_MEDICO = True
            soquete = socket(AF_INET, SOCK_STREAM)
            soquete.bind((SOCKET_ENDERECO, SOCKET_PORTA))
            soquete.settimeout(10)
            soquete.listen()
            print("SERVIDOR ABERTO PARA SISTEMAS MEDICOS")

        else:
            print("COMANDO INVALIDO")

