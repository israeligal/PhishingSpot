from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from sqlalchemy.ext.declarative import declarative_base
from flask_security import RoleMixin, UserMixin
from sqlalchemy.orm import relationship
from flask import request, redirect, url_for, abort

from extentsions import db
Base = declarative_base()


Column = db.Column
Integer = db.Integer
String = db.String
ForeignKey = db.ForeignKey

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('flask_user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('flask_role.id'))
)


class DbUser(db.Model):
    """
    creating two tables just for practice
    this table will hold the persons id in database
    """

    __tablename__ = 'person'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True, autoincrement=True)
    #     email = Column(String(250), nullable=False, unique=True)
    #     password =Column(String(250), nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.id)


class DbDetails(db.Model):
    """
    holds the details of a person email, password, connects to persons table
    """
    __tablename__ = 'address'
    email = Column(String(250), primary_key=True, nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    user_id = Column(Integer, ForeignKey('person.id'))
    user = relationship(DbUser)

    def __repr__(self):
        return '<DbDetails {0} {1}>'.format(self.email, self.password)


class FlaskRole(db.Model, RoleMixin):
    __tablename__ = 'flask_role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class FlaskUser(db.Model, UserMixin):
    __tablename__ = 'flask_user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('FlaskRole', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class MyModelView(ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


