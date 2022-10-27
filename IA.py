from numpy import array
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC

from constantes import METODO_DE_CLASSIFICACAO
from auxiliar import ModeloRegressaoLinear
from db import get_all_medicoes_nao_classificadas, get_all_medicoes, corretivo_medicoes_nao_classificadas


def __gerar_modelo_linear_regression(dados: list, num_registros: int):
    dados = array(dados).reshape(num_registros, 4)

    X = dados[:, :3]
    y = dados[:, -1]

    return LinearRegression().fit(X, y)


def __gerar_modelo_svm(dados: list, num_registros: int):
    dados = array(dados).reshape(num_registros, 4)

    X = dados[:, :3]
    y = dados[:, -1]

    return SVC().fit(X, y)


def criar():
    if get_all_medicoes_nao_classificadas():
        corretivo_medicoes_nao_classificadas()

    if METODO_DE_CLASSIFICACAO == "LN":
        medicoes = get_all_medicoes()
        return ModeloRegressaoLinear(__gerar_modelo_linear_regression(medicoes, len(medicoes)))

    elif METODO_DE_CLASSIFICACAO == "SVM":
        medicoes = get_all_medicoes()
        return __gerar_modelo_svm(medicoes, len(medicoes))

    else:
        raise Exception("MODELO INVALIDO")
