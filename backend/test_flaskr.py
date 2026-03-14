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
            response = self.client.delete("/questions/4")
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

    def test_delete_question_but_not_found(self):
        with self.app.app_context():
            response = self.client.delete("/questions/1000")
            self.assertEqual(response.status_code, 404)

        return
    

    def test_get_questions_by_invalid_category(self):
        with self.app.app_context():
            response = self.client.get("/categories/1000/questions")
            self.assertEqual(response.status_code, 404)

        return 


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
