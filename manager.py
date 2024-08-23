from socket import *
import threading
import time
import json
import random

file_registry = {}
server_registry = []
registry_lock = threading.Lock()

def handle_client(connectionSocket, addr):
    try:
        print(f"Conexão estabelecida com {addr}")

        data = connectionSocket.recv(4096).decode()
        request = json.loads(data)
        status = ''
        message = ''
        
        # Verifica o tipo de remetente
        if 'type' in request:
            if request['type'] == 'client':
                print("Requisição recebida de um cliente.")
                response = process_client_request(request)
                
            elif request['type'] == 'server':
                print("Requisição recebida de um servidor.")
                response = process_server_request(request)
            else:
                print("Tipo de remetente desconhecido.")
                response = {'status': 'failed'}
        else:
            print("Formato de mensagem inválido.")
            response = {'status': 'failed'}

        # Envia uma resposta de confirmação
        #response = response.update({'status': status})
        connectionSocket.send(json.dumps(response).encode())

    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}")
    finally:
        pass
        # Fecha a conexão com o cliente
        #connectionSocket.close()
        #print(f"Conexão com {addr} encerrada")

def update_server_resources(ip, port, active_connections=None, used_space=None):
    print("Atualizando dados do server")
    print(f'{ip}:{port} - {used_space} - {active_connections}')
    with registry_lock:
        for server in server_registry:
            if server['ip'] == ip and server['port'] == port:
                if active_connections is not None:
                    server['active_connections'] = active_connections
                if used_space is not None:
                    server['available_space'] = used_space
                break

def process_client_request(request):
    # Lógica para processar requisições de clientes
    func = request['func']
    if func == 'upload':
        print("Escolhendo um servidor")
        try:
            
            server = choice_server(required_space=request['file_size'])
            server_ip = server[0]
            server_port = server[1]
            response = {'status': 'success', 'ip': server_ip, 'port': server_port}
            print("   server escolhido: "+ str(server_ip) +':'+ str(server_port))
        except Exception as e:
            print("Erro ao escolher servidor: ", e)
            response = {'status': 'failed'}
    else:
        print("Cliente mandou uma requisição ainda não tratada")
        response = {'status': 'failed'}
    
    return response

def choice_server_(previous_server=None):
    server_addresses = get_servers()
    # [('127.0.0.1', 5040), ('127.0.0.1', 5041), ('127.0.0.1', 5042)]

    available_servers = server_addresses.copy()

    if previous_server in available_servers:
        available_servers.remove(previous_server)

    if not available_servers:
        raise Exception("Não há servidores disponíveis para escolha.")

    selected_server = random.choice(available_servers)
    return selected_server

def choice_server(previous_server=None, required_space=0):
    servers = get_servers()

    if previous_server:
        servers = [s for s in servers if (s['ip'], s['port']) != previous_server]

    if not servers:
        raise Exception("Não há servidores disponíveis para escolha.")

    servers.sort(key=lambda s: (s['active_connections'], s['available_space']))

    capable_servers = [
        s for s in servers if s['available_space'] > required_space and s['active_connections'] < s['server_conn']
    ]

    print("Servidores capazes: ")
    print(capable_servers)

    if not capable_servers:
        raise Exception("Nenhum servidor disponível pode atender à requisição. Espaço insuficiente ou excesso de conexões.")

    selected_server = capable_servers[0]

    return (selected_server['ip'], selected_server['port'])
   
def process_server_request(request):
    func = request['func']
    
    if func == 'received_file':
        print('Confirmando upload do arquivo')

        filename = request['filename']
        client_ip = request['client_ip'] 
        client_port = request['client_port'], 
        server_addresses = request['server_addresses'],
        register_file(client_ip, client_port, filename, server_addresses)
        response = {'status': 'success'}

    elif func == 'update_resources':
        update_server_resources(
            request['ip'], 
            request['port'], 
            active_connections=request.get('active_connections'), 
            used_space=request.get('available_space')
        )
        response = {'status': 'success'}

    elif func == 'upload':
        print("Escolhendo um servidor")
        try:
            server = choice_server(request['file_size'])
            server_ip = server[0]
            server_port = server[1]
            response = {'status': 'success', 'ip': server_ip, 'port': server_port}
            print("   server escolhido: "+ str(server_ip) +':'+ str(server_port))
        except Exception as e:
            print("Erro ao escolher servidor: ", e)
            response = {'status': 'failed'}
    elif func == 'get_backup_server':
        print("Escolhendo um servidor")
        previous_server = (request['ip'], request['port'])
        try:
            server = choice_server(previous_server, request['file_size'])
            server_ip = server[0]
            server_port = server[1]
            response = {'status': 'success', 'ip': server_ip, 'port': server_port}
            print("   Server Escolhido: "+ str(server_ip) +':'+ str(server_port))
        except Exception as e:
            print("Erro ao escolher servidor: ", e)
            response = {'status': 'failed'}
    elif func == 'registry_server':
        register_server(
            request['ip'], 
            request['port'],
            request['active_connections'],
            request['server_conn'],
            request['available_space'])
        print(get_servers())
        response = {'status': 'success'}
    elif func == 'add_file':
        client_ip = request['client_addr'][0]
        client_port = request['client_addr'][1]
        filename = request['filename']
        server_addresses = (request['ip'], request['port'])
        register_file(client_ip, client_port, filename, server_addresses)
        response = {'status': 'success'}
    else:
        print("Servidor mandou uma requisição ainda não tratada")
        response = {'status': 'failed'}

    return response

def register_file(client_ip, client_port, filename, server_addresses):
    key = (client_ip, client_port, filename)
    
    with registry_lock:
        file_registry[key] = server_addresses

def register_server_(ip, port):
    with registry_lock:
        if (ip, port) not in server_registry:
            server_registry.append((ip, port))
            print(f"Servidor {(ip, port)} registrado com sucesso.")
        else:
            print(f"Servidor {(ip, port)} já está registrado.")

def register_server(ip, port, active_connections, server_conn, available_space):
    with registry_lock:
        if (ip, port) not in server_registry:
            server_registry.append({
                'ip': ip, 
                'port': port, 
                'active_connections': active_connections,
                'available_space': available_space,
                'server_conn': server_conn
            })
            print(f"Servidor {(ip, port)} registrado com sucesso.")
        else:
            print(f"Servidor {(ip, port)} já está registrado.")

def get_file_servers(client_ip, client_port, filename):
    key = (client_ip, client_port, filename)
    
    with registry_lock:
        return file_registry.get(key, [])

def get_servers():
    with registry_lock:
        return server_registry


serverPort = 12000
serverIP = "127.0.0.1"  

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(1000)

print("O gerenciador está pronta para receber solicitações")

while True:
    # Aceita uma conexão de um cliente
    connectionSocket, addr = serverSocket.accept()
    # Cria um novo thread para lidar com a conexão do cliente
    clientThread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
    clientThread.start()
