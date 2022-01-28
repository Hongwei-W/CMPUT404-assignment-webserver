#  coding: utf-8 
import os
import socketserver

# Copyright 2022 Abram Hindle, Eddie Antonio Santos, Hongwei Wang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        self.data_list = list(self.data.decode().split(" "))
        self.command = self.data_list[0]
        self.path = self.data_list[1]
        if self.command != "GET":
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n405 Method Not Allowed", 'utf-8'))
            return          
        
        if self.command == "GET":
            self.path = "./www" + self.path

            # citations:
            # https://vimsky.com/examples/usage/python-os-path-commonprefix-method.html
            # https://blog.csdn.net/rainshine1190/article/details/85165059
            # https://stackoverflow.com/questions/45188708/how-to-prevent-directory-traversal-attack-from-python-code
            # Note: os.path.realpath() return the path for the actual file, not the Alias (Mac OS) kinda thing 
            if os.path.commonprefix((os.path.realpath(self.path), (os.path.realpath('./www/')))) != os.path.realpath('./www/'):
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n404 Not Found, bad user", 'utf-8'))
                return  
            if os.path.isfile(self.path):
                if '.html' in self.path:
                    content, len_content = self.readfile()
                    self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nServer: hongwei2/1.0\r\nContent-Type: text/html\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + content, 'utf-8'))
                elif '.css' in self.path:
                    content, len_content = self.readfile()
                    self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nServer: hongwei2/1.0\r\nContent-Type: text/css\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + content, 'utf-8'))
                else:
                    rpy_msg = "404 Not Found"
                    len_content = self.length_in_bytes(rpy_msg)
                    self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nServer: hongwei2/1.0\r\nContent-Type: text/plain\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + rpy_msg, 'utf-8'))
            elif os.path.isdir(self.path):
                if self.path[-1] == '/':
                    self.path += 'index.html'
                    content, len_content = self.readfile()
                    self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nServer: hongwei2/1.0\r\nContent-Type: text/html\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + content, 'utf-8'))
                else:
                    rpy_msg = "301 Moved Permanently"
                    len_content = self.length_in_bytes(rpy_msg)
                    self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nServer: hongwei2/1.0\r\nContent-Type: text/plain\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + rpy_msg, 'utf-8'))
            else:
                rpy_msg = "404 Not Found"
                len_content = self.length_in_bytes(rpy_msg)
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nServer: hongwei2/1.0\r\nContent-Type: text/plain\r\nContent-Length: }" + len_content + "\r\nConnection: close\r\n\r\n" + rpy_msg, 'utf-8'))
            return
    
    def readfile(self):
        f = open(self.path)
        content = f.read()
        f.close()
        return content, self.length_in_bytes(content)
    
    def length_in_bytes(self, s):
        # citation https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes/30686735
        return str(len(s.encode('utf-8')))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
