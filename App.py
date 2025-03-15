from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from database import db
from routes import register_routes
from flask_jwt_extended import JWTManager
from auth_routes import auth_bp


def create_app():
    app = Flask(__name__, static_folder='build', static_url_path='/')
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pharmacy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

    # Initialize database and JWT
    db.init_app(app)
    jwt = JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix='/api')

    # API Welcome Route
    @app.route('/api')
    def welcome():
        return jsonify({
            "message": "Welcome to the Pharmacy API Backend!",
            "status": "Online",
            "version": "1.0.0"
        })

    # Serve React Frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    register_routes(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')