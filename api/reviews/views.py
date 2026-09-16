from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from ..models.courses import Course
from ..models.reviews import Review
from ..models.students import Student


reviews_namespace = Namespace('reviews', description='Namespace for Course Reviews')

review_model = reviews_namespace.model(
    'Review', {
        'student_id': fields.Integer(required=True, description="Student's User ID"),
        'course_id': fields.Integer(required=True, description="Course's ID"),
        'rating': fields.Integer(required=True, description='Course rating from 1 to 5'),
        'review': fields.String(required=True, description='Review text')
    }
)


@reviews_namespace.route('')
class CreateReview(Resource):
    @reviews_namespace.expect(review_model, validate=True)
    @reviews_namespace.doc(description='Review a course --- Student Only!')
    @jwt_required()
    def post(self):
        data = reviews_namespace.payload
        student = Student.query.filter_by(id=get_jwt_identity()).first()
        if not student:
            return {'message': 'Student Only!'}, HTTPStatus.FORBIDDEN
        if str(data['student_id']) != str(get_jwt_identity()):
            return {'message': 'You can only submit your own reviews'}, HTTPStatus.FORBIDDEN

        Course.get_by_id(data['course_id'])

        new_review = Review(
            student_id=data['student_id'],
            course_id=data['course_id'],
            rating=data['rating'],
            review=data['review']
        )
        new_review.save()

        return marshal(new_review, review_model), HTTPStatus.CREATED


@reviews_namespace.route('/courses/<int:course_id>')
class ListCourseReviews(Resource):
    @reviews_namespace.doc(description='Get all reviews for a course')
    @jwt_required()
    def get(self, course_id):
        Course.get_by_id(course_id)
        reviews = Review.query.filter_by(course_id=course_id).order_by(Review.student_id).all()
        if not reviews:
            return {'message': 'Reviews not found'}, HTTPStatus.NOT_FOUND

        return marshal(reviews, review_model), HTTPStatus.OK
