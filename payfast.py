import hashlib
from urllib.parse import urlencode
from flask import current_app

def generate_payfast_signature(data, passphrase):
    data_string = '&'.join([f'{key}={value}' for key, value in sorted(data.items())])
    data_string += f'&passphrase={passphrase}'
    return hashlib.md5(data_string.encode()).hexdigest()

def create_payfast_payment(order, user):
    data = {
        'merchant_id': current_app.config['PAYFAST_MERCHANT_ID'],
        'merchant_key': current_app.config['PAYFAST_MERCHANT_KEY'],
        'return_url': current_app.config['PAYFAST_RETURN_URL'],
        'cancel_url': current_app.config['PAYFAST_CANCEL_URL'],
        'notify_url': current_app.config['PAYFAST_NOTIFY_URL'],
        'name_first': user.first_name,
        'name_last': user.last_name,
        'email_address': user.email,
        'm_payment_id': str(order.id),
        'amount': f'{order.total_amount:.2f}',
        'item_name': f'Order #{order.id}',
    }
    data['signature'] = generate_payfast_signature(data, current_app.config['PAYFAST_PASSPHRASE'])
    return f'https://www.payfast.co.za/eng/process?{urlencode(data)}'
