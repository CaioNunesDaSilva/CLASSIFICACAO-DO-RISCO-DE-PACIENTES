try:
    from socket import socket, AF_INET, SOCK_STREAM
    from sys import exit

    from auxiliar import codificar, descodificar, Requisicao
    from constantes import SOCKET_ENDERECO, SOCKET_PORTA, BUFFER, NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO

except ModuleNotFoundError as error:
    print("problema na iniciacao do Sistema Medico")
    print("detectada falha na importacao de modulos utilizados")
    input(error)
    exit(-1)


def __print_pacientes_riscos(pacientes: list):
    print("PACIENTES DE RISCO:")
    for paciente in pacientes:
        if paciente:
            print("ID: {}".format(paciente[0][0]))
            for medicao in paciente:
                print("DATA: {}".format(medicao[1]))
                print("RISCO: {}".format(medicao[2]))
            print("\n")


if __name__ == "__main__":
    print("SISTEMA MEDICO INICIANDO...")

    CONECTADO = False
    soquete = socket(AF_INET, SOCK_STREAM)

    print("INICIANDO CONEXAO")
    while not CONECTADO:
        try:
            soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))
            CONECTADO = True
            print("SISTEMA MEDICO CONECTADO")

        except:
            print("ERRO DE CONEXAO, TENTANDO NOVAMENTE")

    while True:
        comando = input("SISTEMA MEDICO ACEITANDO COMANDOS...\n")

        if comando.upper() == "SAIR":
            soquete.send(codificar(Requisicao(6)))
            soquete.close()
            exit(0)

        elif comando.upper() == "DESCONECTAR":
            soquete.send(codificar(Requisicao(6)))
            soquete.close()
            print("DESCONECTADO DO SERVIDOR")

        elif comando.upper() == "CONECTAR":
            soquete = socket(AF_INET, SOCK_STREAM)
            soquete.connect((SOCKET_ENDERECO, SOCKET_PORTA))
            print("CONEXAO REQUISITADA")

        elif comando.upper() == "PROXIMO PACIENTE":
            soquete.send(codificar(Requisicao(0)))
            print("BUSCANDO PACIENTE, AGUARDE...")
            paciente = descodificar(soquete.recv(BUFFER), "LISTA")
            if paciente:
                print("PROXIMO PACIENTE,"
                      " COM BASE NAS ULTIMAS {} MEDICOES:".format(NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO))
                print("ID: {}".format(paciente[0]))
                print("RISCO MEDIO: {}".format(paciente[1] / NUMERO_DE_MEDICOES_PARA_DETERMINAR_RISCO))
            else:
                print("DADOS OU PACIENTES INSUFICIENTES PARA CATEGORIZACAO, AGUARDE OU CONECTE NOVOS MEDIDORES...")

        elif comando.upper() == "LISTAR MEDICOES EMERGENCIA":
            soquete.send(codificar(Requisicao(1)))
            print("BUSCANDO MEDICOES DE RISCO EMERGENCIA NOS PACIENTES ATIVOS, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR MEDICOES MUITO URGENTE":
            soquete.send(codificar(Requisicao(2)))
            print("BUSCANDO MEDICOES DE RISCO MUITO URGENTE NOS PACIENTES ATIVOS, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR MEDICOES URGENTE":
            soquete.send(codificar(Requisicao(3)))
            print("BUSCANDO MEDICOES DE RISCO URGENTE NOS PACIENTES ATIVOS, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR MEDICOES POUCO URGENTE":
            soquete.send(codificar(Requisicao(4)))
            print("BUSCANDO MEDICOES DE RISCO POUCO URGENTE NOS PACIENTES ATIVOS, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        elif comando.upper() == "LISTAR MEDICOES NAO URGENTE":
            soquete.send(codificar(Requisicao(5)))
            print("BUSCANDO MEDICOES DE RISCO NAO URGENTE NOS PACIENTES ATIVOS, AGUARDE...")
            __print_pacientes_riscos(descodificar(soquete.recv(BUFFER), "LISTA"))

        else:
            print("COMANDO INVALIDO")
