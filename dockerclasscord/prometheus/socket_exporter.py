#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
SOCKET_HOST = 'classcord'  # Nom du service Docker
SOCKET_PORT = 12345
HTTP_PORT = 9091
REFRESH_INTERVAL = 5  # Secondes

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            # Récupérer les métriques depuis le serveur socket
            try:
                metrics = self.fetch_metrics()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(metrics.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def fetch_metrics(self):
        """Récupère les métriques depuis le serveur socket"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SOCKET_HOST, SOCKET_PORT))
            s.sendall(b"GET_METRICS")
            
            # Réception des données
            chunks = []
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                chunks.append(chunk)
                
                # Si la réponse est complète, on peut sortir
                if len(chunk) < 1024:
                    break
                    
            return b''.join(chunks).decode('utf-8')

def run_server():
    """Démarrer le serveur HTTP pour exposer les métriques à Prometheus"""
    server_address = ('', HTTP_PORT)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Starting metrics exporter on port {HTTP_PORT}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()