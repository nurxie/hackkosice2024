import serial
import time

def send_file_to_com_port(filename, com_port):
    # Открытие COM-порта
    ser = serial.Serial(com_port, baudrate=9600, timeout=1)

    # Открытие файла для чтения
    with open(filename, 'r') as file:
        # Посимвольное чтение файла и отправка через COM-порт
        for line in file:
            for char in line:
                # Отправка символа
                ser.write(char.encode())
                # Задержка в 0.1 секунду
                time.sleep(0.03)

    # Закрытие COM-порта
    ser.close()

# Указать имя файла и COM-порт для отправки
# filename = 'output.txt'
# com_port = '/dev/ttyUSB1'

# Вызов функции для отправки файла
# send_file_to_com_port(filename, com_port)
