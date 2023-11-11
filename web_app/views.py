from datetime import datetime, timedelta, date
import requests
import json
import stripe
from flask import render_template, make_response, request, redirect, url_for, jsonify

from db import session, models
from authentication.auth import auth_required, employee_required, manager_required
from db.models import Booking
from web_app.forms import LoginForm, BookingForm, SignupForm, MembershipForm, ManagementPricesForm, \
    ManagementStaffForm, ManagementActivitiesForm, ManagementFacilitiesForm, EmployeeViewBookingsForm, \
    ManagementSessionsForm

from web_app import web_app_bp
from collections import defaultdict
from sqlalchemy import func, desc

stripe.api_key = "sk_test_51MpzYbBLH2T2onqsttEH7nZuxK05VO9Rghs4XlINj6DJ" \
                 "u1aEZhYLV3q6c9DatjJQuCKSP3iny1J7YPNTXInO9o7U00OuAlsDkX"

monthly_membership_prod_id = "prod_NbTUAAcZm4YtWh"
annual_membership_prod_id = "prod_NbTSt5RUaCFpmN"

monthly_membership_price_lookup_key = "test_monthly_sub_key"
annual_membership_price_lookup_key = "test_annual_sub_key"

stripe.api_key = "sk_test_51MpzYbBLH2T2onqsttEH7nZuxK05VO9Rghs4XlINj6DJ" \
                 "u1aEZhYLV3q6c9DatjJQuCKSP3iny1J7YPNTXInO9o7U00OuAlsDkX"


# Function to get user model object of current user
def get_user():
    # Get email address of current user from jwt
    email = None
    token = request.cookies.get("token")
    if token is not None:
        payload = json.dumps({"token": token})
        header = {"Content-Type": "application/json"}
        response = requests.post("http://127.0.0.1:5000/get_user_email", data=payload, headers=header)
        try:
            email = response.json().get("email")
        except:
            print(response.json().get("error"))

    # Query database to get user object
    user = session.query(models.User).filter_by(email=email).first()

    return user


# Function to get the membership status of the current user
def get_membership_type():
    # get membership id of current user
    mem_id = session.query(models.Customer.membership_type).filter_by(user_id=get_user().user_id).first()[0]
    return mem_id


def get_discount():
    return session.query(models.Discount.discount).first()[0]


# check if user is a manager
def check_manager():
    if get_user():
        managers = session.query(models.Manager).all()
        employees = session.query(models.Employee).all()
        for e in employees:
            if e.user_id == get_user().user_id:
                return 1
        for manager in managers:
            if manager.user_id == get_user().user_id:
                return 2
    return 0


@web_app_bp.route("/", methods=["GET"])
def index():
    # Prevent error trying to pass user first name for welcome message when user not authenticated
    if get_user():
        name_first = get_user().name_first
    else:
        name_first = None

    return render_template("index.html",
                           name_first=name_first,
                           title="HOME",
                           discount=get_discount(),
                           manager=check_manager())


@web_app_bp.route("/logout", methods=["GET"])
@auth_required
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('token')
    response.delete_cookie('basket')
    return response


@web_app_bp.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        # Create header and payload for request to login microservice
        payload = json.dumps({
            "email": login_form.email.data,
            "password": login_form.password.data
        })
        header = {"Content-Type": "application/json"}

        # Make post request to login microservice
        response = requests.post("http://127.0.0.1:5000/check_credentials", data=payload, headers=header)

        # Check for error in response
        if response.json().get("error"):
            return response.json().get("error")

        # No error, get jwt token
        token = response.json().get("token")

        # Build response with jwt token in cookie that expires after 30 mins
        response = make_response(redirect("/"))
        expiry_time = datetime.utcnow() + timedelta(minutes=120)
        response.set_cookie("token", value=token, httponly=True, expires=expiry_time)  # secure=true
        return response

    return render_template("login.html",
                           title="LOGIN",
                           login_form=login_form,
                           discount=get_discount())


