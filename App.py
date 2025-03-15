from flask import Flask, jsonify
from flask_cors import CORS
import os
from database import db
from routes import register_routes


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Configure SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pharmacy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initializing database with app
    db.init_app(app)

    # Add a welcome route at the root URL
    @app.route('/')
    def welcome():
        return jsonify({
            "message": "Welcome to the Pharmacy API Backend!",
            "status": "Online",
            "version": "1.0.0"
        })

    # Registration routes
    register_routes(app)

    # database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')