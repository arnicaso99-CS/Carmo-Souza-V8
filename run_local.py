#!/usr/bin/env python3
"""Run the Carmo-Souza converter locally for free.

This starts a tiny local web server using only Python's standard library and
opens index.html in the browser.

Usage:
    python run_local.py

Then open:
    http://127.0.0.1:8000/index.html
"""
from __future__ import annotations

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
HOST = "127.0.0.1"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print("local:", format % args)


def main() -> int:
    root = Path(__file__).resolve().parent
    index = root / "index.html"
    if not index.exists():
        raise SystemExit("index.html nao encontrado. Rode este comando dentro da pasta do projeto.")

    url = f"http://{HOST}:{PORT}/index.html"
    print("Carmo-Souza V8 rodando localmente e de graça.")
    print(f"Abra: {url}")
    print("Pressione Ctrl+C para parar.")
    webbrowser.open(url)

    with socketserver.TCPServer((HOST, PORT), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor local encerrado.")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
