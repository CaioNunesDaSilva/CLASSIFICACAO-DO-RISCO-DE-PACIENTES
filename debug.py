# Utilizar para testes, nao manter no codigo final

from random import randint
from numpy import ndarray
from numpy import array
from time import sleep


def debug(x):
    print(x)
    print(type(x))


def __simular_latencia(n: int):
    sleep(randint(0, n))


def simular_conexao_arduino():
    __simular_latencia(120)
    return gerar_sinais_vitais(), randint(0, 9999)


def simular_acesso_db(dados):
    __simular_latencia(30)
    return True


def simular_categorizacao_IA(dados):
    __simular_latencia(60)
    return True


def gerar_sinais_vitais(risco=False) -> ndarray:
    temp = randint(300, 400)

    bpm = randint(0, 200)

    oxigenacao = randint(0, 100)

    if risco:
        risco_paciente = 0
        risco_paciente = risco_paciente + (100 - oxigenacao)

        if bpm > 90:
            risco_paciente = risco_paciente + (bpm - 90)
        elif bpm < 70:
            risco_paciente = risco_paciente + (70 - bpm)

        if temp > 372:
            risco_paciente = risco_paciente + (temp - 372)
        elif temp < 362:
            risco_paciente = risco_paciente + (362 - temp)

        temp = float(temp / 10)
        return array([temp, bpm, oxigenacao, risco_paciente])

    temp = float(temp / 10)
    return array([temp, bpm, oxigenacao])
