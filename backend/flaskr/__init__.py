from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
import os
import string

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(
        app,
        origins=["*"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    with app.app_context():
        db.create_all()

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def enable_access_control_allow(response):
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS,PUT')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response

    """
    Endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def fetch_all_available_categories():
        if len(request.args) > 1:
            abort(401)

        categories = Category.query.all()
        result_dict = {}
        for category in categories:
            result_dict[str(category.id)] = str(category.type)

        return jsonify({
            "categories": result_dict
        })


    """
    Endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def paginate_available_questions():
        if len(request.args) >= 2:
            abort(401)

        page_number = int(request.args.get("page", "1"))
        questions = Question.query.all()

        if page_number > len(questions) / 10:
            abort(404)

        categories = Category.query.all()
        length = len(questions)
        start = min((page_number - 1) * QUESTIONS_PER_PAGE, len(questions))
        end = min(start + QUESTIONS_PER_PAGE, len(questions))
        paginated_questions = questions[start:end]

        return jsonify({
            "questions": [q.format() for q in paginated_questions],
            "total_questions": length,
            "categories": {str(cat.id): str(cat.type) for cat in categories},
            "current_category": None
        })

    """
    Endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question_by_id(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()

            return jsonify({
                "success": True,
                "message": "Successfully deleted the question!"
            }), 200

        except Exception as e:
            db.session.rollback()
            abort(404)

    """
    Endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_new_question():
        req = request.get_json()
        if len(req) != 4:
            abort(415)
        question = Question(
            req.get("question"),
            req.get("answer"),
            req.get("category"),
            req.get("difficulty")
        )
        question.insert() 

        return jsonify({
            "success": True,
            "message": "Successfully submitted the question!"
        }), 200
    """
    Endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        data = request.get_json()
        search_string = data.get("searchTerm", "")
        if len(search_string) <= 0:
            abort(401)

        for punc in string.punctuation:
            if punc in search_string:
                print(punc)
                abort(415)
        matching_questions = Question.query.filter(Question.question.ilike(f'%{search_string}%')).all()
        length = len(matching_questions) 
        return jsonify({
            "questions": [q.format() for q in matching_questions],
            "total_questions": length,
            "current_category": None,
        })

    """
    Endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def fetch_questions_by_category_id(category_id):
        if len(request.args) > 1:
            abort(401)

        questions = []
        current_category = ""

        try:
            current_category = fetch_all_available_categories().get_json()["categories"][str(category_id)]
            questions = Question.query.filter(Question.category == category_id).all()
        except Exception as e:
            abort(404)

        length = len(questions)
        return jsonify({
            "questions": [q.format() for q in questions],
            "total_questions": length,
            "current_category": current_category,
        })
        

    """
    Endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def fetch_random_questions_for_quiz():
        data = request.get_json()
        previous_questions = data.get("previous_questions")
        quiz_category = data.get("quiz_category").get('id')

        num_of_categories = len(Category.query.all())
        if int(quiz_category) > num_of_categories:
            abort(404)
        questions = []
        if quiz_category == 0:
            questions = Question.query.filter(
                Question.id.notin_(previous_questions)
            ).all()
        else:
            questions = Question.query.filter(
                Question.category == quiz_category
            ).filter(
                Question.id.notin_(previous_questions)
            ).all()

        length = len(questions)
        if length == 0:
            return jsonify({
                "question": None
            })

        target = random.randint(0,length - 1) if length - 1 > 0 else 0
        result = questions[target]
        previous_questions.append(result.id)

        return jsonify({
            "previousQuestions": previous_questions,
            "question": result.format()
        })

    """
    Error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "message": "User is forbidden to access this resource."
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource was not found."
        }), 404
    
    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            "message": "Route not callable with selected method."
        }), 405
    
    @app.errorhandler(415)
    def missing_request_body(error):
        return jsonify({
            "success": False,
            "message": "Missing required fields in the request body."
        }), 415


    @app.errorhandler(422)
    def unservicable_entity(error): 
        return jsonify({
            "success": False,
            "message": "Unservicable Entity submitted"
        }), 422

    @app.errorhandler(500)
    def internal_server(error): 
        return jsonify({
            "success": False,
            "message": "Internal Server error"
        }), 500

    return app

