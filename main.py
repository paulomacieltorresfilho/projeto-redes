#%% 
import socket

host = socket.gethostbyname_ex('cataas.com')
print(host)
#%%
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host[2][0], 80))
requisicao_http = \
"""GET /cat HTTP/1.1
Host: cataas.com
Connection: keep-alive

"""
res = client.send(bytes(requisicao_http, "utf-8"))
print(res)

#%%
print(client)
resposta = client.recv(10000)
print(resposta)

client.close()
# %%
