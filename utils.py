import os
import re

# Método para extrair endereço IP válido
def extract_ip(string):
    # Regex para extrair o IP
    pattern_1 = r"\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*"
    pattern_2 = r"\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)\s*"

    # Extrai o IP usando a regex do pattern
    match_1 = re.match(pattern_2, string)
    match_2 = re.match(pattern_1, string)

    # Lógica para devolver endereço IP válido
    if match_1:
        ip = str(match_1.group(1))
        return ip
    elif match_2:
        ip = str(match_2.group(1))
        return ip
    else:
        raise Exception(f"[ERRO] Formato de endereço IP inválido.")

# Método para extrair endereço porta válido
def extract_port(string):
    # Regex para extrair o Porta
    pattern_1 = r"\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)\s*"
    pattern_2 = r"\s*(\d+)\s*"

    # Extrai o porta usando a regex do pattern
    match_1 = re.match(pattern_1, string)
    match_2 = re.match(pattern_2, string)

    # Lógica para devolver endereço porta válido
    if match_1:
        port_int = int(match_1.group(2))
        return port_int
    elif match_2:
        port_int = int(match_2.group(1))
        return port_int
    else:
        raise Exception(f"[ERRO] Formato de endereço porta inválido.")

# Método para capturar endereço IP válido
def get_ip(class_type):
    # Captura do IP
    ip = input(f"Informe o IP do {class_type} (default: 127.0.0.1): ")
    if not ip:
        ip = "127.0.0.1"
    ip = extract_ip(ip)
    # Exibe endereço IP recebido por input
    print(f"Endereço IP do {class_type} capturado: {ip}.")
    return ip

# Método para capturar endereço de porta válido
def get_port(class_type):

    class_type = class_type.lower()

    if (class_type == 'servidor' or class_type == 'server'):
        port = input(f"Informe a porta do {class_type} (default: 1099): ")
        if not port:
            port = "1099"
        port = extract_port(port)
        # Exibe endereço porta recebido por input
        print(f"Endereço de porta do {class_type} capturado: {port}.")
        return port

    elif (class_type == 'peer' or class_type == 'client' or class_type == 'cliente'):
        port = input(f"Informe a porta do {class_type} (default: 1100): ")
        if not port:
            port = "1100"
        port = extract_port(port)
        # Exibe endereço porta recebido por input
        print(f"Endereço de porta do {class_type} capturado: {port}.")
        return port

    else:
        # Exibe endereço porta recebido por input
        print(f"Class type: {class_type} não foi identificado.")

# Método para capturar caminho de arquivo válido
def get_filepath():
    while True:
        print("Digite o diretório do peer, ou 0 para sair.")
        path = input("Caminho do arquivo (default: peer folder): ")
        if os.path.exists(path):
            return path
        elif path == "0":
            break
        else:
            print("Caminho inválido. Por favor, tente novamente.")

# Método para capturar nome de arquivo
def get_filename():
    while True:
        print("Digite o nome do arquivo, ou 0 para sair.")
        filename = input("Nome do arquivo (default: 'README.md'): ")
        if not filename:
            filename = 'README.md'
        return filename

def get_filename2(folder):
    #Pede ao usuário um nome de arquivo até que um arquivo existente seja fornecido.
    while True:
        filename = input("Digite o nome do arquivo: ")
        file_path = os.path.join(folder, filename)
        
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            return file_path, bytes_to_mb(file_size)
        else:
            print(f"O arquivo '{filename}' não existe no diretório '{folder}'. Tente novamente.")

def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # Verifica se o arquivo realmente existe
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def mb_to_bytes(mb):
    return mb * 1024 * 1024

def bytes_to_mb(bytes):
    return bytes / (1024 * 1024)

# Método para obter nomes dos arquivos em uma pasta
def get_file_names(folder):
    # Verifica se o caminho é uma pasta válida
    if not os.path.isdir(folder):
        raise ValueError("O caminho fornecido não é uma pasta válida.")

    # Obtém os nomes dos arquivos na pasta
    file_names = []
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            file_names.append(file_name)

    return file_names

# Verifica se o diretório existe, caso não exista, crie
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Diretório '{directory_path}' criado.")
    else:
        print(f"Diretório '{directory_path}' já existe.")

# Método para apresentar todos os arquivos de um diretório
def list_files_in_directory(folder):
    try:
        # Obter a lista de arquivos no diretório
        files = os.listdir(folder)
        
        # Verificar se a lista está vazia
        if not files:
            print("Por enquanto esse diretório está vazio")
        else:
            print("Arquivos no diretório:")
            for root, dirs, files in os.walk(folder):
                # Para cada arquivo na pasta atual, exibe o caminho completo
                for file in files:
                    print("    ", end="")
                    print(os.path.join(root, file))
    except FileNotFoundError:
        print("Diretório não encontrado.")

# Método para capturar entradas do peer
def interactive_menu(peer):
    # Peer Info
    my_ip = peer.ip
    my_port = peer.port
    my_folder = peer.folder

    # Peer Info
    print(f'DETALHES SOBRE O PEER: ')
    print(f"IP: {my_ip}, PORT: {my_port}, DIR: {my_folder}")
    
    # Menu
    while True:
        # Opções
        option = input("Você deseja enviar algum arquivo, se sim digite 1, caso contrário digite 0: ")
        
        if option == "1":
            filename, filesize = get_filename2(my_folder)
            peer.upload_file(filename, filesize)
        elif option == "0":
            print("Saindo do programa...")
            peer.close_connection()
            break
        else:
            print("Opção inválida. Tente novamente.")