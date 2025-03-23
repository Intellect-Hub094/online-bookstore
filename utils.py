# utils.py
import random
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def calculate_total_price(cart_items):
    total = 0.0
    for book_id, item in cart_items.items():
        if isinstance(item, dict) and "price" in item and "quantity" in item:
            total += item["price"] * item["quantity"]
        else:
            print(f"Invalid item in cart: {item}")
    return total

def generate_order_code():
    return "ORD-" + str(random.randint(1000, 9999))

def send_confirmation_email(recipient_email, order_code):
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = "Order Confirmation"
        body = f"Your order has been confirmed. Your order code is {order_code}."
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_ADDRESS, recipient_email, message)
        server.quit()
    except Exception as e:
        print("Failed to send the email:", e)