from extensions import db
# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)