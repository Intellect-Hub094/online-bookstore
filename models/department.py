from extensions import db
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    courses = db.relationship("Course", backref="department", lazy=True)
