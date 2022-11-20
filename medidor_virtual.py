try:
    from random import randint
    from sys import exit
    from threading import Thread
    from time import sleep

    from auxiliar import gerar_oxi, gerar_bpm, gerar_temp
    from constantes import TAXA_ATUALIZACAO_ARDUINO
    from db import ativar_paciente_medidor_virtual, get_paciente_medidor_virtual, \
        inserir_medicao, desativar_paciente_medidor_virtual

except ModuleNotFoundError as error:
    print("problema na iniciacao do Medidor Virtual")
    print("detectada falha na importacao de modulos utilizados")
    input(error)
    exit(-1)


def enviar_medicoes():
    while MEDIR:
        inserir_medicao(id_paciente, gerar_oxi(nv_risco_alvo), gerar_bpm(nv_risco_alvo),
                        float(f'{gerar_temp(nv_risco_alvo):.2f}'))
        sleep(TAXA_ATUALIZACAO_ARDUINO)


def novo_paciente() -> int:
    if get_paciente_medidor_virtual(id_dispositivo):
        desativar_paciente_medidor_virtual(id_dispositivo)

    print("CONECTANDO NOVO PACIENTE, AGUARDE...")
    sleep(TAXA_ATUALIZACAO_ARDUINO)

    ativar_paciente_medidor_virtual(id_dispositivo)
    return get_paciente_medidor_virtual(id_dispositivo)[0]


if __name__ == "__main__":
    print("MEDIDOR VIRTUAL INICIANDO...")

    id_dispositivo = randint(1000, 9999)
    id_paciente = novo_paciente()

    MEDIR = True
    nv_risco_alvo = 5

    Thread(target=enviar_medicoes).start()

    print("MEDIDOR VIRTUAL INICIADO")
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