@web_app_bp.route("/signup", methods=["GET", "POST"])
def signup():
    signup_form = SignupForm()

    if signup_form.validate_on_submit():
        # Create header and payload for request to login microservice
        payload = json.dumps({
            "name_first": signup_form.name_first.data,
            "name_last": signup_form.name_last.data,
            "line_1": signup_form.line_1.data,
            "line_2": signup_form.line_2.data,
            "city": signup_form.city.data,
            "postcode": signup_form.postcode.data,
            "email": signup_form.email.data,
            "password": signup_form.password.data
        })
        header = {"Content-Type": "application/json"}

        # Make post request to login microservice and return its response to user
        requests.post("http://127.0.0.1:5000/add_customer", data=payload, headers=header)
        return redirect('/login')

    return render_template("signup.html",
                           title="LOGIN",
                           signup_form=signup_form,
                           discount=get_discount())


@web_app_bp.route("/book", methods=["GET", "POST"])
@auth_required
def book():
    booking_form = BookingForm()
    basket = []
    # display current basket
    if request.cookies.get('basket'):
        # array of all session ids in basket
        basket_array = request.cookies.get('basket').split("~")
        print(basket_array)

        # get bookings' activity name and datetime
        for item in basket_array:
            activity_id = session.query(models.Session.activity_id).filter_by(session_id=item).first()[0]
            name = session.query(models.Activity.activity_name).filter_by(activity_id=activity_id).first()[0]
            start = session.query(models.Session.start_date).filter_by(session_id=item).first()[0]
            basket.append((name, start))

        # clear basket pressed, clear cookie and reload
        if request.method == "POST" and "clear-basket" in request.form:
            response = make_response(redirect('/book'))
            response.delete_cookie('basket')
            return response

    if booking_form.validate_on_submit():

        # add to 'basket' cookie
        basket = request.cookies.get('basket')
        if basket:
            new_basket = f'{basket}~{booking_form.session.data}'
        else:
            new_basket = f'{booking_form.session.data}'

        response = make_response(redirect("/book"))
        response.set_cookie('basket', new_basket)
        return response

    # if checkout is pressed
    if request.method == "POST" and "checkout" in request.form:

        # get user_id and mem_id
        mem_type = get_membership_type()

        # check if user has membership, asking them to pay if not
        if mem_type == 0:

            # list to store the dates of the bookings
            dates = []

            # get basket
            basket_array = request.cookies.get('basket').split("~")

            # get bookings' date and add to total price
            for items in basket_array:
                session_date = session.query(models.Session.start_date).filter_by(session_id=items).first()[0].date()
                dates.append(session_date)

            # check for discount eligibility
            # iterate over all possible triples of dates and check if they are within 7 days of each other
            for i in range(len(dates) - 2):
                for j in range(i + 1, len(dates) - 1):
                    for k in range(j + 1, len(dates)):
                        if (dates[j] - dates[i]) <= timedelta(days=7) and (dates[k] - dates[j]) <= timedelta(
                                days=7) and (dates[k] - dates[i]) <= timedelta(days=7):
                            # give discount if 3 bookings within 7 days
                            return redirect(url_for("web_app.booking_pay_discounted"))

            return redirect(url_for("web_app.booking_pay"))

        return redirect("/book-basket")

    return render_template("book.html",
                           name_first=get_user().name_first,
                           basket=basket,
                           title="BOOK",
                           booking_form=booking_form,
                           discount=get_discount(),
                           manager=check_manager())


def remove_past_bookings():
    now = datetime.now()
    past_bookings = session.query(models.Booking).filter(models.Booking.booking_time < now).all()
    for booking in past_bookings:
        # # Find the facility associated with the booking
        # activity = session.query(models.Activity).filter_by(activity_id=booking.activity_id).first()
        # facility = session.query(models.Facility).filter_by(facility_id=activity.facility_id).first()
        # # Increase the capacity of the facility
        # facility.capacity += 1
        # Delete the booking
        session.delete(booking)
    session.commit()


@web_app_bp.route("/get_user_booked_activities", methods=["POST"])
@auth_required
def get_user_booked_activities():
    user = get_user()
    if user is None:
        return jsonify({'error': 'User not logged in'}), 403

    user_bookings = session.query(models.Booking).filter_by(user_id=user.user_id).all()
    user_booked_activities = [booking.session_id for booking in user_bookings]

    return jsonify({'user_booked_activities': user_booked_activities}), 200


