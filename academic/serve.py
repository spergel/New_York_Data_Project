#!/usr/bin/env python3
"""
Simple HTTP server to serve the academic events website locally.
Run this script and visit http://localhost:8000 to view the site.
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

def open_browser():
    """Open the browser after a short delay"""
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Academic Events Website running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {os.path.dirname(os.path.abspath(__file__))}")
        print("📊 Events data loaded from: scraped_events.json")
        print("🔄 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
