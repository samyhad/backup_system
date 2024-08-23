from socket import *
import json
import os
import threading
from tqdm import tqdm
from utils import get_file_names, get_filepath, get_ip, get_port, interactive_menu


class Peer:

    managerName = '127.0.0.1'
    managerPort = 12000

    # Inicializa as informações o peer
    def __init__(self, ip, port, folder):
        self.ip = ip
        self.port = port
        self.folder = folder

    def upload_file(self, filename, filesize):
        # Cria uma nova conexão com o manager
        manager_socket = socket(AF_INET, SOCK_STREAM)
        manager_socket.connect((Peer.managerName, Peer.managerPort))

        try:
            request = {'type': 'client', 'func': 'upload', 'name_file': filename, 'file_size': filesize}
            manager_socket.send(json.dumps(request).encode())

            response = manager_socket.recv(1024).decode()
            response = json.loads(response)

            if response['status'] == 'failed':
                print("Falha ao iniciar upload.")
            elif response['status'] == 'success':
                serverIP = response['ip']
                serverPort = response['port']

                # Conecta ao servidor de destino
                serverSocket = socket(AF_INET, SOCK_STREAM)
                serverSocket.connect((serverIP, serverPort))

                try:
                    request = {
                        'type': 'client', 'func': 'upload',
                        'name_file': filename, 'file_size': filesize,
                        'client_addr': (self.ip, self.port)
                    }
                    serverSocket.send(json.dumps(request).encode())

                    response = serverSocket.recv(1024).decode()
                    response = json.loads(response)

                    if response['status'] == 'success':
                        with open(filename, 'rb') as file:
                            print(f"Enviando arquivo {filename} ...")
                            progress = tqdm(total=filesize, unit='B', unit_scale=True, desc="Uploading")

                            while True:
                                bytes_read = file.read(4096)
                                if not bytes_read:
                                    break
                                serverSocket.sendall(bytes_read)
                                progress.update(len(bytes_read))

                            progress.close()
                    else:
                        print("Servidor se recusou a receber documentos")

                finally:
                    serverSocket.close()
            else:
                print("Falha ao iniciar upload.")

        except ConnectionRefusedError as e:
            print(f"Falha ao se conectar com o servidor {e}")

        finally:
            # Fecha a conexão com o manager após a operação
            manager_socket.close()

        print("Upload concluído.")

    def close_connection(self):
        # Fecha a conexão do socket
        self.manager_socket.close()


# Inicialização do peer
def start_peer():

    # Exibe a mensagem
    print("Inicializando Peer.")

    # Armazena endereço de IP do peer
    peer_ip = '127.0.0.1' #get_ip('peer')

    # Armazena endereço de porta do peer
    peer_port = get_port('peer')

    # Captura as informações de pasta do peer
    peer_folder = get_filepath() #input("Digite a pasta do peer: ")
    if not peer_folder:
        peer_folder = '.'

    # Inicializa peer
    peer = Peer(ip=peer_ip, port=peer_port, folder=peer_folder)

    return peer

# Função principal do cliente (peer)
def main():
    # Criação do objeto Peer
    peer = start_peer()
    # Menu iterativo do lado do cliente (peer)
    interactive_menu(peer)



if __name__ == "__main__":
    main()

