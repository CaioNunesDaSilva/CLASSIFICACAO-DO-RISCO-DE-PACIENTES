from datetime import datetime

import mysql.connector as mysql

from constantes import BANCO_DE_DADOS_ENDERECO, BANCO_DE_DADOS_NOME, BANCO_DE_DADOS_USUARIO, BANCO_DE_DADOS_SENHA, \
    NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO


def __conectar(host=BANCO_DE_DADOS_ENDERECO, database=BANCO_DE_DADOS_NOME,
               user=BANCO_DE_DADOS_USUARIO, password=BANCO_DE_DADOS_SENHA) -> mysql.MySQLConnection:
    conexao = mysql.connect(host=host, database=database, user=user, password=password)
    if conexao.is_connected():
        return conexao


def __select(conexao: mysql.MySQLConnection, campos: str, tabela: str, condicao=None, desempacotar=False) -> list:
    cursor = conexao.cursor()
    if condicao:
        cursor.execute(f"SELECT {campos} FROM {tabela} WHERE {condicao};")
    else:
        cursor.execute(f"SELECT {campos} FROM {tabela};")
    selecao = cursor.fetchall()

    if isinstance(selecao, tuple):
        lista = []
        for linha in selecao:
            lista.append(linha)
        selecao = lista

    for indice, linha in enumerate(selecao):
        if isinstance(linha, tuple):
            if len(linha) < 1:
                selecao.pop(indice)
            elif len(linha) == 1:
                selecao[indice] = linha[0]

    if selecao and desempacotar:
        if len(selecao) == 1 and isinstance(selecao[0], tuple):
            lista = []
            for celula in selecao[0]:
                lista.append(celula)
            selecao = lista

    return selecao


def __insert(conexao: mysql.MySQLConnection, tabela_campos: str, valores):
    cursor = conexao.cursor()
    if isinstance(valores, tuple):
        cursor.execute(f"INSERT INTO {tabela_campos} VALUES {valores};")
    else:
        cursor.execute(f"INSERT INTO {tabela_campos} VALUES ({valores});")


def __update(conexao: mysql.MySQLConnection, tabela: str, coluna_valor: str, condicao: str):
    cursor = conexao.cursor()
    cursor.execute(f"UPDATE {tabela} SET {coluna_valor} WHERE {condicao};")


def __delete(conexao: mysql.MySQLConnection, tabela: str, condicao: str):
    cursor = conexao.cursor()
    cursor.execute(f"DELETE FROM {tabela} WHERE {condicao};")


def __desconectar(conexao: mysql.MySQLConnection, rollback=False):
    if rollback:
        conexao.rollback()
    else:
        conexao.commit()
    conexao.close()


def get_pacientes_ativos_db() -> list:
    conexao = __conectar()
    pacientes = __select(conexao, "idPaciente", "paciente", "isAtivo = 1")
    __desconectar(conexao)
    return pacientes


def get_all_medicoes_nao_classificadas(paciente=0) -> list:
    conexao = __conectar()
    if paciente:
        medicoes = __select(conexao, "idMedicao, numOxi, numBpm, numTemp", "medicoes",
                            "idPaciente = {} AND risco IS NULL".format(paciente))
    else:
        medicoes = __select(conexao, "idMedicao, numOxi, numBpm, numTemp", "medicoes", "risco IS NULL")
    __desconectar(conexao)
    return medicoes


def inserir_risco_medicao(medicao: int, risco: int):
    conexao = __conectar()
    __update(conexao, "medicoes", "risco = {}".format(risco), "idMedicao = {}".format(medicao))
    __desconectar(conexao)


def ativar_paciente_medidor_virtual(id_medidor: int):
    conexao = __conectar()
    __insert(conexao, "paciente (idEquipamento, isAtivo)", "{}, 1".format(id_medidor))
    __desconectar(conexao)


def get_paciente_medidor_virtual(id_medidor: int) -> list:
    conexao = __conectar()
    paciente = __select(conexao, "idPaciente", "paciente",
                        "idEquipamento = {} AND isAtivo = 1".format(id_medidor), desempacotar=True)
    __desconectar(conexao)
    return paciente


def inserir_medicao(id_paciente: int, oxi: float, bpm: int, temp: float, risco=None):
    conexao = __conectar()
    if risco:
        __insert(conexao, "medicoes (idPaciente, numOxi, numBpm, numTemp, risco)",
                 "{}, {}, {}, {}, {}".format(id_paciente, oxi, bpm, temp, risco))
    else:
        __insert(conexao, "medicoes (idPaciente, numOxi, numBpm, numTemp)",
                 "{}, {}, {}, {}".format(id_paciente, oxi, bpm, temp))
    __desconectar(conexao)


def desativar_paciente_medidor_virtual(id_medidor: int):
    conexao = __conectar()
    __update(conexao, "paciente", "isAtivo = 0", "idEquipamento = {} AND isAtivo = 1".format(id_medidor))
    __desconectar(conexao)


def get_n_medicoes_pacientes_ativos(n_medicoes=NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO) -> list:
    ativos = get_pacientes_ativos_db()
    conexao = __conectar()

    pacientes = []
    for paciente in ativos:
        date = datetime.now()
        medicoes = []
        for x in range(n_medicoes):
            medicao = __select(conexao, "idMedicao, MAX(dtMedicao), risco", "medicoes",
                               "idPaciente = {} AND dtMedicao < '{}'".format(paciente, date), desempacotar=True)
            date = medicao[1]
            medicoes.append(medicao)
        pacientes.append(medicoes)
    __desconectar(conexao)
    return pacientes


def get_all_medicoes_pacientes_ativos(risco=0) -> list:
    ativos = get_pacientes_ativos_db()
    conexao = __conectar()

    pacientes = []
    for paciente in ativos:
        if risco:
            medicoes = __select(conexao, "idPaciente, dtMedicao, risco", "medicoes",
                                "idPaciente = {} AND risco = {}".format(paciente, risco))
        else:
            medicoes = __select(conexao, "idPaciente, dtMedicao, risco", "medicoes", "idPaciente = {}".format(paciente))

        pacientes.append(medicoes)
    __desconectar(conexao)
    return pacientes


def get_all_medicoes():
    conexao = __conectar()
    medicoes = __select(conexao, "numOxi, numBpm, numTemp, risco", "medicoes")
    __desconectar(conexao)
    return medicoes


def corretivo_medicoes_nao_classificadas():
    medicoes = get_all_medicoes_nao_classificadas()
    conexao = __conectar()
    for x in medicoes:
        __delete(conexao, "medicoes", "idMedicao = {}".format(x[0]))
    __desconectar(conexao)
