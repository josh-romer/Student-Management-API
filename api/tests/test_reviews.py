import unittest
from flask_jwt_extended import create_access_token
from .. import create_app
from ..config.config import config_dict
from ..models.courses import Course
from ..models.reviews import Review
from ..models.students import Student
from ..models.studentcourse import StudentCourse
from ..models.teacher import Teacher
from ..utils import db


class ReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()

        self.student = Student(
            identifier='1234', email='student@example.com',
            first_name='Alex', last_name='Smith', password_hash='test',
            admission_no='STD/26/1234'
        )
        self.student.save()
        self.course = Course(name='BCH101', teacher='Prof Smith')
        self.course.save()
        StudentCourse(student_id=self.student.id, course_id=self.course.id).save()
        token = create_access_token(identity=self.student.id)
        self.headers = {'Authorization': f'Bearer {token}'}
        self.data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'rating': 4,
            'review': 'Clear explanations and useful assignments.'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()

    def test_create_and_list_reviews(self):
        response = self.client.post('/reviews', json=self.data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, self.data)
        self.assertEqual(Review.query.one().review, self.data['review'])

        response = self.client.get(
            f'/reviews/courses/{self.course.id}', headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.data])

        other_course = Course(name='CHM101', teacher='Prof Jones')
        other_course.save()
        Review(
            student_id=self.student.id, course_id=other_course.id,
            rating=5, review='Helpful labs.'
        ).save()
        response = self.client.get(
            f'/reviews/courses/{self.course.id}', headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.data])

    def test_cannot_review_as_another_student(self):
        self.data['student_id'] = self.student.id + 1
        response = self.client.post('/reviews', json=self.data, headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.query.count(), 0)

    def test_teacher_cannot_submit_review(self):
        teacher = Teacher(
            identifier='5678', email='teacher@example.com',
            first_name='Sam', last_name='Jones', password_hash='test',
            employee_no='TCH/26/5678'
        )
        teacher.save()
        token = create_access_token(identity=teacher.id)
        response = self.client.post(
            '/reviews', json=self.data,
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.query.count(), 0)

    def test_missing_course(self):
        self.data['course_id'] = self.course.id + 1
        response = self.client.post('/reviews', json=self.data, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            f'/reviews/courses/{self.data["course_id"]}', headers=self.headers
        )
        self.assertEqual(response.status_code, 404)

    def test_required_fields(self):
        for field in self.data:
            with self.subTest(field=field):
                data = dict(self.data)
                del data[field]
                response = self.client.post('/reviews', json=data, headers=self.headers)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.query.count(), 0)

    def test_invalid_field_types(self):
        for field, value in [('student_id', 'one'), ('course_id', 'one'),
                             ('rating', 'good'), ('rating', 4.5), ('review', None)]:
            with self.subTest(field=field, value=value):
                data = dict(self.data, **{field: value})
                response = self.client.post('/reviews', json=data, headers=self.headers)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.query.count(), 0)
