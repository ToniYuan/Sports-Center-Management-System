# Auth module - should be imported by all microservices to add auth_required()
# function as a decorator (@auth_required) so the jwt is checked for authentication
# used: https://stackoverflow.com/questions/74832858/pass-jwt-token-from-login-to-protected-routes

import jwt
from functools import wraps
from flask import request, jsonify, redirect
from db import models, session

JWT_SECRET = '20d232270737969509ead909fdeea99ee1ba1717f1f51c0e7da73b65233a708c'
JWT_ALGORITHM = 'HS512'


# Wrapper function used to check route is being accessed by an authenticated customer
def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("token")  # Get jwt from request

        # Check token exists in request
        if not token:
            return redirect("/login")

        # Verify token
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.decoded_token = decoded_token

            # Get email address from decoded token
            email = decoded_token.get('email')
            if not email:
                return jsonify({"error": "Email address is missing in the token"}), 401

            # Add email address to request object
            request.email = email

            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return ({"error": "Token is invalid"}), 401

    return wrapper


# Wrapper function used to check route is being accessed by an authenticated employee
def employee_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("token")  # Get jwt from request

        # Check token exists in request
        if not token:
            return redirect("/login")

        # Verify token
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.decoded_token = decoded_token

            # Get email address from decoded token
            email = decoded_token.get('email')
            if not email:
                return jsonify({"error": "Email address is missing in the token"}), 401

            # Check if email in token matches a manager account
            user_id = session.query(models.User).filter_by(email=email).first().user_id
            employee = session.query(models.Employee).filter_by(user_id=user_id).first()
            manager = session.query(models.Manager).filter_by(user_id=user_id).first()
            if employee is None and manager is None:
                return jsonify({"error": "Insufficient privileges to access page"}), 403

            # Add email address to request object
            request.email = email

            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return ({"error": "Token is invalid"}), 401

    return wrapper


# Wrapper function used to check route is being accessed by an authenticated manager
def manager_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("token")  # Get jwt from request

        # Check token exists in request
        if not token:
            return redirect("/login")

        # Verify token
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.decoded_token = decoded_token

            # Get email address from decoded token
            email = decoded_token.get('email')
            if not email:
                return jsonify({"error": "Email address is missing in the token"}), 401

            # Check if email in token matches a manager account
            user_id = session.query(models.User).filter_by(email=email).first().user_id
            manager = session.query(models.Manager).filter_by(user_id=user_id).first()
            if manager is None:
                return jsonify({"error": "Insufficient privileges to access page"}), 403

            # Add email address to request object
            request.email = email

            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return ({"error": "Token is invalid"}), 401

    return wrapper
