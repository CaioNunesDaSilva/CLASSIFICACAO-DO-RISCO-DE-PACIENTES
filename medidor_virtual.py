from sys import exit
from time import sleep
from threading import Thread
from random import randint, random

from db import ativar_paciente_medidor_virtual, get_paciente_medidor_virtual,\
    inserir_medicao_medidor_virtual, desativar_paciente_medidor_virtual

from constantes import TAXA_ATUALIZACAO_ARDUINO


def enviar_medicoes():
    while MEDIR:
        inserir_medicao_medidor_virtual(id_paciente[0], gerar_oxi(), gerar_BPM(), float(f'{gerar_temp():.2f}'))
        sleep(TAXA_ATUALIZACAO_ARDUINO)


def novo_paciente() -> int:
    if get_paciente_medidor_virtual(id_dispositivo):
        desativar_paciente_medidor_virtual(id_dispositivo)

    print("CONECTANDO NOVO PACIENTE, AGUARDE...")
    sleep(TAXA_ATUALIZACAO_ARDUINO)

    ativar_paciente_medidor_virtual(id_dispositivo)
    return get_paciente_medidor_virtual(id_dispositivo)


# TODO alterar metodo de geração
def gerar_oxi():
    if nv_risco_alvo == 5:
        return randint(80, 100)

    elif nv_risco_alvo == 4:
        return randint(60, 80)

    elif nv_risco_alvo == 3:
        return randint(40, 60)

    elif nv_risco_alvo == 2:
        return randint(20, 40)

    elif nv_risco_alvo == 1:
        return randint(0, 20)


# TODO alterar metodo de geração
def gerar_BPM():
    n = randint(0, 1)

    if nv_risco_alvo == 5:
        return randint(60, 80)

    elif nv_risco_alvo == 4:
        if n:
            return randint(80, 100)
        else:
            return randint(40, 60)

    elif nv_risco_alvo == 3:
        if n:
            return randint(100, 120)
        else:
            return randint(20, 40)

    elif nv_risco_alvo == 2:
        if n:
            return randint(120, 140)
        else:
            return randint(10, 20)

    elif nv_risco_alvo == 1:
        if n:
            return randint(140, 160)
        else:
            return randint(0, 10)


# TODO alterar metodo de geração
def gerar_temp():
    n = randint(0, 1)

    if nv_risco_alvo == 5:
        return 37 + (random()/2)

    elif nv_risco_alvo == 4:
        return 37 + random()

    elif nv_risco_alvo == 3:
        if n:
            return 38 + random()
        else:
            return 36 + random()

    elif nv_risco_alvo == 2:
        if n:
            return 39 + random()
        else:
            return 35 + random()

    elif nv_risco_alvo == 1:
        if n:
            return 40 + random()
        else:
            return 34 + random()


if __name__ == "__main__":
    id_dispositivo = randint(1000, 9999)
    id_paciente = novo_paciente()

    MEDIR = True
    nv_risco_alvo = 5

    Thread(target=enviar_medicoes).start()

    while True:
        comando = input("MEDIDOR VIRTUAL ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            MEDIR = False
            desativar_paciente_medidor_virtual(id_dispositivo)
            exit(0)

        elif comando.upper() == "DIMINUIR RISCO ALVO":
            if nv_risco_alvo > 1:
                nv_risco_alvo -= 1
            print("NIVEL DE RISCO ALVO ATUAL: {}".format(nv_risco_alvo))

        elif comando.upper() == "AUMENTAR RISCO ALVO":
            if nv_risco_alvo < 5:
                nv_risco_alvo += 1
            print("NIVEL DE RISCO ALVO ATUAL: {}".format(nv_risco_alvo))

        elif comando.upper() == "NOVO PACIENTE":
            MEDIR = False
            sleep(TAXA_ATUALIZACAO_ARDUINO)
            id_paciente = novo_paciente()
            # noinspection PyRedeclaration
            MEDIR = True
            Thread(target=enviar_medicoes).start()

        else:
            print("COMANDO INVALIDO")
