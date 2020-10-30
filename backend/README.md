# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET ...
POST ...
DELETE ...

GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}

```
## Endpoints
#### GET '/categories'
- General
Returns a list of available categories and the number of availalbe categories.
Results are formatted as shown in the result below.

- Sample: `curl http://127.0.0.1:5000/categories`

`example section...`
- Result:
```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true,
  "total_categories": 6
}
```

```hello
```


@TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods = ['GET'])
  def list_categories(): 

    return jsonify({
      'success': True,
      'categories': format_categories(),
      'total_categories': len(get_categories())
    })
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods = ['GET'])
  def list_questions():
    questions = get_questions()   
    current_questions = paginate_questions(request, questions)

    if current_questions == []:
      abort(404)

    return jsonify({
      'success': True,      
      'questions': paginate_questions(request, questions),
      'total_questions': len(questions),
      'current_category': None,
      'categories': format_categories()      
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)
        
      else:
        question.delete()
        questions = get_questions()
        current_questions = paginate_questions(request, questions)

        return jsonify({
          'success': True,
          'deleted': question.format(),
          'questions': current_questions,
          'total_questions': len(questions)
        })
    except:
      abort(422) # not able to process the request

  
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/add', methods = ['POST'])
  def submit_question():
    data = request.get_json()
    new_question = data.get('question', None)
    new_answer = data.get('answer', None)
    new_difficulty = data.get('difficulty', None)
    new_category = data.get('category', None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()
      questions = Question.query.all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'deleted': question.id,
        'question': new_question,
        'answer': new_answer,
        'difficulty': new_difficulty,
        'category': new_category,
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422) # not able to process the request


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods = ['POST'])
  def search_questions():
    data = request.get_json()
    search_term = data.get('searchTerm', None)
    search = '%{0}%'.format(search_term)

    questions = Question.query.filter(Question.question.ilike(search)).all()
    formatted_questions = paginate_questions(request, questions)
    print(questions)
    return jsonify({
      'questions': formatted_questions,
      'total_questions': len(questions),
      'current_category': 1
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, questions)

    if current_questions is None:
      abort(404)

    try:   
      return jsonify({
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': category_id
      })
    except:
      abort(422)

           


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods = ['POST'])
  def play_quiz():
    data = request.get_json()
    category = data.get('quiz_category', None)
    category_id = category['id']
    previous_questions = data.get('previous_questions', None)  

    if category_id == 0:
      questions = get_questions()    
    
    else:    
      category_id = category['id']
      questions = Question.query.filter(Question.category == category_id).all()
    
    new_questions = []
    
    for question in questions:
      if question.id not in previous_questions:        
        new_questions.append(question)
      
    if new_questions == []:
      formatted_question = 0
    
    else:
      question = random.choice(new_questions)   
      formatted_question = question.format() 
      previous_questions.append(formatted_question)

      print(formatted_question)
    
    try:
      return jsonify({
        'question': formatted_question        
      })
    
    except:
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def not_found(error):
    
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not found'
    }), 404

  @app.errorhandler(405)
  def not_found(error):
    
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):

    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422


  @app.errorhandler(500)
  def unprocessable(error):

    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    }), 500

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```