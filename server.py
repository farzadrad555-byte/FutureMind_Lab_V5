
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
from datetime import datetime
import secrets
import sys

sys.path.append(
    "/content/drive/MyDrive/FutureMind_Lab_V5/admin/security"
)

from auth import check_login


BASE = Path("/content/drive/MyDrive/FutureMind_Lab_V5")
ORDERS = BASE / "orders" / "orders.json"

SESSIONS = set()


class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):

        length = int(self.headers.get("Content-Length",0))
        data = self.rfile.read(length)

        try:
            body = json.loads(data.decode("utf-8"))
        except:
            body = {}

        # Admin Login
        if self.path == "/api/login":

            username = body.get("username")
            password = body.get("password")

            if check_login(username,password):

                token = secrets.token_hex(16)
                SESSIONS.add(token)

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.end_headers()

                self.wfile.write(
                    json.dumps({
                        "status":"success",
                        "token":token
                    }).encode()
                )

            else:

                self.send_response(401)
                self.end_headers()

            return


        # Customer Order
        if self.path == "/api/order":

            orders = json.loads(
                ORDERS.read_text(encoding="utf-8")
            )

            body["date"] = str(datetime.now())

            orders.append(body)

            ORDERS.write_text(
                json.dumps(
                    orders,
                    indent=2
                ),
                encoding="utf-8"
            )


            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                b'{"status":"success"}'
            )

            return


        self.send_error(404)



print("FutureMind Lab Security Server V2 running on 8000")


HTTPServer(
    ("0.0.0.0",8000),
    Handler
).serve_forever()
