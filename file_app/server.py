import socket
import json
from os import path, makedirs
import selectors
import types
from typing import Optional
from shared.constants import COMMAND_GET_FILE_PARAMS, COMMAND_GET_FILE_DATA, COMMAND_GET_FILES_LIST, COMMAND_UPLOAD_WITH_PARAMS, READY_TO_UPLOAD_RESPONSE, FILE_SERVER_PORT, HASH_DOES_NOT_COMPARE_RESPONSE, ALREADY_EXIST_RESPONSE, SENDED_BYTES_COUNT, SUCCESS_RESPONSE, FILE_NOT_FOUND_RESPONSE, UPLOADING_ERROR_RESPONSE
import time
import hashlib
import os
import math

UPLOAD_FOLDER = os.environ["FILE_FOLDER"]


sel = selectors.DefaultSelector()

def _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT, try_count=5):
    for _ in range(try_count):
        try:
            resp = sock.recv(bytes_count)
            return resp or bytes()
        except BlockingIOError:
            time.sleep(1)


# File read/write
def get_folder(sha256_str: str):
    return sha256_str[:6]


def get_folder_path(sha256_str: str):
    folder_name = get_folder(sha256_str)
    return path.join(UPLOAD_FOLDER, folder_name)


def get_path(sha256_str: str):
    folder_path = get_folder_path(sha256_str)
    return path.join(folder_path, sha256_str)


def is_exist(sha256_str: str):
    file_path = get_path(sha256_str)
    return path.exists(file_path)


def write_file(data_bytes: bytes, params: dict, sha256_str: str):

    folder_path = get_folder_path(sha256_str)
    try:
        makedirs(folder_path, exist_ok=True)
    except FileExistsError:
        pass
    file_path = get_path(sha256_str)
    if params:
        file_path_meta = file_path + '_meta'
        with open(file_path_meta, 'w') as f:
            f.write(json.dumps(params))
    with open(file_path, 'wb') as f:
        f.write(data_bytes)
    return True


def read_file_data(sha256_str: str):
    file_path = get_path(sha256_str)
    try:
        with open(file_path, 'rb') as f:
            item_data = f.read(SENDED_BYTES_COUNT)
            while item_data:
                yield item_data
                item_data = f.read(SENDED_BYTES_COUNT)
    except FileNotFoundError:
        pass


def read_file_params(sha256_str: str):
    file_path = get_path(sha256_str)
    file_path += '_meta'

    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        pass

# End file
def handle_client(conn, address):
    try:
        data_str = conn.recv(SENDED_BYTES_COUNT).decode()
        if not data_str:
            # if data is not received break
            return
        
        data = json.loads(data_str)
        # записываем meta информацию
        errors = []
        for required_field in ["sha256"]:
            if not data.get(required_field):
                errors.apppend(f"Required field {required_field}")
        if errors:
            conn.send(json.dumps(errors).encode())
            return
        
        conn.send(json.dumps(READY_TO_UPLOAD_RESPONSE).encode())


    finally:
        conn.close()


class InputDataValidateException(Exception):
    pass


class CommandNotFoundException(Exception):
    pass


def command_upload_file_with_params(sock, params: dict):
    
    for required_field in ["sha256", "file_len", "file_params_len"]:
        if not params.get(required_field):
            raise InputDataValidateException(f"param {required_field} is required")
    if is_exist(params["sha256"]):
        if not params.pop("overwrite", False):
            sock.send(json.dumps(ALREADY_EXIST_RESPONSE).encode())
            return

    sock.send(json.dumps(READY_TO_UPLOAD_RESPONSE).encode())

    file_params_len = params.pop("file_params_len")
    file_params_bytes = bytes()
    while len(file_params_bytes) < file_params_len:
        item = _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT)
        if not item:
            break
        file_params_bytes += item
    file_params = json.loads(file_params_bytes)
    file_params.update(params)
    sock.send(json.dumps(READY_TO_UPLOAD_RESPONSE).encode())

    file_data = bytes()
    # item = True
    i = 0
    # while len(file_data) < params["file_len"] or i < 1000:
    while len(file_data) < params["file_len"]:
        item = _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT)
        if not item:
            break
        file_data += item

    # for _ in range(0, math.ceil(params["file_len"]/SENDED_BYTES_COUNT)):

        # i+=1
        # item = _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT)

    real_sha_256 = hashlib.sha256(file_data).hexdigest()
    # Проверяем, что хеш соответствует
    if real_sha_256 != params["sha256"]:
        sock.send(json.dumps(HASH_DOES_NOT_COMPARE_RESPONSE).encode())
        return
    is_writed = write_file(params=file_params, data_bytes=file_data, sha256_str=real_sha_256)
    if is_writed:
        sock.send(json.dumps(SUCCESS_RESPONSE).encode())
    else:
        sock.send(json.dumps(UPLOADING_ERROR_RESPONSE).encode())
    
    return True


