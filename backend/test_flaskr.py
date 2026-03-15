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

    # Claude AI helped with proof-reading tests and providing formatting with banners and comments.
    # ===========================================
    # GET /categories - Success and Failure Tests
    # ===========================================
    def test_get_categories_success(self):
        """Test successful retrieval of all categories"""
        with self.app.app_context():
            response = self.client.get("/categories")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("categories", data)
            self.assertTrue(len(data["categories"]) > 0)

    def test_get_categories_wrong_method(self):
        """Test failure when using wrong HTTP method (POST instead of GET)"""
        with self.app.app_context():
            response = self.client.post("/categories")
            self.assertEqual(response.status_code, 405)

    # ===========================================
    # GET /questions - Success and Failure Tests
    # ===========================================
    def test_get_questions_success(self):
        """Test successful retrieval of paginated questions"""
        with self.app.app_context():
            response = self.client.get("/questions?page=1")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("questions", data)
            self.assertIn("total_questions", data)
            self.assertIn("categories", data)
            self.assertIn("current_category", data)

    def test_get_questions_beyond_valid_page(self):
        """Test requesting a page beyond available questions returns 404"""
        with self.app.app_context():
            response = self.client.get("/questions?page=1000")
            self.assertEqual(response.status_code, 404)

            data = response.get_json()
            self.assertFalse(data.get("success"))

    # ===========================================
    # DELETE /questions/<id> - Success and Failure Tests
    # ===========================================
    def test_delete_question_success(self):
        """Test successful deletion of a question"""
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

    def test_delete_question_not_found(self):
        """Test deletion fails with 404 for non-existent question"""
        with self.app.app_context():
            response = self.client.delete("/questions/99999")
            self.assertEqual(response.status_code, 404)

            data = response.get_json()
            self.assertFalse(data.get("success"))

    # ===========================================
    # POST /questions - Success and Failure Tests
    # ===========================================
    def test_create_question_success(self):
        """Test successful creation of a new question"""
        with self.app.app_context():
            response = self.client.post("/questions", json={
                'question': 'What is the capital of France?',
                'answer': 'Paris',
                'category': '3',
                'difficulty': 1
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertTrue(data.get("success"))

    def test_create_question_no_body(self):
        """Test creation fails when no JSON body is provided"""
        with self.app.app_context():
            response = self.client.post("/questions")
            # Flask returns 415 Unsupported Media Type when Content-Type is missing
            self.assertEqual(response.status_code, 415)

    # ===========================================
    # POST /questions/search - Success and Failure Tests
    # ===========================================
    def test_search_questions_success(self):
        """Test successful search for questions"""
        with self.app.app_context():
            response = self.client.post("/questions/search", json={
                "searchTerm": "title"
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("questions", data)
            self.assertIn("total_questions", data)

    def test_search_questions_no_results(self):
        """Test search with term that matches nothing returns empty list"""
        with self.app.app_context():
            response = self.client.post("/questions/search", json={
                "searchTerm": "xyznonexistentterm123"
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(len(data["questions"]), 0)
            self.assertEqual(data["total_questions"], 0)

    # ===========================================
    # GET /categories/<id>/questions - Success and Failure Tests
    # ===========================================
    def test_get_questions_by_category_success(self):
        """Test successful retrieval of questions by category"""
        with self.app.app_context():
            response = self.client.get("/categories/1/questions")
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("questions", data)
            self.assertIn("total_questions", data)
            self.assertIn("current_category", data)

    def test_get_questions_by_category_not_found(self):
        """Test retrieval fails with 404 for invalid category"""
        with self.app.app_context():
            response = self.client.get("/categories/9999/questions")
            self.assertEqual(response.status_code, 404)

            data = response.get_json()
            self.assertFalse(data.get("success"))

    # ===========================================
    # POST /quizzes - Success and Failure Tests
    # ===========================================
    def test_play_quiz_success(self):
        """Test successful quiz play returns a random question"""
        with self.app.app_context():
            response = self.client.post("/quizzes", json={
                "previous_questions": [],
                "quiz_category": {
                    "id": 1,
                    "type": "Science"
                }
            })
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("question", data)

    def test_play_quiz_invalid_category(self):
        """Test quiz fails with 404 for non-existent category"""
        with self.app.app_context():
            response = self.client.post("/quizzes", json={
                "previous_questions": [],
                "quiz_category": {
                    "id": 99999,
                    "type": "Invalid"
                }
            })
            self.assertEqual(response.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
