import mysql.connector as MySQL

from constantes import BANCO_DE_DADOS_ENDERECO
from constantes import BANCO_DE_DADOS_NOME
from constantes import BANCO_DE_DADOS_USUARIO
from constantes import BANCO_DE_DADOS_SENHA


def __conectar(host=BANCO_DE_DADOS_ENDERECO, database=BANCO_DE_DADOS_NOME,
               user=BANCO_DE_DADOS_USUARIO, password=BANCO_DE_DADOS_SENHA) -> MySQL.MySQLConnection:
    conexao = MySQL.connect(host=host, database=database, user=user, password=password)
    if conexao.is_connected():
        return conexao


def __select(conexao: MySQL.MySQLConnection, campos: str, tabela: str, condicao=None, desempacotar=False) -> list:
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


def __insert(conexao: MySQL.MySQLConnection, tabela_campos: str, valores):
    cursor = conexao.cursor()
    if isinstance(valores, tuple):
        cursor.execute(f"INSERT INTO {tabela_campos} VALUES {valores};")
    else:
        cursor.execute(f"INSERT INTO {tabela_campos} VALUES ('{valores}');")


def __update(conexao: MySQL.MySQLConnection, tabela: str, coluna_valor: str, condicao: str):
    cursor = conexao.cursor()
    cursor.execute(f"UPDATE {tabela} SET {coluna_valor} WHERE {condicao};")


def __delete(conexao: MySQL.MySQLConnection, tabela: str, condicao: str):
    cursor = conexao.cursor()
    cursor.execute(f"DELETE FROM {tabela} WHERE {condicao};")


def __desconectar(conexao: MySQL.MySQLConnection, rollback=False):
    if rollback:
        conexao.rollback()
    else:
        conexao.commit()
    conexao.close()
    