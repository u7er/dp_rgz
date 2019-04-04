import socket
import random

# Соединяемся с сервером
host = "localhost"
port = 8080
print("I'm client. Wait for server to respond!")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

# Получаем N
print(s.recv(1024).decode('utf8'))
N = int(s.recv(1024).decode('utf8'))
print("Server N = ", N)

while True:
    print("1. Sign In")
    print("2. Log In")
    key = input()
    # Если мы хотим зарегистрироваться
    if key == "1":
        # Посылаем серверу сигнал о том, что хотим зарегистрироваться
        s.send("SIGNIN".encode('utf8'))

        # Вводим логин и пароль
        print("Input user name")
        username = input()
        s.send(username.encode('utf8'))
        print("Input password")
        # Вычисляем ключ и отправляем его
        # TODO: changed (int(input()) ** 2) % N ->
        password = (int(input()) ** 2) % N
        s.send(str(password).encode('utf8'))

        # Получаем ответ от сервера и выводим его
        response = s.recv(1024)
        print('Server response: ', response.decode('utf8'))
    # Если хотим авторизироваться
    elif key == "2":
        # Посылаем серверу сигнал о том, что хотим авторизироваться и логин
        print("Input user name")
        username = input()
        s.send("LOGIN".encode('utf8'))
        s.send(username.encode('utf8'))
        answer = s.recv(1024).decode('utf8')
        # Если сервер посылает сигнал о том, что такого пользователя не существует, заканчиваем авторизация
        if answer == "NOTEXISTS":
            print("Username not exists, please Sign In first")
        else:
            # Получаем пароль
            check = True
            print("Input password")
            password = int(input())
            print("Trying to login")
            # Проводим 20 тестов
            for i in range(20):
                print("Test ", i + 1, ":")
                # Генерируем случайно число r от 1 до N - 1
                r = random.randint(1, N - 1)
                print("r = ", r)
                # Вычисляем x и посылаем его
                x = (r ** 2) % N
                print("x = ", x)
                s.send(str(x).encode('utf8').rstrip())
                # Принимаем бит е
                e = int(s.recv(1024).decode('utf8').rstrip())
                print("e = ", e)
                # Вычисляем y и посылаем его
                y = (r * (password ** e)) % N
                print("y = ", y)
                s.send(str(y).encode('utf8').rstrip())
                # Получаем ответ и в если раунд не пройден, заканчиваем, иначе переходим к следующему
                answer = s.recv(1024).decode('utf8').rstrip()
                if answer == "False":
                    check = False
                    break
            # Выведем сообщение в зависимости от результата тестирования
            if check == True:
                print("Log in successfully")
            else:
                print("Log in failed")
    else:
        pass
s.close()
