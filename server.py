import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(__file__), "webapp")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Mini App serveri ishga tushdi: http://localhost:{PORT}")
        print("To'xtatish uchun: Ctrl + C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer to'xtatildi.")
