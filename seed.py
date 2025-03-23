from werkzeug.security import generate_password_hash
from models import (
    db,
    User,
    Book,
    Cart,
    Order,
    Purchase,
    Wishlist,
    Admin,
    Customer,
    Driver,
    Transaction,
)
from datetime import datetime
from app import app


def clear_data():
    db.session.query(Transaction).delete()
    db.session.query(Wishlist).delete()
    db.session.query(Purchase).delete()
    db.session.query(Order).delete()
    db.session.query(Cart).delete()
    db.session.query(Book).delete()
    db.session.query(Admin).delete()
    db.session.query(Customer).delete()
    db.session.query(Driver).delete()
    db.session.query(User).delete()
    db.session.commit()


def create_sample_data():
    # Create sample users
    admin_user = User(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password=generate_password_hash("adminpass"),
        role="admin",
    )
    customer_user = User(
        first_name="Customer",
        last_name="User",
        email="customer@example.com",
        password=generate_password_hash("customerpass"),
        role="customer",
    )
    driver_user = User(
        first_name="Driver",
        last_name="User",
        email="driver@example.com",
        password=generate_password_hash("driverpass"),
        role="driver",
    )

    db.session.add(admin_user)
    db.session.add(customer_user)
    db.session.add(driver_user)
    db.session.commit()

    admin = Admin(user_id=admin_user.id)
    customer = Customer(user_id=customer_user.id)
    driver = Driver(user_id=driver_user.id, license_number="DRIVER123")

    db.session.add(admin)
    db.session.add(customer)
    db.session.add(driver)
    db.session.commit()

    # Create sample books
    book1 = Book(
        title="Book One",
        author="Author One",
        isbn="ISBN001",
        price=10.99,
        stock=100,
        description="Description for Book One",
    )
    book2 = Book(
        title="Book Two",
        author="Author Two",
        isbn="ISBN002",
        price=15.99,
        stock=50,
        description="Description for Book Two",
    )

    db.session.add(book1)
    db.session.add(book2)
    db.session.commit()

    # Create sample carts
    cart_item1 = Cart(customer_id=customer.id, book_id=book1.id, quantity=2)
    cart_item2 = Cart(customer_id=customer.id, book_id=book2.id, quantity=1)

    db.session.add(cart_item1)
    db.session.add(cart_item2)
    db.session.commit()

    # Create sample orders and purchases
    order = Order(
        customer_id=customer.id,
        order_date=datetime.now(),
        total_amount=36.97,
        status="pending",
    )
    db.session.add(order)
    db.session.commit()

    purchase1 = Purchase(order_id=order.id, book_id=book1.id, quantity=2, price=10.99)
    purchase2 = Purchase(order_id=order.id, book_id=book2.id, quantity=1, price=15.99)

    db.session.add(purchase1)
    db.session.add(purchase2)
    db.session.commit()

    # Create sample wishlists
    wishlist_item = Wishlist(
        customer_id=customer.id, book_id=book1.id, added_date=datetime.now()
    )
    db.session.add(wishlist_item)
    db.session.commit()

    # Create sample transactions
    transaction = Transaction(
        order_id=order.id,
        payment_method="Credit Card",
        transaction_date=datetime.now(),
        amount=36.97,
        status="completed",
    )
    db.session.add(transaction)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        clear_data()
        create_sample_data()
