import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from trivia import create_app
from trivia.models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Before 1894, basketball games were played with what sort of ball?',
            'answer': 'Soccer ball',
            'difficulty': 3,
            'category': 6
        }

        self.error_question = {
            'question': '',
            'answer': '',
            'difficulty': 3,
            'category': 6
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ### test for endpoint /categories ###
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
    
    ### test for endpoint /questions ###
    ### GET ###
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_405_questions_not_allowed(self):
        res = self.client().get('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'who'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 3)
    
    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['question_created'])
        self.assertTrue(len(data['questions']))
    
    def test_404_if_book_creation_not_allowed(self):
        res = self.client().post('/books', json=self.error_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    ### test for endpoint '/questions/<int:question_id>' ###
    ### DELETE ###
    def test_delete_question(self):
        id_to_delete = self.client().post('/questions', json={'searchTerm': 'before'})
        id_data = json.loads(id_to_delete.data)
        id_to_delete = id_data['questions'][0]['id']
        res = self.client().delete('/questions/' + str(id_to_delete))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == id_to_delete).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id_to_delete)
        self.assertEqual(question, None)
        
    def test_404_if_book_does_not_exist(self):
        res = self.client().delete('/books/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    ### test for endpoint '/categories/<int:cat_id>/questions' ###
    ### GET ###
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    def test_404_sent_requesting_nonexisting_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    ### test for endpoint '/quizzes' ###
    ### POST ###
    def test_get_next_question(self):
        res = self.client().post('/quizzes', json={
                'previous_questions': [],
                'quiz_category': {
                    'type': 'click',
                    'id': 0
                }
            })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    
    def test_quizzes_get_405(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_next_question_422(self):
        res = self.client().post('/quizzes', json={
                'previous_questions': [],
                'quiz_category': {
                    'type': 'click',
                    'id': 100
                }
            })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()