from sys import exit
from threading import Thread
from time import sleep

from constantes import TAXA_ATUALIZACAO_ARDUINO

from db import checar_pacientes_ativos_db


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

        sleep(TAXA_ATUALIZACAO_ARDUINO)


if __name__ == "__main__":
    PACIENTES_ATIVOS = []

    CHECAR_PACIENTES_ATIVOS = True

    Thread(target=checagem_pacientes_ativos).start()

    while True:
        comando = input("SERVIDOR ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            CHECAR_PACIENTES_ATIVOS = False
            PACIENTES_ATIVOS.clear()
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

        else:
            print("COMANDO INVALIDO")

