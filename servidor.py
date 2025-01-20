# %%
# Tratamento mensagens
from typing import NotRequired, TypedDict
import os
import socket
import json
import enviroment
import signal
import sys
import time
import threading


def log(mensagem: str):
    print("(SERVIDOR)", mensagem)


LISTA_ACOES_DISPONIVEIS = [
    "LISTAR_ARQUIVOS",
    "ADICIONAR_ARQUIVO",
    "BAIXAR_ARQUIVO",
    "SAIR",
]


class Mensagem(TypedDict):
    acao: str
    nome_arquivo: NotRequired[str]


def trata_mensagem(mensagem: Mensagem, socketParaCliente: socket.socket) -> str:
    if "acao" not in mensagem or mensagem["acao"] not in LISTA_ACOES_DISPONIVEIS:
        return "Ação não disponível"
    match (mensagem["acao"]):
        case "LISTAR_ARQUIVOS":
            return recupera_lista_arquivos()
        case "ADICIONAR_ARQUIVO":
            return adiciona_arquivo(socketParaCliente)
        case "BAIXAR_ARQUIVO":
            return envia_arquivo(socketParaCliente)
        case "SAIR":
            return "SAIR"
        case _:
            return "Ação não implementada"


# %%
# Tratamento de arquivos


def recupera_lista_arquivos():
    arquivos = os.listdir("armazenamento/")
    return "\n".join(arquivos)


def envia_arquivo(socketParaCliente: socket.socket):
    arquivos = os.listdir("armazenamento/")
    socketParaCliente.send(json.dumps(arquivos).encode("utf-8"))
    nome_arquivo = socketParaCliente.recv(1024).decode("utf-8")
    with open(f"armazenamento/{nome_arquivo}", "rb") as file:
        while chunk := file.read(1024):
            socketParaCliente.sendall(chunk)
    time.sleep(0.1)
    return "EOF"


def trata_nome_arquivo(nome_arquivo, dup=0):
    nome = nome_arquivo
    if dup > 0:
        nome = f"({dup}) {nome_arquivo}"
    if os.path.exists(f"armazenamento/{nome}"):
        return trata_nome_arquivo(nome_arquivo, dup + 1)
    return nome


def adiciona_arquivo(socketParaCliente: socket.socket):
    nome_arquivo = socketParaCliente.recv(1024).decode("utf-8")
    log("Nome arquivo: " + nome_arquivo)
    if nome_arquivo == "\EOA":
        return "Nome de arquivo não informado"
    nome_arquivo = trata_nome_arquivo(nome_arquivo)
    try:
        with open(f"armazenamento/{nome_arquivo}", "wb") as file:
            while True:
                chunk = socketParaCliente.recv(1024)
                if chunk == b"EOF":
                    return f"Arquivo {nome_arquivo} criado com sucesso!"
                file.write(chunk)
    except Exception as e:
        return "Erro ao escrever no arquivo: " + e.__str__()


# %%


def handle_client(socketParaCliente):
    while True:
        log("Aguardando ação do cliente...")
        msg = socketParaCliente.recv(1024).decode("utf-8")
        log("Mensagem recebida: " + str(msg))
        action_result = trata_mensagem(json.loads(msg), socketParaCliente)
        log("Ação finalizada com sucesso")
        if action_result == "SAIR":
            socketParaCliente.close()
            log("Conexão com cliente fechada")
            break
        socketParaCliente.send(bytes(action_result, "utf-8"))


# Servidor com sockets
servidor = None
servidor_rodando = True


def trata_signal(_signal, _frame):
    global servidor_rodando
    global servidor
    log("Parando servidor")
    servidor_rodando = False
    servidor.close()
    sys.exit()


signal.signal(signal.SIGINT, trata_signal)

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
nome_servidor = socket.gethostname()
ip_servidor = socket.gethostbyname_ex(nome_servidor)
port = 8081
servidor.bind((ip_servidor[2][1], port))

servidor.listen(5)

log(f"Em funcionamento! {ip_servidor[2][1]}:{port}")
while servidor_rodando:
    log("Aguardando conexão...")
    socketParaCliente, enderecoCliente = servidor.accept()
    log(f"Conectado ao cliente: {enderecoCliente}")
    thread = threading.Thread(target=handle_client, args=[socketParaCliente])
    thread.start()

servidor.close()

# %%
