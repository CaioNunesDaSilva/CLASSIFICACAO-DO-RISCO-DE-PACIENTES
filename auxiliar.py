from enum import Enum


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