@web_app_bp.route("/cancel_cbook", methods=["POST"])
@auth_required
def cancel_cbook():
    user = get_user()

    session_id = request.json.get('session_id')
    goal_booking = session.query(models.Booking).filter_by(session_id=session_id, user_id=user.user_id).first()

    if not goal_booking:
        return jsonify({'error': 'No such booking exists.'}), 400

    goal_session = session.query(models.Session).filter_by(session_id=session_id).first()
    if not goal_session:
        return jsonify({'error': 'No such session exists.'}), 400

    # Update the availability
    goal_session.space_left += 1

    session.delete(goal_booking)
    session.commit()

    # Update the userBookedActivities list and return it as well
    user_booked_activities = session.query(models.Booking.session_id).filter(
        models.Booking.user_id == user.user_id).all()
    user_booked_activities = [activity[0] for activity in user_booked_activities]

    return jsonify({'success': 'Cancel successful', 'user_booked_activities': user_booked_activities}), 200


@web_app_bp.route("/cbook", methods=["GET", "POST"])
@auth_required
def cbook():
    user = get_user()
    if user is None:
        return jsonify({'error': 'User not logged in'}), 403

    user_id = user.user_id
    activity_id = request.json.get('activity_id')
    date_str = request.json.get('date')
    time_str = request.json.get('time')
    session_id = request.json.get('session_id')

    # Convert date_str and time_str to datetime object
    booking_time = datetime.strptime(date_str + " " + time_str, '%Y-%m-%d %H:%M')

    today = date.today()
    now = datetime.now()

    if booking_time < now:
        return jsonify({'error': 'You can not book a past session! '}), 400

    # Get the activity
    activity = session.query(models.Activity).filter_by(activity_id=activity_id).first()
    if not activity:
        return jsonify({'error': 'Activity not found'}), 400

    # Get the facility
    facility = session.query(models.Facility).filter_by(facility_id=activity.facility_id).first()
    if not facility:
        return jsonify({'error': 'Facility not found'}), 400

    # Check if the session has enough capacity
    session_obj = session.query(models.Session).filter_by(session_id=session_id).first()
    if session_obj.space_left <= 0:
        return jsonify({'error': 'No capacity left'}), 400

    booking = Booking(user_id=user_id, activity_id=activity_id, booking_time=booking_time, session_id=session_id)
    # Get user's bookings

    try:
        # Make a booking
        session.add(booking)
        # Decrease the capacity
        session_obj.space_left -= 1

        session.commit()
        remove_past_bookings()
        user_bookings = session.query(models.Booking).filter_by(user_id=user.user_id).all()
        user_booked_activities = [booking.activity_id for booking in user_bookings]
        remove_past_bookings()

        return jsonify({'success': 'Booking successful', 'user_booked_activities': user_booked_activities}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# payment endpoint for non-discounted basket
@web_app_bp.route('/booking-pay', methods=['GET', 'POST'])
def booking_pay():
    # total price of basket
    total = 0

    # get basket
    basket_array = request.cookies.get('basket').split("~")

    # get bookings' date and add to total price
    for items in basket_array:
        activity = session.query(models.Session.activity_id).filter_by(session_id=items).first()[0]
        total += session.query(models.Activity.price).filter_by(activity_id=activity).first()[0]

    # create new price object

    product = stripe.Product.create(
        name="Checkout Basket"
    )

    price = stripe.Price.create(
        unit_amount=int(total * 100),
        currency="gbp",
        product=product.id
    )

    try:
        check_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1
                }
            ],
            mode='payment',
            success_url="http://127.0.0.1:5000/book-basket",
            cancel_url="http://127.0.0.1:5000/book"
        )

    except Exception as e:
        return str(e)

    return redirect(check_session.url, code=303)


# payment endpoint for discounted basket
@web_app_bp.route('/booking-pay-discounted', methods=['GET', 'POST'])
def booking_pay_discounted():
    # total price of basket
    total = 0

    # get basket
    basket_array = request.cookies.get('basket').split("~")

    # get bookings' date and add to total price
    for items in basket_array:
        activity = session.query(models.Session.activity_id).filter_by(session_id=items).first()[0]
        total += session.query(models.Activity.price).filter_by(activity_id=activity).first()[0]

    # create new price object
    product = stripe.Product.create(
        name="Checkout Basket"
    )

    price = stripe.Price.create(
        unit_amount=int(total * 100),
        currency="gbp",
        product=product.id
    )

    # get discount value
    discount = session.query(models.Discount.discount).first()[0]
    coupon = stripe.Coupon.create(percent_off=discount, name="7-day multi-booking")
    coupon_id = coupon.id

    try:
        check_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1
                }
            ],
            mode='payment',
            discounts=[{
                'coupon': coupon_id
            }],
            success_url="http://127.0.0.1:5000/book-basket",
            cancel_url="http://127.0.0.1:5000/book"
        )

    except Exception as e:
        return str(e)

    return redirect(check_session.url, code=303)


