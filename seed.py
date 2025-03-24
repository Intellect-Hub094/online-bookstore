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
    book3 = Book(
        id="3",
        title="C# 13 and .NET 9: Modern Cross-Platform Development Fundamentals",
        author="Mark J. Price",
        isbn="ISBN003",
        price=29.99,
        stock=75,
        description="Start building websites and services with ASP.NET Core 9, Blazor, and EF Core 9. Ninth Edition.",
    )

    book4 = Book(
        id="4",
        title="Django 5 By Example",
        author="Antonio Melé",
        isbn="ISBN004",
        price=34.99,
        stock=60,
        description="Build powerful and reliable Python web applications from scratch. Fifth Edition.",
    )

    book5 = Book(
        id="5",
        title="Architecting ASP.NET Core Applications",
        author="Carl-Hugo Marcotte",
        isbn="ISBN005",
        price=39.99,
        stock=45,
        description="An atypical design patterns guide for .NET 8, C#12, and beyond. Third Edition.",
    )

    book6 = Book(
        id="6",
        title="Real-World Web Development with .NET 9",
        author="Mark J. Price",
        isbn="ISBN006",
        price=27.99,
        stock=80,
        description="Build websites and services using mature and proven ASP.NET Core MVC, Web API, and Umbraco CMS.",
    )

    book7 = Book(
        id="7",
        title="The Complete Edition - Software Engineering for Real-Time Systems",
        author="Jim Cooling",
        isbn="ISBN007",
        price=49.99,
        stock=30,
        description="A software engineering perspective toward designing real-time systems.",
    )

    book9 = Book(
        id="9",
        title="Solutions Architect's Handbook",
        author="Saurabh Shrivastava, Neelanjali Srivastav",
        isbn="ISBN009",
        price=44.99,
        stock=55,
        description="Kick-start your career with architecture design principles, strategies, and generative AI techniques. Third Edition.",
    )

    book0 = Book(
        id="0",
        title="Hands-On Software Engineering with Python",
        author="Brian Allbee",
        isbn="ISBN010",
        price=24.99,
        stock=65,
        description="Move beyond basic programming and construct reliable and efficient software with complex code.",
    )

    book1 = Book(
        id="1",
        title="50 Algorithms Every Programmer Should Know",
        author="Imran Ahmad, PhD",
        isbn="ISBN011",
        price=32.99,
        stock=70,
        description="Tackle computer science challenges with classic to modern algorithms in machine learning, software design, data systems, and cryptography. Second Edition.",
    )

    book2 = Book(
        id="2",
        title="Security-Driven Software Development",
        author="Aspen Olmsted",
        isbn="ISBN012",
        price=22.99,
        stock=40,
        description="Learn to analyze and mitigate risks in your software projects.",
    )

    db.session.add(book1)
    db.session.add(book2)
    db.session.add(book3)
    db.session.add(book4)
    db.session.add(book5)
    db.session.add(book6)
    db.session.add(book7)
    db.session.add(book9)
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
