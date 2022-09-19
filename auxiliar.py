from random import randint
from numpy import ndarray
from numpy import array


# Utilizar somente para testes de baixa confiabilidade
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