@web_app_bp.route("/book-basket", methods=['GET', 'POST'])
def book_basket():
    payload = json.dumps({
        "user_id": get_user().user_id,
        "basket": request.cookies.get('basket')
    })

    header = {"Content-Type": "application/json"}

    # Make post request to booking microservice
    requests.post("http://127.0.0.1:5000/checkout", data=payload, headers=header)

    # delete basket cookie
    response = make_response(redirect("/account"))
    response.delete_cookie('basket')
    return response


@web_app_bp.route("/facilities", methods=["GET", "POST"])
def upcoming():
    # Prevent error trying to pass user first name for welcome message when user not authenticated
    if get_user():
        name_first = get_user().name_first
    else:
        name_first = None

    # Query database for activities
    activities = session.query(models.Facility).all()

    return render_template("upcoming.html",
                           name_first=name_first,
                           activities=activities,
                           discount=get_discount(),
                           title="upcoming",
                           manager=check_manager())


def group_activities_by_day(activities):
    activities_by_day = defaultdict(list)
    day_headings = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')

    for activity in activities:
        # activity_date = activity.start_date
        activity_date = activity.Session.start_date
        day_index = activity_date.weekday()
        day_name = day_headings[day_index]
        activities_by_day[day_name].append(activity)

        # print("Activity date", activity_date)

    # Sort in time order
    for day in activities_by_day:
        activities_by_day[day].sort(key=lambda x: x.Session.start_date.time())

    return activities_by_day


def show_booked_sessions(bookings):
    booked_sessions = defaultdict(list)

    for booked in bookings:
        booked_sessions[booked].append(booked)

    return booked_sessions


@web_app_bp.route("/calendar", methods=["GET", "POST"])
@auth_required
def calendar():
    # Get email of current logged in user
    if get_user():
        name_first = get_user().name_first
    else:
        name_first = None

    today = date.today()

    # set start date and end date for the week
    start_of_this_week = today - timedelta(days=today.weekday())

    end_of_this_week = start_of_this_week + timedelta(days=6)

    # calculate and set date for start/end of next week
    days_to_next_monday = 7 - today.weekday()
    start_of_next_week = today + timedelta(days=days_to_next_monday)
    end_of_next_week = start_of_next_week + timedelta(days=6)
    # initialise day of the week
    day_headings = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
    next_week_day_headings = (
        'Next Monday', 'Next Tuesday', 'Next Wednesday', 'Next Thursday', 'Next Friday', 'Next Saturday', 'Next Sunday')

    # join tables : Session, Activity, Facility
    thisweek_activities = (session.query(models.Session, models.Activity, models.Facility).outerjoin(models.Activity,
                                                                                                     models.Session.activity_id == models.Activity.activity_id).outerjoin(
        models.Facility, models.Facility.facility_id == models.Activity.facility_id).filter(
        models.Session.start_date >= start_of_this_week, models.Session.start_date <= end_of_this_week).order_by(
        models.Session.start_date))

    # print("This week act: ", thisweek_activities)

    nextweek_activities = session.query(models.Session, models.Activity, models.Facility).outerjoin(models.Activity,
                                                                                                    models.Session.activity_id == models.Activity.activity_id).outerjoin(
        models.Facility, models.Facility.facility_id == models.Activity.facility_id).filter(
        models.Session.start_date >= start_of_next_week, models.Session.start_date <= end_of_next_week).order_by(
        models.Session.start_date)

    thisweek_activities_by_day = group_activities_by_day(thisweek_activities)

    # print("This week act by days: ", thisweek_activities_by_day)

    nextweek_activities_by_day = group_activities_by_day(nextweek_activities)

    booked_sessions = session.query(models.Booking.user_id, models.Booking.activity_id)

    return render_template("sessions.html",
                           name_first=name_first,
                           title="calendar",
                           day_headings=day_headings,
                           today=today,
                           thisweek_activities_by_day=thisweek_activities_by_day,
                           nextweek_activities=nextweek_activities,
                           next_week_activities_by_day=nextweek_activities_by_day,
                           booked_sessions=booked_sessions,
                           discount=get_discount(),
                           manager=check_manager())


