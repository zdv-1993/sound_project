import socket
import json
import hashlib
from constants import COMMAND_UPLOAD_WITH_PARAMS, COMMAND_GET_FILE_PARAMS, PORT, SENDED_BYTES_COUNT, COMMAND_GET_FILE_DATA
import copy


HOST = socket.gethostname()

MAX_TRIES_COUNT = 100


class FileUploaderClient:

    def __init__(self):
        self._connect()

    def _connect(self):
        self._client_socket = socket.socket()  # instantiate
        self._client_socket.settimeout(10)
        self._client_socket.setblocking(True)
        self._client_socket.connect((HOST, PORT))  # connect to the server

    def _send_to_socket(self, input_data: bytes):
        return self._client_socket.send(input_data)

    def _recv_from_socket(self, bytes_count: int) -> bytes:
        return self._client_socket.recv(bytes_count)

    @staticmethod
    def _get_json_data(json_bytes: bytes):
        return json.loads(json_bytes.decode())

    @staticmethod
    def _get_bytes_from_data(data: dict):
        return json.dumps(data).encode()
        
    
    def send_json_data(self, command: str, **params):
        params["command"] = command
        self._send_to_socket(self._get_bytes_from_data(params))
    
    def recv_json_data(self):
        bytes_data = self._recv_from_socket(SENDED_BYTES_COUNT)
        return self._get_json_data(bytes_data)
    
    def recv_bytes_data(self, bytes_count):
        res = bytes()
        test_arr = []
        if bytes_count <= SENDED_BYTES_COUNT:
            return self._recv_from_socket(bytes_count)
        while len(res) < bytes_count:
            item = self._recv_from_socket(SENDED_BYTES_COUNT)
            if not item:
                break
            res += item
        return res

    def send_bytes_data(self, bytes_data: bytes) -> dict:
        bytes_data_len = len(bytes_data)
        sended = bytes()
        for start_bytes_position in range(0, bytes_data_len +1 , SENDED_BYTES_COUNT):
            sended += bytes_data[start_bytes_position:start_bytes_position+SENDED_BYTES_COUNT]
            self._send_to_socket(bytes_data[start_bytes_position:start_bytes_position+SENDED_BYTES_COUNT])
    
    def _upload_file(self, file_bytes: bytes, extra_params: dict = {}):
        params = copy.copy(extra_params)
        params["sha256"] = hashlib.sha256(file_bytes).hexdigest()
        params["file_len"] = len(file_bytes)
        # TODO: убрать
        params["overwrite"] = True

        self.send_json_data(COMMAND_UPLOAD_WITH_PARAMS, **params)
        first_step_data = self.recv_json_data()

        if "error" in first_step_data:
            print(first_step_data)
            return False
        
        self.send_bytes_data(file_bytes)
        second_step_result = self.recv_json_data()
        if "error" in second_step_result:
            print(second_step_result)
            return False
        print(second_step_result)
        return True
        
    def upload_music(self, file_bytes: bytes, image: str, author: str, album: str, source: str, source_data: dict):
        extra_params = {
            "image": image,
            "author": author,
            "album": album,
            "source": source,
            "source_data": source_data,
        }
        return self._upload_file(file_bytes=file_bytes, extra_params=extra_params)

    def get_file_params(self, sha256_str):
        self.send_json_data(COMMAND_GET_FILE_PARAMS, sha256=sha256_str)
        return self.recv_json_data()
    
    def get_file_data(self, sha256_str, file_len):
        self.send_json_data(COMMAND_GET_FILE_DATA, sha256=sha256_str)
        return self.recv_bytes_data(file_len)


def client_program():
    path = '20210428_124004.jpg'
    file_data = open(path, 'rb').read()
    file_uploader_client = FileUploaderClient()
    file_params = file_uploader_client.get_file_params(sha256_str="3aaadfc62231f81c3bf29173d0975df9eebd5f9b6662962b7dc34c3f3b657f0f")
    print(file_params)

    file_data = file_uploader_client.get_file_data(
        sha256_str="3aaadfc62231f81c3bf29173d0975df9eebd5f9b6662962b7dc34c3f3b657f0f",
        file_len=file_params["file_len"]
        )
    print(len(file_data))

    file_params = file_uploader_client.get_file_params(sha256_str="3aaadfc62231f81c3bf29173d0975df9eebd5f9b6662962b7dc34c3f3b657f0f")
    print(file_params)
    file_params = file_uploader_client.get_file_params(sha256_str="3aaadfc62231f81c3bf29173d0975df9eebd5f9b6662962b7dc34c3f3b657f0f")
    print(file_params)

    uploaded_resp = file_uploader_client.upload_music(
        file_bytes=file_data,
        image="53",
        author="Test author",
        album="Test album",
        source="deezer",
        source_data={
            "url": "324234",
            "id": 212
        }
    )
    print(uploaded_resp)
    file_params = file_uploader_client.get_file_params(sha256_str="3aaadfc62231f81c3bf29173d0975df9eebd5f9b6662962b7dc34c3f3b657f0f")
    print(file_params)


if __name__ == '__main__':
    client_program()
