from sys import exit
from threading import Thread

from debug import simular_conexao_arduino
from debug import simular_acesso_db
from debug import simular_categorizacao_IA


def controlador_de_rede_arduino():
    while REDE_ABERTA_ARDUINO:
        conexao = simular_conexao_arduino()
        Thread(target=medir_risco, args=conexao).start()


def medir_risco(dados, ident):
    simular_categorizacao_IA(dados)
    simular_acesso_db(dados)


if __name__ == "__main__":
    REDE_ABERTA_ARDUINO = True

    thread_CRA = Thread(target=controlador_de_rede_arduino)
    thread_CRA.start()

    while True:
        comando = input("SERVIDOR ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            REDE_ABERTA_ARDUINO = False
            thread_CRA.join()
            exit(0)
            print("TERMINANDO APLICACAO, AGUARDE...")

        elif comando.upper() == "FECHAR ARDUINO":
            REDE_ABERTA_ARDUINO = False
            print("SERVIDOR FECHADO PARA CONEXOES DE ARDUINO")

        elif comando.upper() == "ABRIR ARDUINO":
            REDE_ABERTA_ARDUINO = True
            print("SERVIDOR ABERTO PARA CONEXOES DE ARDUINO")

        else:
            print("COMANDO INVALIDO")

