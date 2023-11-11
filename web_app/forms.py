from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField, TimeField, \
    FloatField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange
from datetime import date, timedelta, datetime
from db import session, models


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=320)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=32)])
    submit = SubmitField('Sign in')


class SignupForm(FlaskForm):
    name_first = StringField('First name', validators=[InputRequired(), Length(max=64)])
    name_last = StringField('Last name', validators=[InputRequired(), Length(max=64)])
    line_1 = StringField('Line 1', validators=[InputRequired(), Length(max=64)])
    line_2 = StringField('Line 2', validators=[InputRequired(), Length(max=64)])
    city = StringField('City', validators=[InputRequired(), Length(max=64)])
    postcode = StringField('Postcode', validators=[InputRequired(), Length(max=8)])
    email = StringField('Email', validators=[InputRequired(), Length(max=320)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=32)])
    submit = SubmitField('Sign in')


def validate_date(form, field):
    if field.data is None:
        raise ValidationError("Booking date is required.")

    if field.data < date.today():
        raise ValidationError("Booking date cannot be in the past.")
    if field.data > (date.today() + timedelta(days=14)):
        raise ValidationError("Booking date must be within 2 weeks from today.")


def validate_time(form, field):
    current_time = datetime.now().time()
    if form.date.data == date.today():  # If the booking is for today
        if field.data <= current_time:  # Compare the booking time with the current time
            raise ValidationError("Booking time cannot be in the past.")


sessions = session.query(models.Session).all()
session_choices = []
for s in sessions:
    # ensure session is within next 2 weeks and has space
    if ((s.start_date > datetime.now()) and (s.start_date.date() < (date.today() + timedelta(days=14)))) and (
            s.space_left > 0):
        activity_name = session.query(models.Activity.activity_name).filter_by(activity_id=s.activity_id).first()[0]
        session_choices.append((s.session_id, activity_name + " at " + s.start_date.strftime("%H:%M:%S on %d/%m/%Y")))

# Doing some change here:
available_activities_name = session.query(models.Activity.activity_name).all()
available_activities_time = session.query(models.Session.start_date).all()


class BookingForm(FlaskForm):
    session = SelectField('Select a session', choices=session_choices)
    submit = SubmitField('Book Now')


class MembershipForm(FlaskForm):
    membership = SelectField('Select Billing Frequency', choices=[('monthly', 'Monthly'), ('annual', 'Annual')])
    submit = SubmitField('Become A Member')


class ManagementPricesForm(FlaskForm):
    monthly_price = StringField('Monthly', validators=[InputRequired()])
    annual_price = StringField('Annual', validators=[InputRequired()])
    discount = IntegerField('Discount', validators=[InputRequired(), NumberRange(0, 100)])
    submit = SubmitField('Update')


class ManagementStaffForm(FlaskForm):
    name_first = StringField('First name', validators=[InputRequired(), Length(max=64)])
    name_last = StringField('Last name', validators=[InputRequired(), Length(max=64)])
    email = StringField('Email', validators=[InputRequired(), Length(max=320)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=32)])
    submit = SubmitField('Add employee')


class ManagementFacilitiesForm(FlaskForm):
    facility_name = StringField('Facility name', validators=[InputRequired(), Length(max=200)])
    capacity = IntegerField('Capacity', validators=[InputRequired()])
    opening_time = TimeField()
    closing_time = TimeField()
    submit = SubmitField('Add facility')


# Method to get tuple of ids and names of each facility to dynamically fill select field
# when creating new activity
def get_facility_choices():
    facility_names = session.query(models.Facility.facility_name).all()
    facility_ids = session.query(models.Facility.facility_id).all()
    facility_choices = []
    for i in range(len(facility_ids)):
        facility_choices.append((facility_ids[i][0], facility_names[i][0]))
    return facility_choices


class ManagementActivitiesForm(FlaskForm):
    activity_name = StringField('Facility name', validators=[InputRequired(), Length(max=128)])
    duration = IntegerField('Duration (hours)', validators=[InputRequired()])
    price = FloatField('Price (£)', validators=[InputRequired()])
    facility_id = SelectField('Select facility', choices=get_facility_choices())
    submit = SubmitField('Add activity')


# Method to get tuple of ids and names of each facility to dynamically fill select field
# when creating new activity
def get_activity_choices():
    activity_names = session.query(models.Activity.activity_name).all()
    activity_ids = session.query(models.Activity.activity_id).all()
    activity_choices = []
    for i in range(len(activity_ids)):
        activity_choices.append((activity_ids[i][0], activity_names[i][0]))
    return activity_choices


class ManagementSessionsForm(FlaskForm):
    activity_id = SelectField('Select Activity', choices=get_activity_choices())
    start_date = DateField('Start Date', validators=[InputRequired()])
    start_time = TimeField('Start Time', validators=[InputRequired()])
    space_left = IntegerField('Spaces Left', validators=[InputRequired()])


# Method to get tuple of customer's user ids and name of customer to dynamically fill select field
# when creating new activity
def get_customer_choices():
    customers = session.query(models.User.name_first, models.User.name_last, models.User.user_id) \
        .join(models.Customer, models.User.user_id == models.Customer.user_id)
    customer_choices = []
    for customer in customers:
        customer_choices.append((customer.user_id, customer.name_first + ' ' + customer.name_last))
    # Sort customers list alphabetically by name
    customer_choices = sorted(customer_choices, key=lambda x: x[1])
    return customer_choices


class EmployeeViewBookingsForm(FlaskForm):
    user_id = SelectField('Select customer', choices=get_customer_choices())
    submit = SubmitField('View bookings')
