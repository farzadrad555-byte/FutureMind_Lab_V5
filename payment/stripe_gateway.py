
import stripe

def create_checkout_session(
    secret_key,
    product_name,
    amount,
    currency="usd"
):

    stripe.api_key = secret_key

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data":{
                    "currency":currency,
                    "product_data":{
                        "name":product_name
                    },
                    "unit_amount": int(amount * 100)
                },
                "quantity":1
            }
        ],
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )

    return session.url
