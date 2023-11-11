from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

# Initialise base for models
Base = declarative_base()

# Initialise engine
engine = create_engine('mysql+mysqlconnector://root:@localhost/sep_live')

# Create sqlalchemy session factory bound to engine
SessionMaker = sessionmaker(bind=engine)

# Create session using factory
session = SessionMaker()

# Create all database tables if they do not already exist
Base.metadata.create_all(engine)
