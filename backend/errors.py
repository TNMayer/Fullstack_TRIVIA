from flask import jsonify

def error_404(app):
    @app.errorhandler(404)
    def not_found_404(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
        }), 404

def error_422(app):
    @app.errorhandler(422)
    def unprocessable_422(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

def error_400(app):
    @app.errorhandler(400)
    def bad_request_400(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "bad request"
        }), 400

def error_405(app):
    @app.errorhandler(405)
    def not_found_405(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
        }), 405