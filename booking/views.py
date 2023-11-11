from flask import jsonify, request
from db import models, session
from booking import book_bp


@book_bp.route("/checkout", methods=['POST'])
def book_activity():
    # get booking details
    user_id = request.json.get("user_id")
    basket = request.json.get("basket")

    # break basket into individual activities
    activities = basket.split("~")
    for info in activities:
        activity_id = session.query(models.Session.activity_id).filter_by(session_id=info).first()[0]
        booking_time = session.query(models.Session.start_date).filter_by(session_id=info).first()[0]
        # add to db
        booking = models.Booking(user_id=user_id,
                                 activity_id=activity_id,
                                 booking_time=booking_time,
                                 session_id=info)

        # remove space from capacity
        sesh = session.query(models.Session).filter_by(session_id=info).first()
        sesh.space_left -= 1

        session.add(sesh)
        session.add(booking)
        session.commit()

    return jsonify({'success': 'booked'})


@book_bp.route("/cancel-booking", methods=['POST'])
def cancel_activity():
    # get booking details
    booking_id = request.json.get("booking_id")
    booking = session.query(models.Booking).filter_by(booking_id=booking_id).first()
    sesh = session.query(models.Session).filter_by(session_id=booking.session_id).first()

    # add 1 to space left
    sesh.space_left += 1
    session.add(sesh)
    # remove booking from db
    session.delete(booking)
    session.commit()

    return jsonify({'success': 'cancelled'})
