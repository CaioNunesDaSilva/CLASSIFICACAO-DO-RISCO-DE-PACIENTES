import sklearn.linear_model as skl
from numpy import ndarray


def gerar_modelo_LinearRegression(dados: ndarray, num_registros: int):
    dados = dados.reshape(num_registros, 4)

    x_train = dados[:, :3]
    y_train = dados[:, -1]

    return skl.LinearRegression().fit(x_train, y_train)
