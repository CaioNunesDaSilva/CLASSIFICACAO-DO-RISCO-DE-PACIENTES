try:
    from tkinter import Tk, Button, Label
    from tkinter.messagebox import showinfo, showerror

    from random import randint
    from socket import socket, AF_INET, SOCK_STREAM
    from sys import exit
    from threading import Thread
    from time import sleep

    from _socket import gaierror
    from mysql.connector.errors import ProgrammingError, DatabaseError
    from numpy import array, ndarray

    from IA import criar
    from auxiliar import codificar, descodificar, Requisicao, gerar_temp, gerar_oxi, gerar_bpm
    from constantes import TAXA_ATUALIZACAO_ARDUINO, SOCKET_ENDERECO, SOCKET_PORTA, BUFFER, \
        NUMERO_DE_MEDICOES_MINIMAS_DB, NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO
    from db import get_pacientes_ativos_db, inserir_risco_medicao, get_n_medicoes_pacientes_ativos, \
        get_all_medicoes_pacientes_ativos, get_all_medicoes_nao_classificadas, get_all_medicoes, inserir_medicao

except ModuleNotFoundError as error:
    try:
        showerror("detectada falha na importacao de modulos utilizados", error)
        exit(1)
    except NameError:
        print("problema na iniciacao do Servidor")
        print("detectada falha na importacao de modulos utilizados")
        input(error)
        exit(1)


def checagem_pacientes_ativos():
    while CHECAR_PACIENTES_ATIVOS:

        pacientes_ativos_db = get_pacientes_ativos_db()

        for paciente in pacientes_ativos_db:
            if paciente not in PACIENTES_ATIVOS:
                PACIENTES_ATIVOS.append(paciente)
                Thread(target=analisar_medicoes, args=(paciente,)).start()

        for paciente in PACIENTES_ATIVOS:
            if paciente not in pacientes_ativos_db:
                PACIENTES_ATIVOS.remove(paciente)

        sleep(TAXA_ATUALIZACAO_ARDUINO)


def analisar_medicoes(paciente: int):
    global lb_oxi
    global lb_bpm
    global lb_temp
    global lb_risco

    while paciente in PACIENTES_ATIVOS:
        medicoes = get_all_medicoes_nao_classificadas(paciente)

        for medicao in medicoes:
            risco = IA.predict(array(medicao[1:]).reshape(1, -1))
            if isinstance(risco, ndarray):
                risco = risco[0]
                inserir_risco_medicao(medicao[0], risco)
            else:
                inserir_risco_medicao(medicao[0], risco.to_int())

            try:
                lb_oxi.config(text="Oxigenacao: {}%".format(medicao[1]))
                lb_bpm.config(text="BPM: {}".format(medicao[2]))
                lb_temp.config(text="temperatura: {}C".format(medicao[3]))
                lb_risco.config(text="risco nivel {}".format(risco.value))
            except Exception as error:
                lb_oxi.config(text="N/A")
                lb_bpm.config(text="N/A")
                lb_temp.config(text="N/A")
                lb_risco.config(text="N/A")

        sleep(TAXA_ATUALIZACAO_ARDUINO)


