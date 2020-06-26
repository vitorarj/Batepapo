import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Cria um socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configura REUSEADDR para 1 no socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# O servidor passa pro OS que vai usar o IP e a Porta passadas como paramêtro
# Pra um servidor usando 0.0.0.0 signfica escutar todas as interfaces
server_socket.bind((IP, PORT))

# Escutando novas conexões
server_socket.listen()

sockets_list = [server_socket]

clients = {}

print(f'Escutando conexões em: {IP}:{PORT}...')

# Recebendo as novas mensagens
def receive_message(client_socket):

    try:

        # Recebe o cabeçalho (header), contendo tamanho da mensagem
        message_header = client_socket.recv(HEADER_LENGTH)

        # Se nenhum dado é recebido será considerado que a conexão deve ser fechada
        # Pode-se usar socket.close() ou
        # socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Muda o cabeçalho para inteiro
        message_length = int(message_header.decode('utf-8').strip())

        # Retorna um objeto "cabeçalho" e "dados" da mensagem
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # Esse trecho entra em execução se a conexão foi fechada usando "ctrl+c"
        # Ou perdeu a conexão (internet caiu)
        return False

while True:

    # O select é usado para mexer em configurações de redes do SO independente do
    # SO que esteja em uso, aqui são usados 3 parâmetros dele, são eles:
    # rlist: sockets que irão enviar dados
    # wlist: sockets que estão prestes a enviar dados (se o buffer não estiver
    # cheio e o socket já está pronto para enviar)
    # xlist: sockets que serão monitorados por excessões (monitora erros, se
    # aparecer algo indevido usamos o rlist)
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Passa pelos sockets notificados (?)
    for notified_socket in read_sockets:

        # Se o socket notificado é um server, aceite
        if notified_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            # Recebe o nome do cliente (username, nick, apelido etc)
            user = receive_message(client_socket)

            # Se não houver conexão, o cliente cai sem nem enviar o nome
            if user is False:
                continue

            # Adiciona socket aceito para a lista de selecionados (append)
            sockets_list.append(client_socket)

            # Salva o apelido e o cabeçalho dele
            clients[client_socket] = user

            print('Conexão do endereço {}:{} confirmada. Usuário: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:

            # Recebe mensagem
            message = receive_message(notified_socket)

            # Se for falso, o cliente desconecta
            if message is False:
                print('Conexão fechada: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove da lista de sockets (socket.socket())
                sockets_list.remove(notified_socket)

                # Remove da lista de usuários
                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Nova mensagem recebida de {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Passa pelos clientes conectados e manda a mensagem (broadcast)
            for client_socket in clients:

                # Mas não envia para quem enviou
                if client_socket != notified_socket:

                    # Envia o usuário e a mensagem (com cabeçalho)
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Perfumaria pra administrar sockets
    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]
