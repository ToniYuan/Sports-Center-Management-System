from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, Boolean, Float, Time, func
from db import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name_first = Column(String(32))
    name_last = Column(String(32))
    email = Column(String(128))
    password = Column(String(128))
    salt = Column(String(16))


class CustomerAddress(Base):
    __tablename__ = 'customer_addresses'
    address_id = Column(Integer, primary_key=True, autoincrement=True)
    line_1 = Column(String(128), nullable=False)
    line_2 = Column(String(128), nullable=False)
    city = Column(String(128), nullable=False)
    postcode = Column(String(8), nullable=False)


class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    address_id = Column(Integer, ForeignKey('customer_addresses.address_id'), nullable=False)
    membership_type = Column(Integer, default=0)


class Manager(Base):
    __tablename__ = 'managers'
    manager_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)


class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.manager_id'), nullable=False)


class Facility(Base):
    __tablename__ = 'facilities'
    facility_id = Column(Integer, primary_key=True, autoincrement=True)
    facility_name = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)


class Activity(Base):
    __tablename__ = 'activities'
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_name = Column(String(128), nullable=False)
    duration = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    facility_id = Column(Integer, ForeignKey('facilities.facility_id'), nullable=False)


class Session(Base):
    __tablename__ = 'sessions'
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('activities.activity_id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    space_left = Column(Integer, nullable=False)


class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    booking_time = Column(DateTime, nullable=False)  # Change date and time to booking_time
    activity_id = Column(Integer, ForeignKey('activities.activity_id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False)


class Discount(Base):
    __tablename__ = 'discount'
    discount_id = Column(Integer, primary_key=True, autoincrement=True)
    discount = Column(Integer, nullable=False)
