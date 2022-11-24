try:
    from tkinter import Tk, Button, Label
    from tkinter.messagebox import showinfo, showerror

    from socket import socket, AF_INET, SOCK_STREAM
    from sys import exit

    from auxiliar import codificar, descodificar, Requisicao
    from constantes import SOCKET_ENDERECO, SOCKET_PORTA, BUFFER, NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO

except ModuleNotFoundError as error:
    try:
        showerror(error, "detectada falha na importacao de modulos utilizados")
        exit(1)
    except NameError as n_error:
        print("problema na iniciacao do Sistema Medico")
        print("detectada falha na importacao de modulos utilizados")
        input(error)
        exit(1)


def __pacientes_riscos(pacientes: list):
    lista = ""
    for paciente in pacientes:
        if paciente:
            lista = lista + "ID: {}\n".format(paciente[0][0])
            for medicao in paciente:
                lista = lista + "DATA: {}   ".format(medicao[1])
                lista = lista + "RISCO: {}".format(medicao[2])
                lista = lista + "\n"
            lista = lista + "\n"
    return lista


def sair():
    global soquete
    soquete.send(codificar(Requisicao(6)))
    soquete.close()
    exit(0)


def proximo_paciente():
    global lb_proximo_paciente
    soquete.send(codificar(Requisicao(0)))
    paciente = descodificar(soquete.recv(BUFFER), "LISTA")
    if paciente:
        lb_proximo_paciente.config(text="ID: {} / RISCO MEDIO: {}".format(paciente[0], paciente[1]))
    else:
        showerror(message="DADOS OU PACIENTES INSUFICIENTES PARA CATEGORIZACAO, AGUARDE OU CONECTE NOVOS MEDIDORES...")


def lista_emergencia():
    soquete.send(codificar(Requisicao(1)))
    showinfo("medicoes emergecia", __pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA")))


def lista_muito_urgente():
    soquete.send(codificar(Requisicao(2)))
    showinfo("medicoes muito urgente", __pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA")))


def lista_urgente():
    soquete.send(codificar(Requisicao(3)))
    showinfo("medicoes urgente", __pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA")))


def lista_pouco_urgente():
    soquete.send(codificar(Requisicao(4)))
    showinfo("medicoes pouco urgente", __pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA")))


def lista_nao_urgente():
    soquete.send(codificar(Requisicao(5)))
    showinfo("medicoes nao urgente", __pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA")))


if __name__ == "__main__":
    CONECTADO = False
    soquete = socket(AF_INET, SOCK_STREAM)

    while not CONECTADO:
        try:
            soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))
            CONECTADO = True
        except:
            print("ERRO DE CONEXAO, TENTANDO NOVAMENTE")

    janela = Tk()
    janela.title("Sistema Medico")
    janela.protocol("WM_DELETE_WINDOW", sair)
    showinfo("servidor encontrado", "aceite a conexao no servidor para executar comandos")

    lb_proximo_paciente = Label(janela, text="Proximo paciente: N/A")
    lb_proximo_paciente.grid(column=1, row=0)

    btn_proximo_paciente = Button(janela, text="Proximo paciente", command=proximo_paciente)
    btn_proximo_paciente.grid(column=0, row=1)
    btn_pacientes_emergencia = Button(janela, text="medicoes emergencia", command=lista_emergencia)
    btn_pacientes_emergencia.grid(column=1, row=1)
    btn_pacientes_muito_urgente = Button(janela, text="medicoes muito urgente", command=lista_muito_urgente)
    btn_pacientes_muito_urgente.grid(column=2, row=1)
    btn_pacientes_urgente = Button(janela, text="medicoes urgente", command=lista_urgente)
    btn_pacientes_urgente.grid(column=0, row=2)
    btn_pacientes_pouco_urgente = Button(janela, text="medicoes pouco urgente", command=lista_pouco_urgente)
    btn_pacientes_pouco_urgente.grid(column=1, row=2)
    btn_pacientes_nao_urgente = Button(janela, text="medicoes nao urgente", command=lista_nao_urgente)
    btn_pacientes_nao_urgente.grid(column=2, row=2)

    janela.mainloop()

