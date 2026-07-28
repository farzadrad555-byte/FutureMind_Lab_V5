
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

from config.payment_config import (
    STRIPE_ENABLED,
    STRIPE_SECRET_KEY,
    CURRENCY
)


BASE = Path("/content/drive/MyDrive/FutureMind_Lab_V6.5_BEFORE_STRIPE_20260724")
ORDERS = BASE / "orders" / "orders.json"

SESSIONS = set()


class Handler(SimpleHTTPRequestHandler):

    def end_headers(self):
        super().end_headers()


    def secure_download(self):

        from urllib.parse import urlparse, parse_qs

        query = parse_qs(
            urlparse(self.path).query
        )

        token = query.get(
            "token",
            [""]
        )[0]


        tokens_file = BASE / "orders" / "download_tokens.json"


        if not tokens_file.exists():

            self.send_error(404)
            return


        tokens = json.loads(
            tokens_file.read_text(
                encoding="utf-8"
            )
        )


        valid = None

        for item in tokens:

            if item.get("token") == token and item.get("status") == "ACTIVE":

                valid = item
                break


        # Check PAID order status

        if valid:

            orders_file = BASE / "orders" / "orders.json"

            if orders_file.exists():

                orders = json.loads(
                    orders_file.read_text(
                        encoding="utf-8"
                    )
                )

                paid = False

                for order in orders:

                    if (
                        order.get("order_id") == valid.get("order_id")
                        and order.get("status") == "PAID"
                    ):
                        paid = True
                        break


                if not paid:

                    self.send_error(403)
                    return


        if not valid:

            self.send_error(403)

            return


        file_path = (
            BASE /
            "downloads" /
            "Hunter-X_Professional.zip"
        )


        if not file_path.exists():

            self.send_error(404)

            return


        # Download Limit V6.2

        MAX_DOWNLOADS = 3

        history_file = BASE / "orders" / "download_history.json"

        if history_file.exists():

            history_check = json.loads(
                history_file.read_text(
                    encoding="utf-8"
                )
            )

        else:

            history_check = []

        download_count = sum(
            1 for item in history_check
            if item.get("token") == token
        )

        if download_count >= MAX_DOWNLOADS:
            self.send_error(403)
            return


        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/zip"
        )

        self.end_headers()


        # Save Download History V6.2

        history_file = BASE / "orders" / "download_history.json"

        if history_file.exists():

            history = json.loads(
                history_file.read_text(
                    encoding="utf-8"
                )
            )

        else:

            history = []


        history.append({

            "order_id": valid.get("order_id"),

            "product_id": valid.get("product_id"),

            "token": token,

            "date": str(datetime.now()),

            "status": "DOWNLOADED"

        })


        history_file.write_text(

            json.dumps(
                history,
                indent=2,
                ensure_ascii=False
            ),

            encoding="utf-8"

        )


        with open(file_path,"rb") as f:

            self.wfile.write(
                f.read()
            )


    def do_GET(self):

        if self.path.startswith("/api/secure-download"):

            return self.secure_download()




        if self.path.startswith("/api/download-info"):

            from urllib.parse import urlparse, parse_qs

            query = parse_qs(
                urlparse(self.path).query
            )

            token = query.get("token", [""])[0]

            tokens_file = BASE / "orders" / "download_tokens.json"

            if tokens_file.exists():
                tokens = json.loads(
                    tokens_file.read_text(encoding="utf-8")
                )
            else:
                tokens = []


            valid = None

            for item in tokens:
                if item.get("token") == token:
                    valid = item
                    break


            if not valid:

                response = {
                    "status": "error",
                    "message": "Invalid token"
                }

            else:

                history_file = BASE / "orders" / "download_history.json"

                if history_file.exists():
                    history = json.loads(
                        history_file.read_text(encoding="utf-8")
                    )
                else:
                    history = []


                count = sum(
                    1 for x in history
                    if x.get("token") == token
                )


                response = {
                    "status": "success",
                    "order_id": valid.get("order_id"),
                    "product_id": valid.get("product_id"),
                    "downloads": count,
                    "limit": 3,
                    "remaining": max(0, 3-count),
                    "token_status": valid.get("status")
                }


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

            return

        if self.path.startswith("/api/download"):

            from urllib.parse import urlparse, parse_qs

            query = parse_qs(
                urlparse(self.path).query
            )

            product_id = query.get(
                "product_id",
                ["unknown"]
            )[0]

            downloads = {
                "hunter-x-v44":
                "Hunter-X_Professional.zip",

                "science-ai-pack":
                "Science_Teacher_AI_Pack.zip",

                "math-ai-pack":
                "Math_Teacher_AI_Pack.zip"
            }

            if product_id in downloads:

                response = {
                    "status": "success",
                    "product_id": product_id,
                    "download":
                    "/downloads/" + downloads[product_id]
                }

            else:

                response = {
                    "status": "error",
                    "message": "Product not found"
                }

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

            return

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



        # Payment Request V6.5 Stripe Ready
        if self.path == "/api/payment/request":

            payment_id = "PAY-" + secrets.token_hex(4).upper()

            response = {
                "status": "success",
                "payment_id": payment_id,
                "gateway": "TEST",
                "message": "Payment gateway ready"
            }

            if STRIPE_ENABLED:

                response["gateway"] = "STRIPE"
                response["message"] = "Stripe payment initialized"

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

            return


        # Payment Confirm V6.4

        if self.path == "/api/payment/confirm":

            order_id = body.get("order_id")

            orders = json.loads(
                ORDERS.read_text(
                    encoding="utf-8"
                )
            )

            found = False

            for order in orders:

                if order.get("order_id") == order_id:

                    order["status"] = "PAID"
                    found = True
                    break


            if found:


                # Auto Token Creation V6.4 FINAL

                token = secrets.token_hex(16)

                tokens_file = BASE / "orders" / "download_tokens.json"


                if tokens_file.exists():

                    tokens = json.loads(
                        tokens_file.read_text(
                            encoding="utf-8"
                        )
                    )

                else:

                    tokens = []


                tokens.append({

                    "order_id": order_id,

                    "product_id": order.get("product_id"),

                    "token": token,

                    "status": "ACTIVE",

                    "date": str(datetime.now())

                })



                # Email Logger Auto Connect V6.4

                email_log_file = BASE / "emails" / "email_log.json"


                if email_log_file.exists():

                    email_logs = json.loads(
                        email_log_file.read_text(
                            encoding="utf-8"
                        )
                    )

                else:

                    email_logs = []


                email_logs.append({

                    "order_id": order_id,

                    "email": order.get("email"),

                    "product": order.get("product"),

                    "portal_link":
                    "/pages/download.html?token=" + token,

                    "status": "READY",

                    "date": str(datetime.now())

                })


                email_log_file.parent.mkdir(
                    exist_ok=True
                )


                email_log_file.write_text(

                    json.dumps(
                        email_logs,
                        indent=2,
                        ensure_ascii=False
                    ),

                    encoding="utf-8"

                )


                tokens_file.write_text(

                    json.dumps(
                        tokens,
                        indent=2,
                        ensure_ascii=False
                    ),

                    encoding="utf-8"

                )

                ORDERS.write_text(
                    json.dumps(
                        orders,
                        indent=2,
                        ensure_ascii=False
                    ),
                    encoding="utf-8"
                )

                response = {
                    "status": "success",
                    "order_id": order_id,
                    "payment_status": "PAID",
                }

            else:

                response = {
                    "status": "error",
                    "message": "Order not found"
                }


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

            return


        # Customer Order
        if self.path == "/api/order":

            orders = json.loads(
                ORDERS.read_text(encoding="utf-8")
            )

            order_id = "FM-" + secrets.token_hex(4).upper()

            body["order_id"] = order_id
            body["date"] = str(datetime.now())

            if "product_id" not in body or body["product_id"] == "unknown":

                product_name = body.get("product", "")

                if product_name == "Hunter-X V44 Professional":
                    body["product_id"] = "hunter-x-v44"

                elif product_name == "Science Teacher AI Pack":
                    body["product_id"] = "science-ai-pack"

                elif product_name == "Math Teacher AI Pack":
                    body["product_id"] = "math-ai-pack"

                else:
                    body["product_id"] = "unknown"

            if "currency" not in body:
                body["currency"] = "USD"

            if "payment_method" not in body:
                body["payment_method"] = "TEST"

            if "status" not in body:
                body["status"] = "PENDING"

            orders.append(body)

            ORDERS.write_text(
                json.dumps(
                    orders,
                    indent=2,
                    ensure_ascii=False
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




        # Product Download API V6
        if self.path.startswith("/api/download"):

            from urllib.parse import urlparse, parse_qs

            query = parse_qs(
                urlparse(self.path).query
            )

            product_id = query.get(
                "product_id",
                ["unknown"]
            )[0]


            downloads = {

                "hunter-x-v44":
                "Hunter-X_Professional.zip",

                "science-ai-pack":
                "Science_Teacher_AI_Pack.zip",

                "math-ai-pack":
                "Math_Teacher_AI_Pack.zip"

            }


            if product_id in downloads:

                response = {

                    "status": "success",

                    "product_id": product_id,

                    "download":
                    "/downloads/" + downloads[product_id]

                }

            else:

                response = {

                    "status": "error",

                    "message":
                    "Product not found"

                }


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()


            self.wfile.write(
                json.dumps(response)
                .encode()
            )

            return


        self.send_error(404)



print("FutureMind Lab Security Server V2 running on 8000")


HTTPServer(
    ("0.0.0.0",8000),
    Handler
).serve_forever()
