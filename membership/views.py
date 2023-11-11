from flask import jsonify, request
from db import models, session
from membership import membership_bp


@membership_bp.route("/new_member", methods=['POST'])
def new_member():
    # get user id and membership type post
    mem_type = request.json.get("membership_type")
    user_id = request.json.get("user_id")

    # use user_id to get the customer
    cust = session.query(models.Customer).filter_by(user_id=user_id).first()
    # assign appropriate membership type
    cust.membership_type = mem_type

    # commit to db
    session.add(cust)
    session.commit()

    return jsonify({"success": "membership assigned"})


@membership_bp.route("/cancel", methods=['POST'])
def cancel():
    # get user_id from post
    user_id = request.json.get("user_id")
    # find customer from user id
    cust = session.query(models.Customer).filter_by(user_id=user_id).first()
    # remove customer membership
    cust.membership_type = 0

    # commit to db
    session.add(cust)
    session.commit()

    return jsonify({"success": "membership cancelled"})
