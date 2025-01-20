# %%

import json
import socket
import enviroment
import os
import time


def print_menu() -> None:
    print(f'{"MENU":=^30}')
    print("1. LISTAR ARQUIVOS")
    print("2. ADICIONAR ARQUIVO")
    print("3. BAIXAR ARQUIVO")
    print("4. SAIR")


def trata_nome_arquivo(nome_arquivo, dup=0):
    nome = nome_arquivo
    if dup > 0:
        nome = f"({dup}) {nome_arquivo}"
    if os.path.exists(f"local/{nome}"):
        return trata_nome_arquivo(nome_arquivo, dup + 1)
    return nome


def recebe_arquivo_do_servidor(cliente: socket.socket, nome_arquivo_final: str):
    with open(f"local/{nome_arquivo_final}", "wb") as file:
        while True:
            chunk = cliente.recv(1024)
            print("Recebeu ", chunk)
            if chunk == b"EOF":
                print(f"Arquivo {nome_arquivo_final} baixado com sucesso!")
                return
            file.write(chunk)


print("Conectando ao servidor...")
try:
    ip = str(input("Informe o IP do servidor: "))
    port = int(input("Informe a porta do servidor: "))
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip, port))
    print("Conectado com sucesso!")
except Exception as e:
    print(e.__str__())
    print("Falha ao conectar, encerrando programa")
    quit()

running = True
while running:
    print_menu()
    option = int(input("Selecione a opção desejada: "))
    match option:
        case 1:
            print()
            print(f'{"LISTAR ARQUIVOS":=^30}')
            cliente.send(json.dumps({"acao": "LISTAR_ARQUIVOS"}).encode("utf-8"))
            mensagem_servidor = cliente.recv(1024).decode("utf-8")
            print(mensagem_servidor)
            print()
        case 2:
            print()
            print(f'{"ADICIONAR ARQUIVO":=^30}')
            cliente.send(json.dumps({"acao": "ADICIONAR_ARQUIVO"}).encode("utf-8"))
            nome_arquivo = str(input("Informe o nome do arquivo: "))
            if not os.path.exists(nome_arquivo):
                cliente.send(b"\EOA")
                mensagem_servidor = cliente.recv(1024).decode("utf-8")
                print("Mensagem recebida: ", mensagem_servidor)
                print("Arquivo não encontrado! Cancelando ação")
                print()
                continue
            nome_arquivo_salvar = nome_arquivo[nome_arquivo.rindex("/") + 1 :]
            cliente.send(bytes(nome_arquivo_salvar, "utf-8"))
            with open(nome_arquivo, "rb") as file:
                while chunk := file.read(1024):
                    cliente.sendall(chunk)

            time.sleep(0.1)
            cliente.send(b"EOF")
            mensagem_servidor = cliente.recv(1024).decode("utf-8")
            print("Mensagem recebida: " + mensagem_servidor)
            print()
        case 3:
            print()
            print(f'{"BAIXAR ARQUIVO":=^30}')
            cliente.send(json.dumps({"acao": "BAIXAR_ARQUIVO"}).encode("utf-8"))
            arquivos_disponiveis = json.loads(cliente.recv(1024).decode("utf-8"))
            print(
                "\n".join(
                    [
                        f"{index} - {value}"
                        for index, value in enumerate(arquivos_disponiveis)
                    ]
                )
            )
            index_informado = int(input("Informe o código do arquivo desejado: "))
            try:
                nome_arquivo = arquivos_disponiveis[index_informado]
            except:
                print("Código inválido! Cancelando ação")
                print()
                continue
            cliente.send(nome_arquivo.encode("utf-8"))
            nome_arquivo_final = trata_nome_arquivo(nome_arquivo)
            try:
                recebe_arquivo_do_servidor(cliente, nome_arquivo_final)
            except Exception as e:
                print("Erro ao escrever no arquivo: " + e.__str__())
                print()
                continue
            print()
        case 4:
            running = False
            cliente.send(json.dumps({"acao": "SAIR"}).encode("utf-8"))
            cliente.close()

# %%
# with open("local/arquivo2.txt", 'r') as file:
#     while (buffer := file.read(1024)):
#         print(buffer, end='')
# %%
