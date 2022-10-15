from numpy import array
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC

from auxiliar import Categoria
from constantes import METODO_DE_CLASSIFICACAO


def __gerar_modelo_LinearRegression(dados: list, num_registros: int):
    dados = array(dados).reshape(num_registros, 4)

    X = dados[:, :3]
    y = dados[:, -1]

    return LinearRegression().fit(X, y)


def __gerar_modelo_SVM(dados: list, num_registros: int):
    dados = array(dados).reshape(num_registros, 4)

    X = dados[:, :3]
    y = dados[:, -1]

    return SVC().fit(X, y)


def __gerar_modelo_kmeans(dados: list): return KMeans(n_clusters=5).fit(dados)


def classificar(medicao: list) -> Categoria:
    if METODO_DE_CLASSIFICACAO == "LN":
        return Categoria(5)

    elif METODO_DE_CLASSIFICACAO == "K":
        return Categoria(5)

    elif METODO_DE_CLASSIFICACAO == "SVM":
        return Categoria(5)

    else:
        return arvore_de_decisao(medicao)


def arvore_de_decisao(medicao: list) -> Categoria:
    return Categoria(5)