def command_get_file_params(sock, params: dict):
    # from pudb import remote
    # remote.set_trace(term_size=(180, 39), host='0.0.0.0', port=6910)
    for required_field in ["sha256"]:
        if not params.get(required_field):
            raise InputDataValidateException(f"param {required_field} is required")
    file_params_bytes_data = read_file_params(params["sha256"])
    if not file_params_bytes_data:
        sock.send(json.dumps(ALREADY_EXIST_RESPONSE).encode())
        return
    sock.send(json.dumps({"len": len(file_params_bytes_data)}).encode())
    ready_resp = _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT)
    
    sock.send(file_params_bytes_data)
    return True


def command_get_file_data(sock, params: dict):
    for required_field in ["sha256"]:
        if not params.get(required_field):
            raise InputDataValidateException(f"param {required_field} is required")
    file_bytes_data_iterable = read_file_data(params["sha256"])
    if not file_bytes_data_iterable:
        sock.send(json.dumps(ALREADY_EXIST_RESPONSE).encode())
        return
    for file_bytes_data_item in file_bytes_data_iterable: 
        sock.send(file_bytes_data_item)
    return True

def command_get_files_list(sock, params: dict):
    files_total_list = []
    for _, _, files in os.walk(UPLOAD_FOLDER):
        for file_name in files:
            if not file_name.endswith("_meta"):
                files_total_list.append(file_name)
    sended_bytes = json.dumps(files_total_list).encode()
    sock.send(json.dumps({"len": len(sended_bytes)}).encode())
    ready_resp = _read_from_socket(sock, bytes_count=SENDED_BYTES_COUNT)
    sock.send(sended_bytes)
    return True

COMMANDS_MAPPER = {
    COMMAND_UPLOAD_WITH_PARAMS: command_upload_file_with_params,
    COMMAND_GET_FILE_PARAMS: command_get_file_params,
    COMMAND_GET_FILE_DATA: command_get_file_data,
    COMMAND_GET_FILES_LIST: command_get_files_list,
}


def get_command_and_data_from_bytes(data_bytes: bytes):
    params = json.loads(data_bytes.decode())
    command_name = params.pop("command", None)

    command_function = COMMANDS_MAPPER[command_name]
    if not command_function:
        raise CommandNotFoundException(f"Command with name {command_name}")
    return command_function, params
    

def accept_wrapper(sock):
    sock.setblocking(True)
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    # conn.setblocking(False)
    conn.setblocking(True)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # events = selectors.EVENT_READ
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(SENDED_BYTES_COUNT)  # Should be ready to read
        except Exception as ex:
            recv_data = None
            print('erer')
        if not recv_data:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)                                                                                                    
            sock.close()
            return
        # data.outb += recv_data
        try:
            command_function, params = get_command_and_data_from_bytes(recv_data)
            print(command_function)
            command_function(sock, params)
            # sock.send(json.dumps(SUCCESS_RESPONSE).encode())
        finally:
            pass
            # sel.unregister(sock)
            # sock.close() 
        

    if mask & selectors.EVENT_WRITE:
        # print("selector write")
        pass
        # sock.close()

        # if data.outb:
        #     print(f"Echoing {data.outb!r} to {data.addr}")
        #     sent = sock.send(data.outb)  # Should be ready to write
        #     data.outb = data.outb[sent:]


def server_program():
    # get the hostname
    host = socket.gethostname()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, FILE_SERVER_PORT))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(100)
    server_socket.setblocking(False)

    sel.register(server_socket, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

    # while True:
    #     conn, address = server_socket.accept()  # accept new connection
        
    #     print("Connection from: " + str(address))

if __name__ == '__main__':
    server_program()