# function to get the membership status of the current user
def get_user_and_membership_type(email):
    # get current user id
    user_id = None
    if email is not None:
        user_id = session.query(models.User.user_id).filter_by(email=email.lower()).first()[0]

    # get membership id of current user
    mem_id = session.query(models.Customer.membership_type).filter_by(user_id=user_id).first()[0]
    return mem_id, user_id


@web_app_bp.route("/account", methods=["GET", "POST"])
@auth_required
def account():
    # get user's current membership type
    mem_id = get_membership_type()

    # determine user's membership type
    if mem_id == 0:
        sub_type = "No Membership"
    elif mem_id == 1:
        sub_type = "Monthly Subscription"
    else:
        sub_type = "Annual Subscription"

    # get all bookings for the current user
    bookings = session.query(models.Booking).filter_by(user_id=get_user().user_id).all()
    user_bookings = []
    outdated_bookings = []

    for booking in bookings:
        # for each booking
        activity_name = session.query(models.Activity.activity_name).filter_by(activity_id=booking.activity_id)[0]

        # if booking has passed
        if booking.booking_time < datetime.now():
            outdated_bookings.append(
                [activity_name[0], booking.booking_time.strftime("%d-%m-%Y %H:%M:%S"), booking.booking_id])
        else:
            user_bookings.append(
                [activity_name[0], booking.booking_time.strftime("%d-%m-%Y %H:%M:%S"), booking.booking_id])

    # if user presses button to cancel membership or a booking
    if request.method == "POST":
        if "cancel" in request.form:

            if mem_id == 0:
                return redirect('/account')

            payload = json.dumps({
                "user_id": get_user().user_id
            })
            header = {"Content-Type": "application/json"}

            requests.post("http://127.0.0.1:5000/cancel", data=payload, headers=header)

            return redirect('/account')

        for name in request.form:
            if name.startswith("cancel-booking-"):
                booking_id = name.split('-')[-1]
                # cancel booking with above id
                payload = json.dumps({
                    "booking_id": booking_id,
                })

                header = {"Content-Type": "application/json"}

                requests.post("http://127.0.0.1:5000/cancel-booking", data=payload, headers=header)

                return redirect('/account')

    return render_template("account.html",
                           name_first=get_user().name_first,
                           sub_type=sub_type,
                           user_bookings=user_bookings,
                           outdated_bookings=outdated_bookings,
                           discount=get_discount(),
                           manager=check_manager(),
                           title="MY ACCOUNT")


@web_app_bp.route("/membership", methods=["GET", "POST"])
@auth_required
def membership():
    # Get prices of monthly and annual memberships in pence
    monthly_membership_price = stripe.Price.search(query="product:'" + monthly_membership_prod_id + "'").data[0].get(
        "unit_amount")
    annual_membership_price = stripe.Price.search(query="product:'" + annual_membership_prod_id + "'").data[0].get(
        "unit_amount")

    membership_form = MembershipForm()

    if membership_form.validate_on_submit():

        # get membership type of user and user id
        mem_id = get_membership_type()

        # user already has a membership
        if mem_id != 0:
            return redirect('/account')

        # otherwise redirect to appropriate payment
        if membership_form.membership.data == "monthly":
            return redirect(url_for("web_app.monthly_pay"))
        else:
            return redirect(url_for("web_app.annual_pay"))

    return render_template("membership.html",
                           name_first=get_user().name_first,
                           title="BECOME A MEMBER",
                           monthly_membership_price="{:.2f}".format(monthly_membership_price / 100),
                           annual_membership_price="{:.2f}".format(annual_membership_price / 100),
                           discount=get_discount(),
                           membership_form=membership_form,
                           manager=check_manager())


@web_app_bp.route("/monthly", methods=['GET', 'POST'])
@auth_required
def monthly():
    payload = json.dumps({
        "membership_type": 1,
        "user_id": get_user().user_id
    })
    header = {"Content-Type": "application/json"}
    requests.post("http://127.0.0.1:5000/new_member", data=payload, headers=header)

    return redirect("/account")


@web_app_bp.route("/annual", methods=['GET', 'POST'])
@auth_required
def annual():
    payload = json.dumps({
        "membership_type": 2,
        "user_id": get_user().user_id
    })
    header = {"Content-Type": "application/json"}
    requests.post("http://127.0.0.1:5000/new_member", data=payload, headers=header)

    return redirect("/account")


