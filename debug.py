# Utilizar para testes, nao manter no codigo final

from random import randint

from auxiliar import Categoria


def debug(x):
    print(x)
    print(type(x))


def gerar_sinais_vitais(risco=False, risco_as_int=True) -> list:
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

        if risco_paciente < 25:
            categoria = Categoria(5)
        elif risco_paciente < 50:
            categoria = Categoria(4)
        elif risco_paciente < 75:
            categoria = Categoria(3)
        elif risco_paciente < 100:
            categoria = Categoria(2)
        else:
            categoria = Categoria(1)

        if risco_as_int:
            return [temp, bpm, oxigenacao, categoria.value]
        return [temp, bpm, oxigenacao, categoria]

    temp = float(temp / 10)
    return [temp, bpm, oxigenacao]
