from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import parse_qs
from fyres_start import *
import threading
import time
import ssl
from logger import *

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        auth_code = None
        query_string = self.path.split('?', 1)[-1]
        print(f"Received GET request with query string: {query_string}")
        # Parse the query string
        query_params = parse_qs(query_string)
        # Print the extracted query parameters
        for key, values in query_params.items():
            print(f"{key}: {values[0]}")
            if key == "auth_code" :
                if not auth_code:                    
                    auth_code = values[0]                

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Request received and processed successfully')
        if auth_code:
            generate_access_token(auth_code)
            stop_server()

class StoppableHTTPSServer(TCPServer):
    allow_reuse_address = True

def start_server():
    global httpd
    httpd = StoppableHTTPSServer(('127.0.0.1', 443), MyHandler)  # Change the port to 443 for HTTPS

    # Replace 'cert.pem' and 'key.pem' with your SSL certificate and private key paths
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='ssl\cert.pem', keyfile='ssl\key.pem', server_side=True)

    print('Server listening on https://127.0.0.1:443/')

    # Start the server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

def stop_server():
    if httpd:
        print('Stopping the server...')
        httpd.shutdown()
        httpd.server_close()
        print('Server stopped.')
        
        

if __name__ == '__main__':
    start_server()
