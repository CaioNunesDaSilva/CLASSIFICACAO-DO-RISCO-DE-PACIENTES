from datetime import datetime
from enum import Enum
from json import dumps, loads
from random import randint, uniform


class ModeloRegressaoLinear:
    def __init__(self, modelo):
        self.modelo = modelo

    def predict(self, dado):
        dado = self.modelo.predict(dado)
        dado = int(round(dado[0], 0))
        if dado > 0:
            return Categoria(dado)
        return Categoria(1)


class Categoria(Enum):
    EMERGENCIA = 1
    MUITO_URGENTE = 2
    URGENTE = 3
    POUCO_URGENTE = 4
    NAO_URGENTE = 5

    def to_json(self) -> str:
        return str(self.value)

    def to_int(self) -> int:
        return int(self.value)

    @classmethod
    def from_str(cls, string: str) -> 'Categoria':
        return cls(int(string))


class Requisicao(Enum):
    PROXIMO_PACIENTE = 0
    PACIENTES_EMERGENCIA = 1
    PACIENTES_MUITO_URGENTE = 2
    PACIENTES_URGENTE = 3
    PACIENTES_POUCO_URGENTE = 4
    PACIENTES_NAO_URGENTE = 5
    DESCONECTAR = 6

    def to_json(self) -> str:
        return str(self.value)

    @classmethod
    def from_str(cls, string: str) -> 'Requisicao':
        return cls(int(string))


def codificar(dados) -> bytes:
    if isinstance(dados, bytes):
        return dados

    if isinstance(dados, list):
        for x in range(len(dados)):
            if isinstance(dados[x], datetime):
                dados[x] = dados[x].isoformat()
            if isinstance(dados[x], tuple):
                lista = []
                for n in dados[x]:
                    lista.append(n)
                dados[x] = lista
            if isinstance(dados[x], list):
                for y in range(len(dados[x])):
                    if isinstance(dados[x][y], datetime):
                        dados[x][y] = dados[x][y].isoformat()
                    if isinstance(dados[x][y], tuple):
                        lista = []
                        for n in dados[x][y]:
                            lista.append(n)
                        dados[x][y] = lista
                    if isinstance(dados[x][y], list):
                        for z in range(len(dados[x][y])):
                            if isinstance(dados[x][y][z], datetime):
                                dados[x][y][z] = dados[x][y][z].isoformat()

        dados = dumps(dados)
        return dados.encode()

    return dados.to_json().encode()


def descodificar(dados, classe):
    if isinstance(dados, bytes):
        dados = dados.decode()

    if dados is None:
        return None

    elif classe == Categoria:
        return Categoria.from_str(dados)

    elif classe == Requisicao:
        return Requisicao.from_str(dados)

    elif classe == "LISTA":
        return loads(dados)


def gerar_oxi(nv_risco_alvo: int) -> int:
    if nv_risco_alvo == 5:
        return randint(96, 100)

    elif nv_risco_alvo == 4:
        return randint(93, 95)

    elif nv_risco_alvo == 3:
        return randint(90, 92)

    elif nv_risco_alvo == 2:
        return randint(87, 89)

    elif nv_risco_alvo == 1:
        return randint(0, 86)


def gerar_bpm(nv_risco_alvo: int) -> int:
    n = randint(0, 1)

    if nv_risco_alvo == 5:
        return randint(80, 110)

    elif nv_risco_alvo == 4:
        if n:
            return randint(111, 130)
        else:
            return randint(60, 79)

    elif nv_risco_alvo == 3:
        if n:
            return randint(131, 140)
        else:
            return randint(50, 59)

    elif nv_risco_alvo == 2:
        if n:
            return randint(141, 160)
        else:
            return randint(50, 69)

    elif nv_risco_alvo == 1:
        if n:
            return randint(161, 220)
        else:
            return randint(0, 49)


def gerar_temp(nv_risco_alvo: int) -> float:
    n = randint(0, 1)

    if nv_risco_alvo == 5:
        return uniform(36.5, 37.5)

    elif nv_risco_alvo == 4:
        if n:
            return uniform(37.6, 38.0)
        else:
            return uniform(36.0, 36.4)

    elif nv_risco_alvo == 3:
        if n:
            return uniform(38.1, 38.4)
        else:
            return uniform(35.6, 35.9)

    elif nv_risco_alvo == 2:
        if n:
            return uniform(38.5, 38.9)
        else:
            return uniform(35.1, 35.5)

    elif nv_risco_alvo == 1:
        if n:
            return uniform(39.0, 42.0)
        else:
            return uniform(32.0, 35.0)
