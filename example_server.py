import selectors
import socket
import time

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(True)
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, read)

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    print("I am here!")
    # import pdb; pdb.set_trace()
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)  # Hope it won't block
        time.sleep(4)

        second_data = conn.recv(1000)
        print('hi')
        print(second_data.decode())
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(('localhost', 1234))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)


while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
