import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in questions]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Headers', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response

  @app.route('/')
  def start_app():
    questions = get_questions()
    print(questions)
    print("hello")
    
    return questions
    
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods = ['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type

    if len(categories) == 0:
      abort(404)  

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(categories)
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
  #@app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    current_questions = paginate_questions(request, questions)

    categories = Category.query.all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type
    
    '''print("questions on this page:")
    print(len(current_questions))
    print("total questions:")
    print(len(questions))'''

    return jsonify({
      'success': True,      
      'questions': current_questions,
      'total_questions': len(questions),
      'current_category': None,
      'categories': formatted_categories
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
        questions = Question.query.all()
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
    #questions = Question.query.filter(Question.question.ilike('%box%')).all()
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
    questions = Question.query.filter(Question.category == category_id).all()
    #formatted_questions = paginate_questions(request, questions)
    print('previous questions: ' + str(previous_questions))
    print(category['id'])
    new_questions = []
    print('first new questions: ' + str(new_questions))
    for question in questions:
      if question.id in previous_questions:        
        print('the question is in previous_questions')
      else:
        new_questions.append(question)

    print("new questions: " + str(new_questions))


    question = random.choice(new_questions)   
    formatted_question = question.format() 
    previous_questions.append(formatted_question)
    print(question)
    print(formatted_question)
    
    try:
      return jsonify({
        #'previous_questions': previous_questions,
        #'quiz_category': category_id,
        'question': formatted_question
      })
      
    except:
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    