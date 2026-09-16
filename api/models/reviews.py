from ..utils import db


class Review(db.Model):
    __tablename__ = 'reviews'

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text(), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