def conexao_sistema_medico(conexao, endereco):
    while CONEXAO_SISTEMA_MEDICO:
        requisicao = descodificar(conexao.recv(BUFFER), Requisicao)

        if requisicao == Requisicao.DESCONECTAR:
            break

        elif requisicao == Requisicao.PROXIMO_PACIENTE:
            try:
                medicoes_pacientes = get_n_medicoes_pacientes_ativos()

                arriscado = 6*NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO
                pacienteID = 0
                for pacientes in medicoes_pacientes:
                    if pacientes:
                        risco_geral = 0
                        paciente = 0
                        for medicao in pacientes:
                            risco_geral += medicao[2]
                            paciente = medicao[-1]
                        if risco_geral < arriscado:
                            arriscado = risco_geral
                            pacienteID = paciente

                if not pacienteID == 0 and not arriscado == 6*NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO:
                    conexao.send(codificar([pacienteID, arriscado/NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO]))
                else:
                    conexao.send(codificar([]))

            except TypeError as error:
                try:
                    showerror("medicao invalida", "paciente: {}\nmedicao: {}\n{}".format(paciente, medicao, error))
                except Exception:
                    showerror("medicao invalida", error)

            except IndexError as error:
                try:
                    showerror("medicao invalida", "paciente: {}\nmedicao: {}\n{}".format(paciente, medicao, error))
                except Exception:
                    showerror("medicao invalida", error)

        elif requisicao == Requisicao.PACIENTES_EMERGENCIA:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=1)))

        elif requisicao == Requisicao.PACIENTES_MUITO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=2)))

        elif requisicao == Requisicao.PACIENTES_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=3)))

        elif requisicao == Requisicao.PACIENTES_POUCO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=4)))

        elif requisicao == Requisicao.PACIENTES_NAO_URGENTE:
            conexao.send(codificar(get_all_medicoes_pacientes_ativos(risco=5)))

        else:
            break


def sair():
    global CHECAR_PACIENTES_ATIVOS
    global CONEXAO_SISTEMA_MEDICO
    global PACIENTES_ATIVOS
    global soquete
    CHECAR_PACIENTES_ATIVOS = False
    CONEXAO_SISTEMA_MEDICO = False
    PACIENTES_ATIVOS.clear()
    soquete.close()
    exit(0)


def fechar_paciente():
    global CHECAR_PACIENTES_ATIVOS
    global PACIENTES_ATIVOS
    CHECAR_PACIENTES_ATIVOS = False
    PACIENTES_ATIVOS.clear()


def abrir_paciente():
    global CHECAR_PACIENTES_ATIVOS
    if not CHECAR_PACIENTES_ATIVOS:
        CHECAR_PACIENTES_ATIVOS = True
        Thread(target=checagem_pacientes_ativos).start()


def listar_pacientes():
    global PACIENTES_ATIVOS
    lista = ""
    for id_paciente in PACIENTES_ATIVOS:
        lista = lista + "id: {}\n".format(id_paciente)
    showinfo(message=lista)


def fechar_medico():
    global CONEXAO_SISTEMA_MEDICO
    global soquete
    CONEXAO_SISTEMA_MEDICO = False
    soquete.close()


def abrir_medico():
    global CONEXAO_SISTEMA_MEDICO
    global soquete
    CONEXAO_SISTEMA_MEDICO = True
    soquete = socket(AF_INET, SOCK_STREAM)
    soquete.bind((SOCKET_ENDERECO, SOCKET_PORTA))
    soquete.settimeout(10)
    soquete.listen()


def conectar_medico():
    try:
        conexao, endereco = soquete.accept()
        Thread(target=conexao_sistema_medico, args=(conexao, endereco)).start()
        showinfo(message=" SISTEMA MEDICO CONECTADO NO ENDERECO:{}, PORTA:{}".format(SOCKET_ENDERECO, SOCKET_PORTA))

    except Exception as error:
        showerror(title=error, message="nenhum sistema medico encontrado")


def analisar_riscos():
    global IA
    for medicao in get_all_medicoes_nao_classificadas():
        risco = IA.predict(array(medicao[1:]).reshape(1, -1))
        inserir_risco_medicao(medicao[0], risco.to_int())


def retreinar_ia():
    global CHECAR_PACIENTES_ATIVOS
    global PACIENTES_ATIVOS
    global IA
    CHECAR_PACIENTES_ATIVOS = False
    PACIENTES_ATIVOS.clear()
    IA = criar()
    CHECAR_PACIENTES_ATIVOS = True
    Thread(target=checagem_pacientes_ativos).start()


