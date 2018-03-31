from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Person(Base):
    """
    creating two tables just for practice
    this table will hold the persons id in database
    """

    __tablename__ = 'person'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True, autoincrement=True)


class Details(Base):
    """
    holds the details of a person email, password, connects to persons table
    """
    __tablename__ = 'address'
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship(Person)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///login_data.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)