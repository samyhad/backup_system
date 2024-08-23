from socket import *
import json
import os
import threading
from utils import get_directory_size, ensure_directory_exists, get_file_names, get_filepath, get_ip, get_port, list_files_in_directory, bytes_to_mb, mb_to_bytes

class Server:
    managerName = '127.0.0.1'
    managerPort = 12000

    def __init__(self, ip, port, folder, server_conn, server_size):
        self.ip = ip
        self.port = port
        self.folder = folder
        self.capacity = {'conn':server_conn, 'size':server_size}
        self.active_connections = 0
        self.used_space = bytes_to_mb(get_directory_size(folder))
        self.register_server()

    def register_server_(self):
        request = {'type': 'server', 'func': 'registry_server', 'ip': self.ip, 'port': self.port}
        self.send_to_manager(request)

    def register_server(self):
        request = {
            'type': 'server', 
            'func': 'registry_server', 
            'ip': self.ip, 
            'port': self.port,
            'active_connections': self.active_connections,
            'server_conn': self.capacity['conn'],
            'available_space': self.capacity['size'] - bytes_to_mb(get_directory_size(self.folder))#self.capacity['size'] - self.used_space  # ou calcule o espaço disponível real
        }
        
        self.send_to_manager(request)
    
    def notify_manager_update(self, active_connections = 0, used_space = 0):
        request = {
            'type': 'server', 
            'func': 'update_resources', 
            'ip': self.ip, 
            'port': self.port, 
            'active_connections': self.active_connections, 
            'available_space': self.capacity['size'] - bytes_to_mb(get_directory_size(self.folder))#self.capacity['size'] - self.used_space
        }
        print(f"    Espaço disponível: {request['available_space']}")
        print(f"    Conexões ativas: {request['active_connections']}")
        self.send_to_manager(request)

    def send_to_manager(self, request):
        try:
            manager_socket = socket(AF_INET, SOCK_STREAM)
            manager_socket.connect((Server.managerName, Server.managerPort))
            manager_socket.send(json.dumps(request).encode())

            response = manager_socket.recv(1024).decode()
            response = json.loads(response)
        finally:
            manager_socket.close()
        return response

    def handle_client(self, connectionSocket, addr):
        
        self.active_connections += 1
        self.notify_manager_update(active_connections=self.active_connections)
        
        try:
            print(f"Conexão estabelecida com {addr}")
            data = connectionSocket.recv(4096).decode()
            request = json.loads(data)

            if 'type' in request:
                if request['type'] == 'client':
                    print("Requisição recebida de um cliente.")
                    self.process_client_request(request, connectionSocket)
                elif request['type'] == 'server':
                    print("Requisição recebida de um servidor.")
                    self.process_server_request(request, connectionSocket)
                else:
                    print("Tipo de remetente desconhecido.")
            else:
                print("Formato de mensagem inválido.")

            # Envia uma resposta de confirmação
            #response = {'status': status, 'message': message}
            #connectionSocket.send(json.dumps(response).encode())

        except Exception as e:
            raise 
            print(f"Erro ao lidar com o cliente {addr}: {e}")
        finally:
            # Fecha a conexão com o cliente
            self.active_connections -= 1
            self.notify_manager_update(active_connections=self.active_connections)
            connectionSocket.close()
            print(f"Conexão com {addr} encerrada")

    def process_client_request(self, request, connectionSocket):
        if request['func'] == 'upload':
            self.receiving_file(request, connectionSocket)
            self.replicating_data(request['name_file'], request['file_size'], request['client_addr'])
            list_files_in_directory(self.folder)
        else:
            print("Requisição solicitada é desconhecida")

    def process_server_request(self, request, connectionSocket):
        if request['func'] == 'upload':
            print("Recebendo arquivo")
            self.receiving_file(request, connectionSocket)

    def listening(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((self.ip, self.port))
        serverSocket.listen(self.capacity['conn'])

        print("O servidor está pronto para receber solicitações")

        while True:
            # Aceita uma conexão de um cliente
            connectionSocket, addr = serverSocket.accept()

            # Verifica o limite de conexões
            if self.active_connections < self.capacity['conn']:
                self.active_connections += 1
                # Cria um novo thread para lidar com a conexão do cliente
                clientThread = threading.Thread(target=self.handle_client, args=(connectionSocket, addr))
                clientThread.start()
            else:
                print("Número máximo de conexões atingido.")
                connectionSocket.close()
    
    def receiving_file(self, request, connectionSocket):
        filename = request['name_file']
        filesize = request['file_size']
        client_addr = request['client_addr']

        connectionSocket.send(json.dumps({'status': 'success'}).encode())

        filepath = os.path.join(self.folder, filename)
        ensure_directory_exists(os.path.dirname(filepath))
        
        if os.path.exists(filepath):
            used_space=filesize-bytes_to_mb(os.path.getsize(filepath))
        else:
            used_space=filesize
        
        with open(filepath, 'wb') as file:
            print(f"Recebendo arquivo {os.path.basename(filename)} de {client_addr} ...")
            bytes_received = 0
            while bytes_received < mb_to_bytes(filesize):
                bytes_read = connectionSocket.recv(4096)
                if not bytes_read:
                    break
                file.write(bytes_read)
                bytes_received += len(bytes_read)

        request = {
            'type': 'server', 'func': 'add_file', 
            'ip': self.ip, 'port': self.port, 
            'client_addr': client_addr, 
            'filename': filename
        }
        
        self.used_space = bytes_to_mb(get_directory_size(self.folder))

        self.notify_manager_update(used_space=self.used_space)

        self.send_to_manager(request)

        print(f"Arquivo {os.path.basename(filename)} recebido com sucesso.")

    def replicating_data(self, filename, filesize, client_addr):
        request = {
            'type': 'server', 'func': 'get_backup_server', 
            'ip': self.ip, 'port': self.port,
            'file_size': filesize}
        response = self.send_to_manager(request)

        if response['status'] == 'failed':
            print("Falha ao iniciar o backup dos dados")
        elif response['status'] == 'success':
            backup_server = (response['ip'], response['port'])
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((backup_server[0], backup_server[1]))

            request = {
                'type': 'server', 'func': 'upload', 
                'name_file': filename, 'file_size': filesize, 
                'client_addr': client_addr
            }
            
            serverSocket.send(json.dumps(request).encode())

            response = serverSocket.recv(1024).decode()
            response = json.loads(response)

            if response['status'] == 'success':
                with open(filename, 'rb') as file:
                    print(f"Enviando arquivo {filename}...")
                    while True:
                        bytes_read = file.read(4096)
                        if not bytes_read:
                            break
                        try:
                            serverSocket.sendall(bytes_read)
                        except ConnectionResetError as e:
                            print(f"Erro: Conexão foi resetada durante o envio: {e}")
                            break
                        except Exception as e:
                            print(f"Erro ao enviar dados: {e}")
                            break
            else:
                print("Falha ao entrar em contato com o servidor de backup")

            serverSocket.close()

def start_server():

    # Exibe a mensagem
    print("Inicializando server ...")

    # Armazena endereço de IP 
    server_ip = '127.0.0.1' #get_ip('server')

    # Armazena endereço de porta 
    server_port = get_port('server')

    server_conn = 20#int(input("Quantas conexões esse servidor pode receber: "))

    server_size = 10 #int(input("Quanto espaço de armazenamento esse servidor tem (mb): "))

    # Captura as informações de pasta 
    server_folder = get_filepath() #input("Digite a pasta do peer: ")
    if not server_folder:
        server_folder = '.'

    print("Conectando ao gerenciador")
    server = Server(
         ip=server_ip, 
         port=server_port, 
         folder=server_folder, 
         server_conn=server_conn, 
         server_size=server_size)

    return server

def main():
    server = start_server()
    server.listening()

if __name__ == "__main__":
    main()