@web_app_bp.route('/monthlyPay', methods=['GET', 'POST'])
@auth_required
def monthly_pay():
    try:
        check_session = stripe.checkout.Session.create(
            line_items=[{
                'price': stripe.Price.search(query="product:'" + monthly_membership_prod_id + "'").data[0].get("id"),
                'quantity': 1
            }],
            mode='subscription',
            success_url="http://127.0.0.1:5000/monthly",
            cancel_url="http://127.0.0.1:5000/account"
        )
    except Exception as e:
        return str(e)

    return redirect(check_session.url, code=303)


@web_app_bp.route('/annualPay', methods=['GET', 'POST'])
@auth_required
def annual_pay():
    try:
        check_session = stripe.checkout.Session.create(
            line_items=[{
                'price': stripe.Price.search(query="product:'" + annual_membership_prod_id + "'").data[0].get("id"),
                'quantity': 1
            }],
            mode='subscription',
            success_url="http://127.0.0.1:5000/annual",
            cancel_url="http://127.0.0.1:5000/account"
        )
    except Exception as e:
        return str(e)

    return redirect(check_session.url, code=303)


@web_app_bp.route("/management", methods=["GET", "POST"])
@manager_required
def management():
    # Create flask form for each management pane
    management_prices_form = ManagementPricesForm()
    management_staff_form = ManagementStaffForm()
    management_facilities_form = ManagementFacilitiesForm()
    management_activities_form = ManagementActivitiesForm()
    management_sessions_form = ManagementSessionsForm()

    # Get prices of monthly and annual memberships in pence using stripe api
    monthly_membership_price = stripe.Price.search(
        query="product:'" + monthly_membership_prod_id + "'").data[0].get("unit_amount")
    annual_membership_price = stripe.Price.search(
        query="product:'" + annual_membership_prod_id + "'").data[0].get("unit_amount")

    # Get employee data
    employees = session.query(models.User.name_first, models.User.name_last, models.User.email,
                              models.Employee.manager_id) \
        .join(models.Employee, models.User.user_id == models.Employee.user_id)

    # Get facilities and activities data
    facilities = session.query(models.Facility).all()
    activities = session.query(models.Activity.activity_name, models.Activity.duration, models.Activity.price,
                               models.Facility.facility_name) \
        .join(models.Facility, models.Activity.facility_id == models.Facility.facility_id).all()

    # Get Statistic and orders
    bookings = session.query(models.Booking.booking_id,
                             models.Activity.activity_name, models.Activity.price,
                             func.count(models.Activity.activity_name).label("counts"),
                             (models.Activity.price * (func.count(models.Activity.activity_name))).label("revenue")) \
        .join(models.Activity, models.Booking.activity_id == models.Activity.activity_id) \
        .group_by(models.Activity.activity_name).all()

    # Stats per facility
    facilities_stats = session.query(models.Booking.booking_id,
                                     models.Activity.activity_name, models.Activity.price,
                                     func.count(models.Activity.activity_name).label("counts"),
                                     func.sum(models.Activity.price).label("revenue"),
                                     models.Facility.facility_name) \
        .join(models.Activity, models.Booking.activity_id == models.Activity.activity_id) \
        .join(models.Facility, models.Activity.facility_id == models.Facility.facility_id) \
        .group_by(models.Facility.facility_name).order_by(desc('counts')).all()

    # Total Revenue
    total_rev = session.query(models.Booking.booking_id,
                              models.Activity.activity_name, models.Activity.price,
                              func.count(models.Activity.activity_name).label("counts"),
                              func.sum(models.Activity.price).label("revenue")) \
        .join(models.Activity, models.Booking.activity_id == models.Activity.activity_id) \
        .limit(1)

    # Total Session booked
    total_booked = session.query(models.Booking.booking_id,
                                 models.Activity.activity_name, models.Activity.price,
                                 func.count(models.Activity.activity_name).label("counts")) \
        .join(models.Activity, models.Booking.activity_id == models.Activity.activity_id).limit(1)

    # Most booked
    most_booked = session.query(models.Booking.booking_id,
                                models.Activity.activity_name, models.Activity.price,
                                func.count(models.Activity.activity_name).label("counts")) \
        .join(models.Activity, models.Booking.activity_id == models.Activity.activity_id) \
        .group_by(models.Activity.activity_name).order_by(desc('counts')).limit(1)

    # get all sessions
    sessions = session.query(models.Session).all()
    # get name of each activity in sessions
    s = []
    for sesh in sessions:
        activity_name = session.query(models.Activity.activity_name).filter_by(activity_id=sesh.activity_id).first()[0]
        s.append((activity_name, sesh))

    # Number of customers/ members
    members = session.query(models.Customer.customer_id, models.Customer.user_id, models.Customer.membership_type,
                            func.count(models.Customer.membership_type).label("counts")) \
        .group_by(models.Customer.membership_type).all()

    # total number of customers
    total_cus = session.query(models.Customer.customer_id, models.Customer.user_id, models.Customer.membership_type,
                              func.count(models.Customer.user_id).label("total")).limit(1)

    # total number of members
    total_mem = session.query(models.Customer.customer_id, models.Customer.user_id, models.Customer.membership_type,
                              func.count(models.Customer.user_id).label("total")).filter(
        models.Customer.membership_type != 0).limit(1)

    return render_template("management.html",
                           name_first=get_user().name_first,
                           title="Management",
                           monthly_membership_price="{:.2f}".format(monthly_membership_price / 100),
                           annual_membership_price="{:.2f}".format(annual_membership_price / 100),
                           discount=get_discount(),
                           management_prices_form=management_prices_form,
                           management_staff_form=management_staff_form,
                           management_facilities_form=management_facilities_form,
                           management_activities_form=management_activities_form,
                           management_sessions_form=management_sessions_form,
                           employees=employees,
                           facilities=facilities,
                           activities=activities,
                           bookings=bookings,
                           facilities_stats=facilities_stats,
                           total_rev=total_rev,
                           total_booked=total_booked,
                           most_booked=most_booked,
                           s=s,
                           members=members,
                           total_cus=total_cus,
                           total_mem=total_mem,
                           manager=check_manager())