if __name__ == "__main__":
    try:
        if len(get_all_medicoes()) < NUMERO_DE_MEDICOES_MINIMAS_DB:
            showinfo(message="POUCOS VALORES NO BANCO DE DADOS PARA TREINAMENTO DA IA,"
                             "INSERINDO {} NOVOS VALORES...".format(NUMERO_DE_MEDICOES_MINIMAS_DB))
            for x in range(NUMERO_DE_MEDICOES_MINIMAS_DB):
                risco = randint(1, 5)
                inserir_medicao(1, gerar_oxi(risco), gerar_bpm(risco), gerar_temp(risco), risco)

        IA = criar()

        CONEXAO_SISTEMA_MEDICO = True
        soquete = socket(AF_INET, SOCK_STREAM)
        soquete.bind((SOCKET_ENDERECO, SOCKET_PORTA))
        soquete.settimeout(10)
        soquete.listen()

        PACIENTES_ATIVOS = []
        CHECAR_PACIENTES_ATIVOS = True
        Thread(target=checagem_pacientes_ativos).start()

    except ProgrammingError as error:
        showerror("problema na iniciacao do servidor", "detectada falha com o banco de dados\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except DatabaseError as error:
        showerror("problema na iniciacao do servidor", "detectada falha com o banco de dados\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except ValueError as error:
        showerror("problema na iniciacao do servidor", "problema no treinamento da IA\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except gaierror as error:
        showerror("problema na iniciacao do servidor", "problema na definicao do endereco do soquete\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except TypeError as error:
        showerror("problema na iniciacao do servidor", "problema com valor da porta do soquete\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except OverflowError as error:
        showerror("problema na iniciacao do servidor", "problema com valor da porta do soquete\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    except Exception as error:
        showerror("problema na iniciacao do servidor", "Erro inesperado\n{}".format(error))
        try:
            CHECAR_PACIENTES_ATIVOS = False
            CONEXAO_SISTEMA_MEDICO = False
        except Exception as e:
            exit(1)
        exit(1)

    janela = Tk()
    janela.title("Servidor")
    janela.protocol("WM_DELETE_WINDOW", sair)

    med_txt = Label(janela, text="ultima medicao clasificada")
    med_txt.grid(column=1, row=0)

    lb_oxi = Label(janela, text="N/A")
    lb_oxi.grid(column=0, row=1)
    lb_bpm = Label(janela, text="N/A")
    lb_bpm.grid(column=1, row=1)
    lb_temp = Label(janela, text="N/A")
    lb_temp.grid(column=2, row=1)
    lb_risco = Label(janela, text="N/A")
    lb_risco.grid(column=1, row=2)

    btn_fechar_pacientes = Button(janela, text="Parar classificacao", command=fechar_paciente)
    btn_fechar_pacientes.grid(column=0, row=3)
    btn_abrir_pacientes = Button(janela, text="retomar classificacao", command=abrir_paciente)
    btn_abrir_pacientes.grid(column=1, row=3)
    btn_listar_pacientes = Button(janela, text="lista de pacientes ativos", command=listar_pacientes)
    btn_listar_pacientes.grid(column=2, row=3)
    btn_fechar_medico = Button(janela, text="fechar socket do sistema medico", command=fechar_medico)
    btn_fechar_medico.grid(column=0, row=4)
    btn_abrir_medico = Button(janela, text="abrir socket do sistema medico", command=abrir_medico)
    btn_abrir_medico.grid(column=1, row=4)
    btn_conectar_medico = Button(janela, text="aceitar conexao do sistema medico", command=conectar_medico)
    btn_conectar_medico.grid(column=2, row=4)
    btn_analisar_riscos = Button(janela, text="analisar riscos pendentes", command=analisar_riscos)
    btn_analisar_riscos.grid(column=0, row=5)
    btn_retreinar_ia = Button(janela, text="retreinar inteligencia artificial", command=retreinar_ia)
    btn_retreinar_ia.grid(column=2, row=5)

    janela.mainloop()
