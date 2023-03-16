import socket
import logging
import re

logger = logging.getLogger(__name__.replace('__', ''))


class ClientTCP:

    def __init__(self, address_family, socket_kind, timeout=1.5):
        super(ClientTCP, self).__init__()

        self._address_family = address_family
        self._socket_kind = socket_kind

        self._ip = "127.0.0.1"
        self._port = 0
        self._timeout = timeout
        self._connected = False

    def get_connection_status(self):
        return self._connected

    def connect(self, ip, port):
        self._ip = ip
        self._port = port

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect((self._ip, self._port))
        
        self._connected = True

        logger.debug(f"Connection to {self._ip}:{self._port} successfully")



    def disconnect(self):

        if self._connected is True:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError as ex:
                logger.error(f"Shutdown error: {ex}")

            self._socket.close()

        self._connected = False

        logger.debug(f"Disconnect from server")


    def get_connection_status(self) -> bool:
        return self._connected
    
    def send(self, data):    
        if self._connected is True:
            self._send_data(data)

    def read(self, msg_len):
        data = None
        if self._connected is True:
            data = self._read_data(msg_len)
        return data
    
    def _read_data(self, msg_len):
        return self._socket.recv(msg_len)

    def _send_data(self, data):
        self._socket.send(data)


    def parse_answer_tcp_percent(self, data):
        new_data = data.decode("utf-8")

        # pos_start = new_data.find("per:")
        # pos_end = new_data.find(",")
        # val = 50
        # if pos_start != -1 and pos_end != -1:
        #     val = int(new_data[pos_start + 4:pos_end])
        val = 50
        match = re.search(r'per:\d+', new_data)
        try:
            val = int(match[0][4:])
        except TypeError as ex:
            logger.error(f"Parse percent error: {ex}. Match:{match}. Set val = 50")


        return val