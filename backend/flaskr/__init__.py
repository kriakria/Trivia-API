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

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, PATCH, POST, DELETE, OPTIONS')

        return response

    def get_questions():
        questions = Question.query.all()

        if len(questions) == 0:
            abort(404)

        return questions

    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return categories

    def format_categories():
        categories = get_categories()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        return formatted_categories

    @app.route('/categories', methods=['GET'])
    def list_categories():

        categories = get_categories()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': format_categories(),
            'total_categories': len(categories)
        })

    @app.route('/questions', methods=['GET'])
    def list_questions():
        questions = get_questions()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginate_questions(request, questions),
            'total_questions': len(questions),
            'current_category': None,
            'categories': format_categories()
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

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
        except BaseException:
            abort(422)  # not able to process the request

    @app.route('/questions/add', methods=['POST'])
    def submit_question():
        data = request.get_json()
        new_question = data.get('question', None)
        new_answer = data.get('answer', None)
        new_difficulty = data.get('difficulty', None)
        new_category = data.get('category', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=new_difficulty,
                category=new_category)
            question.insert()
            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'question': new_question,
                'answer': new_answer,
                'difficulty': new_difficulty,
                'category': new_category,
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(422)  # not able to process the request

    @app.route('/questions', methods=['POST'])
    def search_questions():
        data = request.get_json()
        search_term = data.get('searchTerm', None)
        search = '%{0}%'.format(search_term)

        questions = Question.query.filter(
            Question.question.ilike(search)).all()
        formatted_questions = paginate_questions(request, questions)
        print(questions)
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': 0
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        questions = Question.query.filter(
            Question.category == category_id).all()
        current_questions = paginate_questions(request, questions)

        if current_questions == []:
            abort(404)

        try:
            return jsonify({
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category_id,
                'success': True
            })
        except BaseException:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        category = data.get('quiz_category', None)
        category_id = category['id']

        previous_questions = data.get('previous_questions', None)

        if category_id == 0:
            questions = get_questions()

        else:
            category_id = category['id']
            questions = Question.query.filter(
                Question.category == category_id).all()

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

        try:
            return jsonify({
                'question': formatted_question,
                'success': True
            })

        except BaseException:
            abort(404)

    @app.errorhandler(400)
    def bad_request(error):

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
    def method_not_allowed(error):

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
    def server_error(error):

        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app
