import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

data = input("Command: ")

handler = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

handler.write(bytes(data, 'ascii'))

data = handler.readline().decode('ascii')
while(not data):
    data = handler.readline().decode('ascii')
    pass
data = data[0:len(data)-2]
print(data)