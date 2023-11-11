from flask import Flask
import config
from authentication import auth_bp
from web_app import web_app_bp, views
from booking import book_bp
from membership import membership_bp
from db import Base, engine
from apscheduler.schedulers.background import BackgroundScheduler


# Factory for flask app with all microservices
def create_app():
    # Create flask app
    app = Flask(__name__)
    app.register_blueprint(web_app_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(membership_bp)

    # Apply configurations from config.py
    app.config.from_object(config)

    # Define the scheduler task
    scheduler = BackgroundScheduler(daemon=True)
    # Call remove_past_bookings function once per hour
    scheduler.add_job(views.remove_past_bookings, 'interval', hours=1)
    scheduler.start()

    return app


if __name__ == '__main__':
    # Create flask app using factory
    test_app = create_app()

    Base.metadata.create_all(engine)

    # Run the Flask app
    test_app.run(host='0.0.0.0', port=5000, debug=True)