@web_app_bp.route("/amend-prices", methods=["POST"])
@manager_required
def amend_prices():
    # Create flask form for changing prices and discount
    form = ManagementPricesForm()

    # Define function to use when form submitted
    if form.validate_on_submit():
        # Validation: check prices are valid numbers and in format of GBP (while converting to unit amount)
        try:
            new_monthly_price = int(float("{:.2f}".format(float(form.monthly_price.data))) * 100)
            new_annual_price = int(float("{:.2f}".format(float(form.annual_price.data))) * 100)
        except ValueError:
            return jsonify({"error": "Invalid membership prices"})
        # Validation: check price not negative
        if new_monthly_price < 0 or new_annual_price < 0:
            return jsonify({"error": "Membership prices cannot be negative"})
        # Get original prices
        monthly_membership_price = stripe.Price.search(
            query="product:'" + monthly_membership_prod_id + "'").data[0].get("unit_amount")
        annual_membership_price = stripe.Price.search(
            query="product:'" + annual_membership_prod_id + "'").data[0].get("unit_amount")
        # Create new stripe price for monthly plan if it was changed
        if new_monthly_price != monthly_membership_price:
            stripe.Price.create(
                unit_amount=new_monthly_price,
                currency="gbp",
                recurring={"interval": "month"},
                product=monthly_membership_prod_id,
                transfer_lookup_key=True,
            )
        # Create a new stripe price for annual plan if it was changed
        if new_annual_price != annual_membership_price:
            stripe.Price.create(
                unit_amount=new_annual_price,
                currency="gbp",
                recurring={"interval": "year"},
                product=annual_membership_prod_id,
                transfer_lookup_key=True,
            )
        # Update discount in database if it was changed
        if form.discount.data != get_discount():
            session.query(models.Discount).where(models.Discount.discount_id == 1).update(
                {'discount': form.discount.data})
            session.commit()
        # Price changes complete - redirect to management
        return redirect('/management')

    # If no form submitted return error message
    return jsonify({"error": "No form submitted"})


@web_app_bp.route("/amend-facilities", methods=["POST"])
@manager_required
def amend_facilities():
    # Create flask form for changing prices and discount
    form = ManagementFacilitiesForm()
    print(form.opening_time.data.hour)

    # Define function to use when form submitted
    if form.validate_on_submit():
        new_facility = models.Facility(facility_name=form.facility_name.data,
                                       capacity=form.capacity.data,
                                       opening_time=form.opening_time.data,
                                       closing_time=form.closing_time.data)
        session.add(new_facility)
        session.commit()
        return redirect('/management')

    # If no form submitted return error message
    return jsonify({"error": "No form submitted"})


