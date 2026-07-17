
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
from datetime import datetime

BASE = Path("/content/drive/MyDrive/FutureMind_Lab_V5")
ORDERS = BASE / "orders" / "orders.json"


class Handler(SimpleHTTPRequestHandler):

    def do_POST(self):

        if self.path == "/api/order":

            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)

            order = json.loads(data.decode("utf-8"))

            orders = json.loads(
                ORDERS.read_text(encoding="utf-8")
            )

            order["date"] = str(datetime.now())

            orders.append(order)

            ORDERS.write_text(
                json.dumps(orders, indent=2),
                encoding="utf-8"
            )

            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()

            self.wfile.write(
                b'{"status":"success"}'
            )

        else:
            self.send_error(404)


print("FutureMind Lab Server running on 8000")

HTTPServer(
    ("0.0.0.0",8000),
    Handler
).serve_forever()
