import os
import unittest

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "kirklincoln"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        with self.app.app_context():
            response = self.client.get("/categories")

            self.assertEqual(response.status_code, 200)

            data = response.get_json()

            self.assertTrue(data.get("categories"))

        return

    def test_get_questions(self):
        with self.app.app_context():
            response = self.client.get("/questions?page=1")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("questions"))
            self.assertTrue(data.get("total_questions"))
            self.assertTrue(data.get("categories"))
            self.assertTrue(data.get("current_category") == None)

        return

    def test_create_questions(self):
        with self.app.app_context():
            response = self.client.post("/questions", json={
                'question': 'What is 2+2?',                                                                                                                                                                                                                                            
                'answer': '4',                                                                                                                                                                                                                                                         
                'category': '1',                                                                                                                                                                                                                                                       
                'difficulty': 1   
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("success"))
            self.assertTrue(data.get("message"))

        return

    def test_delete_question(self):
        with self.app.app_context():
            # First create a question to delete
            question = Question(
                question='Test question to delete',
                answer='Test answer',
                category='1',
                difficulty=1
            )
            question.insert()
            question_id = question.id

            # Now delete it
            response = self.client.delete(f"/questions/{question_id}")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("success"))
            self.assertTrue(data.get("message"))

        return
    
    def test_search_questions(self):
        with self.app.app_context():
            response = self.client.post("/questions/search", json={
                "searchTerm": "title"
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("questions"))
            self.assertTrue(data.get("total_questions"))
            self.assertTrue(data.get("current_category") == None)

        return 
    
    def test_get_questions_by_category(self):
        with self.app.app_context():
            response = self.client.get("/categories/1/questions")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("questions"))
            self.assertTrue(data.get("total_questions"))
            self.assertTrue(data.get("current_category"))

        return 

    def test_play_quiz(self):
        with self.app.app_context():
            response = self.client.post("/quizzes", json={
                "previous_questions": [20],
                "quiz_category": {
                    "id": 1,
                    "type": "Science"
                }
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("question"))
            self.assertTrue(data.get("previousQuestions"))

        return

    # Deleting Failures
    def test_fails_to_delete_question(self):
        with self.app.app_context():
            response = self.client.delete("/questions/1000")
            self.assertEqual(response.status_code, 404)

        return
    
    def test_fails_with_repeating_deletes(self):
        with self.app.app_context():
            # First create a question to delete
            question = Question(
                question='Test question for repeat delete',
                answer='Test answer',
                category='1',
                difficulty=1
            )
            question.insert()
            question_id = question.id

            # First delete should succeed
            response = self.client.delete(f"/questions/{question_id}")
            self.assertEqual(response.status_code, 200)

            # Second delete should fail with 404
            response = self.client.delete(f"/questions/{question_id}")
            self.assertEqual(response.status_code, 404)
        return

    # Questions By Categories Failures
    def test_fails_to_get_questions_by_invalid_category(self):
        with self.app.app_context():
            response = self.client.get("/categories/1000/questions")
            self.assertEqual(response.status_code, 404)

        return 

    def test_fail_to_get_questions_with_post_request(self):
        with self.app.app_context():
            response = self.client.post("/categories/1000/questions")
            self.assertEqual(response.status_code, 405)

        return 

    # Categories Failures
    def test_fails_to_get_categories_with_invalid_method(self):
        with self.app.app_context():
            response = self.client.post("/categories")
            self.assertEqual(response.status_code, 405)

        return 

    def test_fail_to_get_categories_with_invalid_query_params(self):
        with self.app.app_context():
            response = self.client.get("/categories?page=1&malicious_param=123")
            self.assertEqual(response.status_code, 401)

        return 

    # Questions Failures
    def test_fails_to_get_questions_with_invalid_query_params(self):
        with self.app.app_context():
            response = self.client.get("/questions?page=1&malicious_param=123")
            self.assertEqual(response.status_code, 401)

        return 

    def test_fail_to_get_categories_with_page_out_of_range(self):
        with self.app.app_context():
            response = self.client.get("/questions?page=1000")
            self.assertEqual(response.status_code, 404)

        return 

    # Question Creation Failures
    def test_fails_to_post_question_with_missing_request_fields(self):
        with self.app.app_context():
            response = self.client.post("/questions")
            self.assertEqual(response.status_code, 415)

        return 

    def test_fail_to_get_categories_with_extra_request_body_fields(self):
        with self.app.app_context():
            response = self.client.post("/questions", json={
                "question": "My incredible question",
                "answer": "My incredible answer",
                "category": "2",
                "difficulty": 1,
                "malicious_code_field": "function(){() => setTimeout(() => {}, 10000000)}"
            })
            self.assertEqual(response.status_code, 415)

        return 

    # Question Search Failures
    def test_fails_to_search_for_questions(self):
        with self.app.app_context():
            response = self.client.post("/questions/search", json={
                "searchTerm": "rm -rf /" 
            })
            self.assertEqual(response.status_code, 415)

        return 

    def test_fail_to_post_question_with_no_search_term(self):
        with self.app.app_context():
            response = self.client.post("/questions", json={
                "searchTerm": ""
            })
            self.assertEqual(response.status_code, 415)

        return

    def test_fail_to_fetch_quizzes_with_invalid_category(self):
        with self.app.app_context():
            response = self.client.post("/quizzes", json={
                "quiz_category": {"id": 100000000},
                "previous_questions": []
            })
            self.assertEqual(response.status_code, 404)

        return  
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
