from socket import socket, AF_INET, SOCK_STREAM
from sys import exit
from threading import Thread
from time import sleep

from IA import classificar
from auxiliar import codificar, descodificar, Requisicao
from constantes import TAXA_ATUALIZACAO_ARDUINO, SOCKET_ENDERECO, SOCKET_PORTA, BUFFER
from db import get_pacientes_ativos_db, get_medicoes_nao_classificadas_from_paciente, inserir_risco_medicao, \
    get_medicoes_paciente_ativos, get_all_medicoes_nao_classificadas


def checagem_pacientes_ativos():
    while CHECAR_PACIENTES_ATIVOS:

        pacientes_ativos_db = get_pacientes_ativos_db()

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

        elif requisicao == Requisicao.PROXIMO_PACIENTE:
            medicoes_pacientes = get_medicoes_paciente_ativos()

            pacientes = []
            risco_geral = []

            for medicoes_paciente in medicoes_pacientes:
                pacientes.append(medicoes_paciente[0][0])

                risco = 0
                for medicao in medicoes_paciente:
                    risco += medicao[-1]
                risco_geral.append(risco)

            indice = risco_geral.index(min(risco_geral))
            conexao.send(codificar([pacientes[indice], risco_geral[indice]]))

        elif requisicao == Requisicao.PACIENTES_EMERGENCIA:
            conexao.send(codificar(get_medicoes_paciente_ativos(risco=1, rows=1)))

        elif requisicao == Requisicao.PACIENTES_MUITO_URGENTE:
            conexao.send(codificar(get_medicoes_paciente_ativos(risco=2, rows=1)))

        elif requisicao == Requisicao.PACIENTES_URGENTE:
            conexao.send(codificar(get_medicoes_paciente_ativos(risco=3, rows=1)))

        elif requisicao == Requisicao.PACIENTES_POUCO_URGENTE:
            conexao.send(codificar(get_medicoes_paciente_ativos(risco=4, rows=1)))

        elif requisicao == Requisicao.PACIENTES_NAO_URGENTE:
            conexao.send(codificar(get_medicoes_paciente_ativos(risco=5, rows=1)))

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

        elif comando.upper() == "ANALISAR RISCOS":
            print("ANALISANDO MEDICOES NAO CLASSIFICADAS")
            for medicao in get_all_medicoes_nao_classificadas():
                risco = classificar(medicao[1:])
                inserir_risco_medicao(medicao[0], risco.to_int())
                print("MEDICAO {} CLASSIFICADA".format(medicao[0]))

        else:
            print("COMANDO INVALIDO")

