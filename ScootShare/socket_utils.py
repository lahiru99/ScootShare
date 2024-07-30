#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/struct.html
import socket, json, struct



#Methods showen in class, helped alot with figuring this out, need to double check its all good


def sendJson(target_socket: socket.socket, object):
    jsonString = json.dumps(object)
    data = jsonString.encode("utf-8")
    jsonLength = struct.pack("!i", len(data))
    target_socket.sendall(jsonLength)
    target_socket.sendall(data)



def recvJson(target_socket: socket.socket):
    # Receive the 4-byte message length
    length_bytes = target_socket.recv(4) 
    if not length_bytes:
        return None  # No data received

    jsonLength = struct.unpack("!i", length_bytes)[0] #We have the length of the message

    # Initialize a buffer for the JSON data
    buffer = bytearray()
    while jsonLength > 0:
        # Receive a chunk of data
        chunk = target_socket.recv(min(jsonLength, 4096))
        if not chunk:
            return None  # Incomplete data received

        buffer.extend(chunk)
        jsonLength -= len(chunk)

    # Decode the received data and parse it into a Python dictionary
    jsonString = buffer.decode("utf-8")
    return json.loads(jsonString) 




#Consider deleting once the above one is fully tested
def recvJsonFixed(target_socket: socket.socket):
    buffer = target_socket.recv(4) #This was 4, changed the size to fix larger msg's
    jsonLength = struct.unpack("!i", buffer)[0] #Need to disucss this as i am having issues unpacking

    # Reference: https://stackoverflow.com/a/15964489/9798310
    buffer = bytearray(jsonLength)
    view = memoryview(buffer)
    while jsonLength:
        nbytes = target_socket.recv_into(view, jsonLength)
        view = view[nbytes:]
        jsonLength -= nbytes

    jsonString = buffer.decode("utf-8")
    return json.loads(jsonString)  #parses it into a Python dictionary before returning