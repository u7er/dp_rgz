import socket
import random
import os

#Функция проверки числа на простоту
def check_for_prime(possible_prime):
    isPrime = True
    for num in range(2, int(possible_prime ** 0.5) + 1):
        if possible_prime % num == 0:
            isPrime = False
            break
    return isPrime

#Функция для генерации простого числа
def gen_prime():
    prime = random.randint(1000, 100000)
    while check_for_prime(prime) == False:
        prime = random.randint(1000, 100000)
    return prime

#IP-адресс и порт
host = "localhost"
port = 8080

#Инициализация и ожидание соединения клиента
print("Hi! I'm server, I'll wait for client to connect!")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
sock, addr = s.accept()
print("Client connected with address " + addr[0] + "!")
sock.send(b"Connected!")

#Считываем базу логин-ключ из файла
base = {}
with open("base.txt") as f:
    for line in f:
       if line == "":
           pass
       (key, val) = line.split()
       base[str(key)] = val

#Генерация чисел и запись их в файл
P = gen_prime()
Q = gen_prime()
N = P * Q
with open("secret numbers.txt", 'a') as f:
    f.write(str(P) + "\n" + str(Q) + "\n" + str(N) + "\n")

#Инициализация чисел и считываение их из файла
P = Q = N = 0
with open("secret numbers.txt") as f:
    P = int(f.readline())
    Q = int(f.readline())
    N = int(f.readline())

print("P = ", P, "\nQ = ", Q, "\nN = ", N)
#Отправляем клиенту число N
sock.send(str(N).encode('utf8'))
while True:
    buf = sock.recv(1024)
    buf = buf.rstrip()
    #Если пользователь хочет зарегистрироваться
    if buf.decode('utf8') == "SIGNIN":
        #Получаем логин-ключ от пользователя
        new_username = sock.recv(1024).decode('utf8')
        # TODO: changed int(sock.recv(1024).decode('utf8')) ->
        new_password = int(sock.recv(1024).decode('utf8'))
        #Если такого пользователя нету, то посылаем пользователю сигнал о том, что регистрация прошла успешно, иначе говорим, что пользователь с таким логином существует
        if not new_username in base:
            base[new_username] = new_password
            with open("base.txt", 'a') as f:
                f.write("\n" + new_username + " " + str(new_password))
            print("New user added to base. Login: ", new_username, ", Password: ", new_password)
            sock.send("Success!".encode('utf8'))
        else:
            sock.send("This user already exists!".encode('utf8'))
    #Если пользователь хочет авторизироваться
    elif buf.decode('utf8') == "LOGIN":
        #Получаем логин и проверяем его на наличие
        username = sock.recv(1024).decode('utf8')
        if not username in base:
            sock.send(b"NOTEXISTS")
        else:
            sock.send(b"EXISTS")
            password = int(base[username])
            check = True
            print("User ", username, " tries to login")
            #Проводим 20 тестов
            for i in range(20):
                print("Test ", i + 1, ":")
                #Получаем х от клиента
                x = int(sock.recv(1024).decode('utf8'))
                print("x = ", x)
                #Генерируем бит е
                e = random.randint(0, 1)
                print("e = ", e)
                sock.send(str(e).encode('utf8'))
                #Получаем y от клиента
                y = int(sock.recv(1024).decode('utf8'))
                print("y = ", y)
                #Проверяем полученные значения
                if (((y ** 2) % N) == ((x * (password ** e)) % N)):
                    sock.send(b"True")
                else:
                    sock.send(b"False")
                    check = False
                    break
            #Выведем сообщение в зависимости от результата тестирования
            if check == True:
                print("User ", username, " Log on successfully")
            else:
                print("User ", username, " log in failed")
sock.close()
