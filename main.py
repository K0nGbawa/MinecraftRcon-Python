import random
import socket
import struct
import datetime


def error(s):
    print(f"{datetime.datetime.now().strftime('%H:%M:%S')} [ERROR] {s}")


def info(s):
    print(f"{datetime.datetime.now().strftime('%H:%M:%S')} [INFO] {s}")

def warn(s):
    print(f"{datetime.datetime.now().strftime('%H:%M:%S')} [WARN] {s}")

class RconClient:
    def __init__(self, ip: str, port: int, password: str):
        self.ip = ip
        self.port = port
        self.pwd = password
        self.rid = random.randint(1, 2147483647)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.login()

    def login(self):
        packet = self.build_packet(3, self.pwd)
        self.send_packet(packet)
        response = self.receive_packet()['request_id']
        if response == -1:
            raise "登录失败"
        else:
            info("登录成功")
            self.rid = response

    def build_packet(self, _type: int, payload: str):
        payload_bytes = payload.encode()
        length = len(payload_bytes) + 10
        packet = (
            struct.pack('<ii', length, self.rid) +
            struct.pack('<i', _type) +
            payload_bytes +
            b'\x00\x00'
        )
        return packet

    def send_packet(self, packet: bytes):
        self.socket.sendall(packet)

    def receive_packet(self):
        length_bytes = self.socket.recv(4)
        length = struct.unpack('<i', length_bytes)[0]
        packet = self.socket.recv(length)
        rid, _type = struct.unpack('<ii', packet[:8])
        payload = packet[8:-2].decode()
        return {'request_id':rid, 'packet': _type, 'payload':payload}

    def send_command(self, command):
        packet = self.build_packet(2, command)
        self.send_packet(packet)
        response = self.receive_packet()
        return response['payload']

    def exit(self):
        self.socket.close()






if __name__ == "__main__":
    Client = RconClient('127.0.0.1', 25575, 'password')
    Client.connect()
    while True:
        cmd = input('>_ ')
        cmd = cmd.strip()
        if cmd[:4] == "from":
            with open(cmd.split(' ')[1], 'r') as f:
                txt = f.read()
                if '\r\n' in txt:
                    cmds = txt.split('\r\n')
                else:
                    cmds = txt.split('\n')
                for i in cmds:
                    info(f'executing "{i.strip()}"')
                    Client.send_command(i.strip())
            continue
        Client.send_command(cmd)