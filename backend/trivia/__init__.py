import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from trivia.models import setup_db, Question, Category, db
from trivia.errors import error_404, error_422, error_400, error_405, error_500

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    pagelength = request.args.get('pagelength', QUESTIONS_PER_PAGE, type=int)
    start =  (page - 1) * pagelength
    end = start + pagelength

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def api_greeting():
        return jsonify({'message':'Hello, World!'})
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.

    === DONE ===
    '''

    @app.route('/categories')
    def get_categories():
        allCategories = Category.query.order_by(Category.id).all()

        out_dictionary = {}
        for category in allCategories:
            out_dictionary[category.id] = category.type

        if len(allCategories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': out_dictionary
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

    === DONE ===
    little error in frontend/README.md
    endpoint should return total_questions and not totalQuestions iot be able to paginate frontend
    '''

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        allCategories = Category.query.order_by(Category.id).all()

        out_categories = {}
        for category in allCategories:
            out_categories[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': out_categories
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.

    === DONE ===
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.

    === DONE === 
    '''
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start.
    === DONE ===
    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        searchTerm = body.get('searchTerm', None)

        print(body)

        try:
            # if a searchTerm is present in body search database for questions alike
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                    'current_category': None
                })
            # insert a question to the database
            else:
                print(new_question)
                if ((new_question is None) or (new_answer is None) or\
                    (new_question == '') or (new_answer == '')):
                    abort(404)
                
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except:
            abort(422)
    
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown.

    === DONE ===
    '''

    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def retrieve_questions_per_cat(cat_id):
        selection = Question.query.filter(Question.category==cat_id).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        allCategories = Category.query.order_by(Category.id).all()

        out_categories = {}
        for category in allCategories:
            out_categories[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': out_categories
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.

    === DONE ===
    '''

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        body = request.get_json()
        print(body)
        cat_id = body.get('quiz_category', None)['id']
        previous_questions = body.get('previous_questions', None)
        
        try:
            if cat_id == 0:
                ids = db.session.query(Question.id).distinct()
                allIds = list(set([id[0] for id in ids]) - set(previous_questions))
                print(allIds)
                randomQuestion = Question.query.filter(Question.id == random.choice(allIds)).first()

                return jsonify({
                    'success': True,
                    'question': randomQuestion.format()
                })
            else:
                ids = db.session.query(Question.id).filter(Question.category == cat_id).distinct()
                allIds = list(set([id[0] for id in ids]) - set(previous_questions))
                print(allIds)
                randomQuestion = Question.query.filter(Question.id == random.choice(allIds)).first()

                return jsonify({
                    'success': True,
                    'question': randomQuestion.format()
                })
        except:
            abort(422)

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422.
    === DONE ===
    '''
    error_404(app)
    error_422(app)
    error_400(app)
    error_405(app)
    error_500(app)
  
    return app