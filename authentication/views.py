import jwt
from secrets import token_hex
from flask import jsonify, request
from hashlib import sha512
from db import models, session
from authentication.auth import JWT_ALGORITHM, JWT_SECRET
from authentication import auth_bp


# Function to generate salt and use it to hash and salt password
def hash_salt_password(password):
    salt = token_hex(8)  # Generate 16 character hexadecimal salt for the user
    h = sha512()  # Create instance of sha512 object (h)
    h.update(bytes.fromhex(salt))  # Feed salt from user record in database into h
    h.update(password.encode("utf-8"))  # Feed password from request into h
    hashed_password = h.hexdigest()  # Hash salt + request password
    return salt, hashed_password


# Endpoint for validating user credentials and returning jwt token
@auth_bp.route('/check_credentials', methods=['POST'])
def check_credentials():
    email = request.json.get("email").lower()  # Get email from form data in request
    password = request.json.get("password")  # Get password from form data in request

    # Create instance of user model matching email in request
    user = session.query(models.User).filter_by(email=email.lower()).first()

    # Check that user with email from request exists
    if user is None:
        return jsonify({'error': 'Invalid email or password'}), 401

    h = sha512()  # Create instance of sha512 object (h)
    h.update(bytes.fromhex(user.salt))  # Feed salt from user record in database into h
    h.update(password.encode("utf-8"))  # Feed password from request into h
    hashed_password = h.hexdigest()  # Hash salt + request password

    # Check that generated hash matches hash stored in database
    if user.password != hashed_password:
        return jsonify({'error': 'invalid email or password'}), 401

    # Credentials verified, generate jwt
    payload = {'email': email}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Return the token to the user
    return jsonify({'token': token})


# Endpoint for validating new user credentials and adding user to database
@auth_bp.route('/add_customer', methods=['POST'])
def add_customer():
    email = request.json.get("email").lower()  # Get email from form data in request

    # Create instance of user model matching email in request
    user = session.query(models.User).filter_by(email=email.lower()).first()
    # Check that user with email from request exists
    if user is not None:
        return {'error': 'Email already in use'}

    # Email not found, hash and salt password
    salt, hashed_password = hash_salt_password(request.json.get("password"))

    # Create new user with username, hashed password and display name
    new_user = models.User(name_first=request.json.get("name_first"),
                           name_last=request.json.get("name_last"),
                           email=email,
                           password=hashed_password,
                           salt=salt)
    session.add(new_user)
    session.commit()

    # Create customer address to link to customer
    new_customer_address = models.CustomerAddress(line_1=request.json.get("line_1"),
                                                  line_2=request.json.get("line_2"),
                                                  city=request.json.get("city"),
                                                  postcode=request.json.get("postcode"))
    session.add(new_customer_address)
    session.commit()

    # Create customer linked to user and link address to customer, set membership to none
    new_customer = models.Customer(user_id=new_user.user_id,
                                   address_id=new_customer_address.address_id,
                                   membership_type=0)
    session.add(new_customer)
    session.commit()

    return {'success': 'Account created'}


# Endpoint used to add employee to database in management page
@auth_bp.route('/add_employee', methods=['POST'])
def add_employee():
    email = request.json.get("email").lower()  # Get email from form data in request

    # Create instance of user model matching email in request
    user = session.query(models.User).filter_by(email=email.lower()).first()
    # Check that user with email from request exists
    if user is not None:
        return {'error': 'Email already in use'}

    # Email not found, hash and salt password
    salt, hashed_password = hash_salt_password(request.json.get("password"))

    # Create new user with username, hashed password and display name
    new_user = models.User(name_first=request.json.get("name_first"),
                           name_last=request.json.get("name_last"),
                           email=email,
                           password=hashed_password,
                           salt=salt)
    session.add(new_user)
    session.commit()

    # Create new employee with new user id and manager id
    new_employee = models.Employee(user_id=new_user.user_id,
                                   manager_id=request.json.get("manager_id"))
    session.add(new_employee)
    session.commit()

    return {'success': 'employee added'}


# Route to decrypt jwt in user's token to retrieve their email address from it
@auth_bp.route('/get_user_email', methods=['POST'])
def get_user_email():
    token = request.json.get('token')
    if token:
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_email = decoded_token['email']
            return {'email': user_email}
        except jwt.ExpiredSignatureError:
            return {'error': 'token expired'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'token is invalid'}, 401
    else:
        return {'error': 'token is missing'}, 401
