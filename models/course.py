from extensions import db
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey("department.id"), nullable=False
    )
    books = db.relationship("Book", backref="course", lazy=True)
