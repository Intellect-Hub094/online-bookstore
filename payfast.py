import hashlib
from urllib.parse import urlencode, quote_plus
from flask import current_app


def generate_payfast_signature(data, passphrase):
    # Build the query string maintaining parameter order
    payload = ""
    for key in data:
        # Ensure spaces are encoded as '+' and URL encoding is uppercase
        value = data[key].replace(" ", "+")
        encoded_value = quote_plus(value)
        # PayFast requires uppercase encoding for some characters
        encoded_value = encoded_value.replace("%2f", "%2F").replace("%3a", "%3A")
        payload += f"{key}={encoded_value}&"

    # Remove last ampersand
    payload = payload[:-1]

    # Add passphrase if provided
    if passphrase:
        passphrase_encoded = quote_plus(passphrase)
        passphrase_encoded = passphrase_encoded.replace("%2f", "%2F").replace(
            "%3a", "%3A"
        )
        payload += f"&passphrase={passphrase_encoded}"

    # Generate MD5 hash
    return hashlib.md5(payload.encode()).hexdigest()


def create_payfast_payment(order, user):
    # Order matters for PayFast signature generation!
    data = {
        "merchant_id": current_app.config.get("PAYFAST_MERCHANT_ID"),
        "merchant_key": current_app.config.get("PAYFAST_MERCHANT_KEY"),
        "return_url": current_app.config.get("PAYFAST_RETURN_URL")
        + f"?order_id={order.id}",
        "notify_url": current_app.config.get("PAYFAST_NOTIFY_URL"),
        "m_payment_id": str(order.id),
        "amount": f"{order.total_amount:.2f}",
        "item_name": f"Order{order.id}",
    }
    data["signature"] = generate_payfast_signature(
        data, current_app.config["PAYFAST_PASSPHRASE"]
    )

    return f"https://sandbox.payfast.co.za/eng/process?{urlencode(data)}"