@web_app_bp.route("/amend-activities", methods=["POST"])
@manager_required
def amend_activities():
    # Create flask form for changing prices and discount
    form = ManagementActivitiesForm()
    # Define function to use when form submitted
    if form.validate_on_submit():
        new_activity = models.Activity(activity_name=form.activity_name.data,
                                       duration=form.duration.data,
                                       price=form.price.data,
                                       facility_id=form.facility_id.data)
        session.add(new_activity)
        session.commit()
        return redirect('/management')
    # If no form submitted return error message
    return jsonify({"error": "No form submitted"})


@web_app_bp.route("/amend-sessions", methods=["POST"])
@manager_required
def amend_sessions():
    form = ManagementSessionsForm()
    # Define function to use when form submitted
    if form.validate_on_submit():
        start_d = datetime.combine(form.start_date.data, form.start_time.data)
        new_session = models.Session(activity_id=form.activity_id.data,
                                     start_date=start_d,
                                     end_date=start_d + timedelta(hours=1),
                                     space_left=form.space_left.data)
        session.add(new_session)
        session.commit()
        return redirect('/management')
    # If no form submitted return error message
    return jsonify({"error": "No form submitted"})


@web_app_bp.route("/amend-staff", methods=["POST"])
@manager_required
def amend_staff():
    # Create flask form for changing prices and discount
    form = ManagementStaffForm()
    # Define function to use when form submitted
    if form.validate_on_submit():
        # Create header and payload for request to login microservice
        payload = json.dumps({
            "name_first": form.name_first.data,
            "name_last": form.name_last.data,
            "email": form.email.data,
            "password": form.password.data,
            "manager_id": session.query(models.Manager.manager_id).filter_by(user_id=get_user().user_id).first()[0]
        })
        header = {"Content-Type": "application/json"}
        # Make post request to auth microservice and return its response to user
        requests.post("http://127.0.0.1:5000/add_employee", data=payload, headers=header)
        # Return success / error message from auth microservice
        return redirect('/management')

    # If no form submitted return error message
    return jsonify({"error": "No form submitted"})


@web_app_bp.route("/employee", methods=["GET", "POST"])
@employee_required
def employee():
    # Forms required for amending customer bookings
    employee_view_bookings_form = EmployeeViewBookingsForm()

    # Redirect to selected customer's view booking page when for submitted
    if employee_view_bookings_form.validate_on_submit():
        return redirect("/employee/view-bookings/" + employee_view_bookings_form.user_id.data)

    return render_template("employee.html",
                           name_first=get_user().name_first,
                           title="Employee",
                           discount=get_discount(),
                           employee_view_bookings_form=employee_view_bookings_form,
                           manager=check_manager())


@web_app_bp.route("/employee/view-bookings/<target_user_id>", methods=["GET", "POST"])
@employee_required
def employee_view_bookings(target_user_id):
    booking_form = BookingForm()

    # If employee submits create customer booking form
    if booking_form.validate_on_submit():
        payload = json.dumps({"basket": booking_form.session.data,
                              "user_id": target_user_id})
        header = {"Content-Type": "application/json"}
        requests.post("http://127.0.0.1:5000/checkout", data=payload, headers=header)
        return redirect("/employee/view-bookings/" + target_user_id)

    # If employee presses cancel booking button
    if request.method == "POST":
        for name in request.form:
            if name.startswith("cancel-booking-"):
                booking_id = name.split('-')[-1]
                # cancel booking with above id
                payload = json.dumps({"booking_id": booking_id})
                header = {"Content-Type": "application/json"}
                requests.post("http://127.0.0.1:5000/cancel-booking", data=payload, headers=header)
                return redirect("/employee/view-bookings/" + target_user_id)

    target_user = session.query(models.User).filter_by(user_id=target_user_id).first()
    bookings = session.query(models.Booking.user_id, models.Booking.booking_id,
                             models.Activity.activity_name, models.Session.start_date) \
        .filter_by(user_id=target_user_id) \
        .join(models.Session, models.Session.session_id == models.Booking.session_id) \
        .join(models.Activity, models.Session.activity_id == models.Activity.activity_id)

    return render_template("employee_view_bookings.html",
                           name_first=get_user().name_first,
                           title="Employee",
                           discount=get_discount(),
                           target_user=target_user,
                           bookings=bookings,
                           booking_form=booking_form,
                           manager=check_manager())
