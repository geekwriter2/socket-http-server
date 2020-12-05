""" a simple server"""

import socket
import sys
import traceback
import os
# pylint: disable=C0103
# pylint: disable=R0101
# pylint: disable=R0912
# pylint: disable=bare-except
# cd C:\Users\mimcdona\Dropbox\UW\UW-Python230_Project\socket-http-server
# python -u http_server.py

WEB_DIR = os.getcwd() + '\\webroot'
FILE_TYPES_DICT = {'html': 'text/html', 'htm': 'text/html',
                   'js': 'text/javascript', 'py': 'text/python',
                   'gif': 'image/gif', 'png': 'image/png',
                   'txt': 'text/plain', 'ico': 'image/ico',
                   'jpeg': 'image/jpeg', 'jpg': 'image/jpeg'}
PROTOCOLS_LIST = ['http/1.0', 'http/1.1', 'http/2.0']


def response_ok(body=b"<html>"
                     b"<head><title>Hello World</title></head>"
                     b"<body></body>"
                     b"</html>", mimetype=b"text/html"):
    """define a header for an ok response"""

    header = b'HTTP/1.1 200 OK'
    line_feed = b'\r\n'
    content_type = b'Content-Type: ' + mimetype
    response = b''.join([header, line_feed, content_type, line_feed, line_feed, body])
    return response


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"HTTP/1.1 405 Method Not Allowed\n"


def response_not_found():
    """Returns a 404 Not Found response"""

    return b"HTTP/1.1 404 Not Found\n"


def parse_request(request):
    """parse the server request"""

    request_path = ''
    test_for_get = request[0:3]
    if test_for_get == 'GET':
        request_path = request[4:]
        request_path = request_path[:-8]
        request_path = request_path.strip()
    else:
        raise NotImplementedError("GET only implemented")
    return request_path


def response_path(path):
    """create a response path"""

    file_type = ''
    content = ''
    mime_type = ''
    path_split = path.split(' ')
    path = path_split[0]
    # directory request
    if path[-1] == '/':
        try:
            for subdir, dirs, files in os.walk(WEB_DIR + path):
                print(dirs)
                for file in files:
                    subdir = subdir.replace(WEB_DIR + '/', '')
                    content += os.path.join(subdir, file)  + '\r\n'
                    # content += subdir + file
            content = content.encode('utf8')
            mime_type = b'text/plain'
        except NameError:
            content = '404 directory not found'
    # file request
    elif '.' in path:
        path_words = path.split()
        # strip protocol
        results = [word for word in path_words if word.lower() not in PROTOCOLS_LIST]
        path = ' '.join(results)
        # remove webroot
        path = path.replace('/webroot', '')
        path = path.replace('webroot', '')
        # noinspection PyTypeChecker
        content_dict = dict(x.split(".") for x in path.split("&"))
        if len(content_dict.items()) == 1:
            for k, v in content_dict.items():
                file_type = v
                print(k)
        else:
            mime_type = ''
            content = ''
            raise NameError('404 malformed request')
        if file_type in FILE_TYPES_DICT:
            mime_type = FILE_TYPES_DICT.get(file_type)
            mime_type = mime_type.encode('utf8')
        else:
            content = b'not implemented'
            mime_type = b'not implemented'
            raise NameError('404 filetype not handled')
        # handle directory paths
        try:
            with open(WEB_DIR + path, 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            raise NameError('404 file not found')

    # not a page request or a directory request
    else:
        raise NameError('404 request type not handled')

    return content, mime_type


def server(log_buffer=sys.stderr):
    """boot server"""

    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break
                try:
                    path = parse_request(request)
                except NotImplementedError:
                    path = 'NotImplementedError'
                try:
                    content, mime_type = response_path(path)
                except NameError:
                    content = 'NameError'
                    mime_type = ''
                if path == 'NotImplementedError':
                    response = response_method_not_allowed()
                elif content == 'NameError':
                    response = response_not_found()
                else:
                    response = response_ok(body=content, mimetype=mime_type)
                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close()
    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)
