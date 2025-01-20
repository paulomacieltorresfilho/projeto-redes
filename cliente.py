# %%

import json
import socket
import enviroment
import os


def print_menu() -> None:
    print(f'{"MENU":=^30}')
    print("1. LISTAR ARQUIVOS")
    print("2. ADICIONAR ARQUIVO")
    print("3. RECUPERAR ARQUIVO")
    print("4. SAIR")


print("Conectando ao servidor...")
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((enviroment.host, enviroment.port))
print("Conectado com sucesso!")

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
                print("Arquivo não encontrado! Cancelando operação")
                print()
                continue
            nome_arquivo_salvar = nome_arquivo[nome_arquivo.rindex("/") + 1 :]
            cliente.send(bytes(nome_arquivo_salvar, "utf-8"))
            with open(nome_arquivo, "rb") as file:
                while chunk := file.read(1024):
                    cliente.send(chunk)
            cliente.send(b"\EOF")
            mensagem_servidor = cliente.recv(1024).decode("utf-8")
            print("Mensagem recebida: " + mensagem_servidor)
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
