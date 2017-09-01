import json
import threading
import socket
import struct
import zlib
import pprint
import sys
import logging

class Transceiver():
    def __init__(self):
        self.buf = b""
        self.compress = False
        self.sock= None
        self.requestId = 1
        self.mutex=threading.Lock()
    def socket_connect(self,gateway_info):
        try:
            self.mutex.acquire()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((gateway_info['host'], gateway_info['port']))
        finally:
            self.mutex.release()


    def __send_and_echo(self, serverType, serverId, command, param={}, json=False, output=False):
        try:
            self.mutex.acquire()
            self.__check_connect()
            self.__send(serverType, serverId, command, json, param)
            return self.recv(output)
        finally:
            self.mutex.release()

    def __check_connect(self):
        if self.sock is None:
            raise Exception("not connect yet")

    def __send(self, serverType, serverId, cmd, json, param={}):
        data = ""
        # pack send params
        if json:
            data = param['data']
        else:
            index = 1
            for (key, value) in param.items():
                value = str(value)
                if index > 1:
                    data = data + "&"
                data = data + key + "=" + value
                index = index + 1

        # pack package
        if serverType != None:
            length = 45 + len(data)
            result = struct.pack(">ibii32si%ss" % (len(data)), length, 1, serverType, serverId, cmd.encode('utf-8'),
                                 self.requestId, data.encode('utf-8'))
        else:
            length = 37 + len(data)
            result = struct.pack(">ib32si%ss" % (len(data)), length, 1, cmd.encode('uft-8'), self.requestId,
                                 data.encode('utf-8'))

        # send package
        self.sock.send(result)
        self.requestId = self.requestId + 1
        return result

    def recv(self, output=False):
        self.__check_connect()

        # read package head
        if (len(self.buf) < 4):
            data = self.sock.recv(1024)
            self.buf = self.buf + data

        # obtain package length
        length = struct.unpack(">i", self.buf[0:4])
        length = int(length[0])

        # store package content
        while (len(self.buf) < length + 4):
            data = self.sock.recv(1024)
            self.buf = self.buf + data

        # parse package
        command, id, msg = struct.unpack(">32si%ss" % (length - 5 - 32), self.buf[5:length + 4])

        # decompress if server open the compress option
        if self.compress:
            msg = zlib.decompress(msg)

        # store the extra content
        self.buf = self.buf[4 + length:]

        # parse content use Json
        jsonObj = json.loads(msg.decode('utf-8'))
        state = jsonObj['state']

        # print content
        if output:
            logging.info(msg.decode("utf-8"))
            pp = pprint.PrettyPrinter()
            pp.pprint(jsonObj)
            sys.stdout.flush()

        return jsonObj

    def send_cmd_server(self, server_type,server_id,cmd,params={},output=False):
        json_obj = self.__send_and_echo(server_type, server_id, cmd, params, output=output)
        return json_obj

