import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users_details.db')

    # turn off signal to application every time a change is about to be made in the database.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
