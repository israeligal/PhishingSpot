
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DbUser(Base):
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


class DbDetails(Base):
    """
    holds the details of a person email, password, connects to persons table
    """
    __tablename__ = 'address'
    email = Column(String(250),primary_key=True, nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    user_id = Column(Integer, ForeignKey('person.id'))
    user = relationship(DbUser)

    def __repr__(self):
        return '<DbDetails {}>'.format(self.email, self.password)


