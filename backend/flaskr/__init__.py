from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

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
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(
        app,
        origins=["*"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def enable_access_control_allow(response):
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS,PUT')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def fetch_all_available_categories():
        categories = Category.query.all()
        result_dict = {}
        for category in categories:
            result_dict[str(category.id)] = str(category.type)

        return jsonify({
            "categories": result_dict
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
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
        page_number = int(request.args.get("page", "1"))
        print(page_number)
        questions = Question.query.all()
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
    @TODO:
    Create an endpoint to DELETE question using a question ID.

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
            raise ValueError("unable to delete entity")

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions/submit", methods=["POST"])
    def create_new_question():
        req = request.get_json()
        question = Question(
            req.get("question", ""),
            req.get("answer", ""),
            req.get("category", ""),
            req.get("difficulty", 1)
        )
        question.insert() 

        return jsonify({
            "success": True,
            "message": "Successfully submitted the question!"
        }), 200
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
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
        print(search_string)
        matching_questions = Question.query.filter(Question.question.ilike(f'%{search_string}%')).all()
        length = len(matching_questions) 
        return jsonify({
            "questions": [q.format() for q in matching_questions],
            "total_questions": length,
            "current_category": None,
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def fetch_questions_by_category_id(category_id):
        current_category = fetch_all_available_categories().get_json()["categories"][str(category_id)]
        print(current_category)
        questions = Question.query.filter(Question.category == category_id).all()
        length = len(questions)
        return jsonify({
            "questions": [q.format() for q in questions],
            "total_questions": length,
            "current_category": current_category,
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def fetch_questions_to_play():
        previous_questions = request.args.getlist("previous_questions", [])
        quiz_category = request.args.get("quiz_category", 1)
        questions = Question.query.filter(Question.category == quiz_category, Question.id not in previous_questions).all()
        length = len(questions)
        print(questions)
        target = random.randint(0,length)
        result = questions[target]
        previous_questions.append(result.id)
        return jsonify({
            "previous_questions": previous_questions,
            "question": result.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
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

    @app.errorhandler(422)
    def unservicable_entity(error): 
        return jsonify({
            "success": False,
            "message": "Unservicable Entity submitted"
        }), 422


    return app

