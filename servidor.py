from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from sys import exit
from threading import Thread
from time import sleep

from numpy import array, ndarray

from IA import criar
from auxiliar import codificar, descodificar, Requisicao, gerar_temp, gerar_oxi, gerar_bpm
from constantes import TAXA_ATUALIZACAO_ARDUINO, SOCKET_ENDERECO, SOCKET_PORTA, BUFFER, NUMERO_DE_MEDICOES_MINIMAS_DB
from db import get_pacientes_ativos_db, inserir_risco_medicao, get_n_medicoes_pacientes_ativos, \
    get_all_medicoes_pacientes_ativos, get_all_medicoes_nao_classificadas, get_all_medicoes, inserir_medicao


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

        medicoes = get_all_medicoes_nao_classificadas(paciente)
        for medicao in medicoes:

            risco = IA.predict(array(medicao[1:]).reshape(1, -1))
            if isinstance(risco, ndarray):
                risco = risco[0]
                inserir_risco_medicao(medicao[0], risco)
            else:
                inserir_risco_medicao(medicao[0], risco.to_int())

        sleep(TAXA_ATUALIZACAO_ARDUINO)


def conexao_sistema_medico(conexao, endereco):
    while CONEXAO_SISTEMA_MEDICO:
        requisicao = descodificar(conexao.recv(BUFFER), Requisicao)

        if requisicao == Requisicao.DESCONECTAR:
            break

        elif requisicao == Requisicao.PROXIMO_PACIENTE:
            medicoes_pacientes = get_n_medicoes_pacientes_ativos()

            if medicoes_pacientes:
                pacientes = []
                for x in range(len(medicoes_pacientes)):
                    if medicoes_pacientes[x]:
                        pacientes.append(medicoes_pacientes[x][0][-1])

                riscos = []
                for medicoes_paciente in medicoes_pacientes:
                    risco_soma = 0
                    for medicao_paciente in medicoes_paciente:
                        risco_soma += medicao_paciente[-2]

                    if medicoes_paciente:
                        riscos.append(risco_soma)

                indice = riscos.index(min(riscos))
                conexao.send(codificar([pacientes[indice], riscos[indice]]))

            else:
                conexao.send(codificar([]))

        elif requisicao == Requisicao.PACIENTES_EMERGENCIA:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=1)))

        elif requisicao == Requisicao.PACIENTES_MUITO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=2)))

        elif requisicao == Requisicao.PACIENTES_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=3)))

        elif requisicao == Requisicao.PACIENTES_POUCO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=4)))

        elif requisicao == Requisicao.PACIENTES_NAO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=5)))

        else:
            break


if __name__ == "__main__":
    if len(get_all_medicoes()) < NUMERO_DE_MEDICOES_MINIMAS_DB:
        print("POUCOS VALORES NO BANCO DE DADOS PARA TREINAMENTO DA IA,"
              " INSERINDO {} NOVOS VALORES...".format(NUMERO_DE_MEDICOES_MINIMAS_DB))
        for x in range(NUMERO_DE_MEDICOES_MINIMAS_DB):
            risco = randint(1, 5)
            inserir_medicao(1, gerar_oxi(risco), gerar_bpm(risco), gerar_temp(risco), risco)
        print("VALORES INSERIRDOS")

    print("TREINANDO IA...")
    IA = criar()

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
            Thread(target=checagem_pacientes_ativos).start()
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
                risco = IA.predict(array(medicao[1:]).reshape(1, -1))
                inserir_risco_medicao(medicao[0], risco.to_int())
                print("MEDICAO {} CLASSIFICADA".format(medicao[0]))

        elif comando.upper() == "RETREINAR IA":
            CHECAR_PACIENTES_ATIVOS = False
            PACIENTES_ATIVOS.clear()
            print("RETREINANDO IA, AGUARDE...")
            IA = criar()
            print("IA TREINADA")
            CHECAR_PACIENTES_ATIVOS = True
            Thread(target=checagem_pacientes_ativos).start()

        else:
            print("COMANDO INVALIDO")
