try:
    from tkinter import Tk, Button, Label
    from tkinter.messagebox import showinfo, showerror

    from random import randint
    from sys import exit
    from threading import Thread
    from time import sleep
    import os

    from auxiliar import gerar_oxi, gerar_bpm, gerar_temp
    from constantes import TAXA_ATUALIZACAO_ARDUINO
    from db import ativar_paciente_medidor_virtual, get_paciente_medidor_virtual, \
        inserir_medicao, desativar_paciente_medidor_virtual

except ModuleNotFoundError as error:
    try:
        showerror(error, "detectada falha na importacao de modulos utilizados")
        exit(1)
    except NameError as n_error:
        print("problema na iniciacao do Medidor Virtual")
        print("detectada falha na importacao de modulos utilizados")
        input(error)
        exit(1)


def enviar_medicoes():
    try:
        global ult_med
        while MEDIR:
            oxi = gerar_oxi(nv_risco_alvo)
            bpm = gerar_bpm(nv_risco_alvo)
            temp = float(f'{gerar_temp(nv_risco_alvo):.2f}')
            inserir_medicao(id_paciente, oxi, bpm, temp)

            ult_med.config(text="Ultima medicao enviada - Temp:{} BPM:{} Oxi:{}".format(temp, bpm, oxi))

            sleep(TAXA_ATUALIZACAO_ARDUINO)

    except Exception as error:
        showerror("erro econtrado ao enviar medicao", error)
        os._exit(1)


def novo_paciente() -> int:
    if get_paciente_medidor_virtual(id_dispositivo):
        desativar_paciente_medidor_virtual(id_dispositivo)

    sleep(TAXA_ATUALIZACAO_ARDUINO + 2)

    ativar_paciente_medidor_virtual(id_dispositivo)
    return get_paciente_medidor_virtual(id_dispositivo)[0]


def diminuir_risco_alvo():
    global nv_risco_alvo
    global nv_atual
    if nv_risco_alvo > 1:
        nv_risco_alvo -= 1
    nv_atual.config(text="Nivel de risco alvo: {}".format(nv_risco_alvo))


def aumentar_risco_alvo():
    global nv_risco_alvo
    global nv_atual
    if nv_risco_alvo < 5:
        nv_risco_alvo += 1
    nv_atual.config(text="Nivel de risco alvo: {}".format(nv_risco_alvo))


def conectar_novo_paciente():
    global MEDIR
    global id_paciente
    MEDIR = False
    showinfo(message="Conectando novo paciente, aguarde em torno de {} segundos".format(TAXA_ATUALIZACAO_ARDUINO))
    id_paciente = novo_paciente()
    MEDIR = True
    Thread(target=enviar_medicoes).start()


def sair():
    global MEDIR
    global id_dispositivo
    MEDIR = False
    desativar_paciente_medidor_virtual(id_dispositivo)
    exit(0)


if __name__ == "__main__":
    try:
        id_dispositivo = randint(1000, 9999)
        id_paciente = novo_paciente()

        MEDIR = True
        nv_risco_alvo = 5

        Thread(target=enviar_medicoes).start()

    except Exception as error:
        showerror("erro na inicializacao do medidor virtual", error)
        exit(1)

    try:
        janela = Tk()
        janela.title("MEDIDOR VIRTUAL")
        janela.protocol("WM_DELETE_WINDOW", sair)

        nv_atual = Label(janela, text="Nivel de risco alvo: {}".format(nv_risco_alvo))
        nv_atual.grid(column=1, row=0)

        ult_med = Label(janela, text="Ultima medicao enviada - Temp:N/A BPM:N/A Oxi:N/A")
        ult_med.grid(column=1, row=1)

        amt_nv_atual = Button(janela, text="Aumentar nivel de risco alvo", command=aumentar_risco_alvo)
        amt_nv_atual.grid(column=0, row=2)

        nv_paciente = Button(janela, text="Conectar novo paciente", command=conectar_novo_paciente)
        nv_paciente.grid(column=1, row=2)

        dmr_nv_atual = Button(janela, text="Diminuir nivel de risco alvo", command=diminuir_risco_alvo)
        dmr_nv_atual.grid(column=3, row=2)

        janela.mainloop()

    except Exception as error:
        showerror("erro na interface da aplicacao", error)

