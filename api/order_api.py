
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from datetime import datetime

BASE = Path("/content/drive/MyDrive/FutureMind_Lab_V5")
ORDERS = BASE / "orders" / "orders.json"


class OrderHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        if self.path.endswith("/order"):

            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)

            order = json.loads(data.decode("utf-8"))

            orders = json.loads(
                ORDERS.read_text(encoding="utf-8")
            )

            order["date"] = str(datetime.now())

            orders.append(order)

            ORDERS.write_text(
                json.dumps(
                    orders,
                    indent=2
                ),
                encoding="utf-8"
            )

            self.send_response(200)
            self.end_headers()

            self.wfile.write(
                b'{"status":"success"}'
            )

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(
    ("0.0.0.0", 9001),
    OrderHandler
)

print("Order API running on port 9000")

server.serve_forever()
