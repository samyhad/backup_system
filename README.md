# Sistema de Backup Distribuído com Replicação

Este projeto implementa um sistema de backup distribuído que replica arquivos em servidores distribuídos. O sistema é capaz de selecionar servidores baseados em critérios como espaço disponível e número de requisições, garantindo redundância e alta disponibilidade dos arquivos armazenados.

## Funcionalidades

- **Upload de Arquivos:** Os clientes podem enviar arquivos para o sistema, que serão armazenados em um servidor selecionado pelo gerenciador.
- **Replicação de Arquivos:** Após o upload, os arquivos são replicados em um segundo servidor para garantir redundância.
- **Gerenciamento de Recursos:** O sistema monitora os recursos dos servidores, como o espaço disponível e o número de requisições, para otimizar a distribuição de arquivos.
- **Escalabilidade:** Novos servidores podem ser facilmente adicionados ao sistema, aumentando a capacidade de armazenamento e a redundância.

## Arquitetura

### Componentes

1. **Client (Cliente):** Responsável por enviar arquivos para o sistema. Conecta-se ao gerenciador, que designa um servidor principal para o armazenamento e um servidor secundário para a replicação.
2. **Manager (Gerenciador):** Centraliza a lógica de seleção de servidores com base nos recursos disponíveis e coordena as operações de replicação.
3. **Server (Servidor):** Recebe os arquivos do cliente e replica-os para outro servidor, garantindo que os arquivos sejam distribuídos de forma eficiente.

### Fluxo de Operações

1. O cliente envia uma solicitação de upload ao gerenciador.
2. O gerenciador seleciona um servidor com base nos recursos disponíveis (espaço em disco, carga de trabalho, etc.).
3. O cliente se conecta ao servidor principal e realiza o upload do arquivo.
4. Após o upload, o servidor principal replica o arquivo em outro servidor, conforme especificado pelo gerenciador.
5. Os servidores atualizam suas informações de uso de recursos com o gerenciador.

## Instalação

### Pré-requisitos

- Python 3.10+
- Bibliotecas: tqdm, os, json, threading, socket, entre outras.

### Clonando o Repositório

```bash
git clone 
cd backup_system
