import socket
import select
import errno

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Nome no chat: ")

# Cria o socket, aqui são usados IPv4 e TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao IP e a porta escolhida
client_socket.connect((IP, PORT))

# Configura a conexão para "non-blocking", então ".recv()" não será bloqueado
client_socket.setblocking(False)

# Preparar o nome de usuário (username), transformando em bytes para compor a mensagem
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    # Espera o usuário inserir a mensagem
    message = input(f'{my_username} > ')

    # Se a mensagem não for vazia nem sair(), envie
    if message and message != "sair()":

        # Codifica a mensagem para bytes, preara o header e converte em bytes também, após isso envie
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        # Loop das mensagens recebidas e 'printa'
        while True:

            # Recebe o header contendo o tamanho do nome de usuário. O tamanho é definido e constante
            username_header = client_socket.recv(HEADER_LENGTH)

            # Se não receber dados, o servidor fecha a conexão
            if not len(username_header):
                print('Conexão fechada pelo servidor')
                sys.exit()

            # Converte o header para int
            username_length = int(username_header.decode('utf-8').strip())

            # Recebe e traduz o nome de usuário
            username = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Exibe a mensagem
            print(f'{username} > {message}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Erro: {}'.format(str(e)))
            sys.exit()

        continue

    except Exception as e:
        print('Erro: '.format(str(e)))
        sys.exit()
