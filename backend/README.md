# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

### API Documentation

#### `GET /categories`

Fetches all available categories.

- **Request Arguments:** None
- **Returns:** An object with a single key `categories`, containing an object of `id: category_string` key-value pairs.

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

---

#### `GET /questions`

Fetches a paginated list of questions (10 per page by default).

- **Request Arguments:**
  - `page` (integer, optional) - Page number for pagination. Defaults to 1.
- **Returns:** An object containing:
  - `questions` - List of question objects
  - `total_questions` - Total number of questions
  - `categories` - All available categories
  - `current_category` - Currently selected category (null for all)

```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": "3",
      "difficulty": 1
    }
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

---

#### `DELETE /questions/<question_id>`

Deletes a question by its ID.

- **Request Arguments:**
  - `question_id` (integer, required) - The ID of the question to delete (URL parameter)
- **Returns:** A success message on successful deletion.

```json
{
  "success": true,
  "message": "Successfully deleted the question!"
}
```

- **Errors:** Returns 404 if the question does not exist.

---

#### `POST /questions`

Creates a new question.

- **Request Body:**

```json
{
  "question": "What is the largest planet?",
  "answer": "Jupiter",
  "category": "1",
  "difficulty": 2
}
```

- **Returns:** A success message on successful creation.

```json
{
  "success": true,
  "message": "Successfully submitted the question!"
}
```

---

#### `POST /questions/search`

Searches for questions containing the search term (case-insensitive).

- **Request Body:**

```json
{
  "searchTerm": "title"
}
```

- **Returns:** An object containing matching questions.

```json
{
  "questions": [
    {
      "id": 5,
      "question": "What movie won the title for Best Picture?",
      "answer": "Moonlight",
      "category": "5",
      "difficulty": 4
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

---

#### `GET /categories/<category_id>/questions`

Fetches all questions for a specific category.

- **Request Arguments:**
  - `category_id` (integer, required) - The ID of the category (URL parameter)
- **Returns:** An object containing questions for that category.

```json
{
  "questions": [
    {
      "id": 20,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": "1",
      "difficulty": 4
    }
  ],
  "total_questions": 3,
  "current_category": "Science"
}
```

---

#### `POST /quizzes`

Fetches a random question in a specific category, excluding previously asked questions.

- **Request Body:**

```json
{
  "previous_questions": [20],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

- **Notes:**
  - Use `"id": 0` to get questions from all categories.
  - `previous_questions` is an array of question IDs already asked.

- **Returns:** A random question in a specific category but not in the previous questions list.

```json
{
  "previousQuestions": [20, 21],
  "question": {
    "id": 21,
    "question": "Who discovered penicillin?",
    "answer": "Alexander Fleming",
    "category": "1",
    "difficulty": 3
  }
}
```

- **Returns when no more questions:** `{ "question": null }`

---

### Error Handling

The API returns JSON error responses in the following format:

```json
{
  "success": false,
  "message": "Error description"
}
```

**Error Codes:**
- `400` - Bad Request
- `404` - Resource was not found
- `422` - Unprocessable Entity
- `500` - Internal Server Error

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
