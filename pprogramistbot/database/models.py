"""The module is responsible for tables and relations betweeen them inside of the database."""
# Standard library imports
import datetime

# Third party imports
from sqlalchemy import (
    Column, DateTime,
    ForeignKey, func,
    Integer, String, TIMESTAMP,
    SmallInteger, BigInteger, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Local application imports
from database.settings import engine

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        # It is forbidden to leave just -> datetime.datetime.now convert it to str first!
        server_default=str(datetime.datetime.now()),
        comment='The date an object has been created'
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=str(datetime.datetime.now()),
        onupdate=datetime.datetime.now,
        comment='The date an object has been updated'
    )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Reception(BaseModel):
    __tablename__ = 'reception'

    apply = Column(
        Integer,
        nullable=False,
        comment='How much times the APPLY button has been pressed',
        default=1
    )

    about_courses = Column(
        BigInteger,
        nullable=False,
        comment='How much times the ABOUT_COURSES button has been pressed',
        default=1
    )

    about_company = Column(
        Integer,
        nullable=False,
        comment='How much times the ABOUT_COMPANY button has been pressed',
        default=1
    )

    vacancies = Column(
        BigInteger,
        nullable=False,
        comment='How much times the VACANCIES button has been pressed',
        default=1
    )

    news = Column(
        Integer,
        nullable=False,
        comment='How much times the NEWS button has been pressed',
        default=1
    )


    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Deparment(BaseModel):
    __tablename__ = 'department'

    department_name = Column(
        String,
        nullable=False,
        comment='Programming language name'
    )

    customers = relationship('Customer')
    courses = relationship('Course')
    vacancies = relationship('Vacancy')
    news = relationship('News')

    def __repr__(self):
        return self.department_name



class Customer(BaseModel):
    __tablename__ = 'customer'

    first_name = Column(
        String,
        nullable=False,
        comment='How much times the apply button has been pressed'
    )

    last_name = Column(
        String,
        nullable=False,
        comment='How much times the apply button has been pressed'
    )

    phone = Column(
        Integer,
        nullable=False,
        comment='How much times the apply button has been pressed'
    )


    department_id = Column(Integer, ForeignKey('department.id'))

    # _customer = relationship(
    #     'Department',
    #     back_populates='relationships',
    #     cascade='all, delete-orphan'
    # )

    def __repr__(self):
        return f'{self.department.department_name} - {self.first_name} {self.last_name}'


class Course(BaseModel):
    __tablename__ = 'course'

    department_id = Column(Integer, ForeignKey('department.id'))

    # department = relationship(
    #     'Department',
    #     back_populates='courses',
    #     cascade='all, delete-orphan'
    # )

    department_info = Column(
        Text,
        nullable=False,
        comment='The information about course'
    )

    def __repr__(self):
        return f'{self.department.department_name}'


class Vacancy(BaseModel):
    __tablename__ = 'vacancy'

    vacancy_type = Column(
        SmallInteger,
        nullable=False,
        comment='If VACANCY_TYPE = 1 it means that vacancy provided by P-Programist, otherwise the vacancy provided by another resource'
    )

    department_id = Column(Integer, ForeignKey('department.id'))
    # department = relationship(
    #     'Department',
    #     back_populates='vacancies',
    #     cascade='all, delete-orphan'
    # )

    vacancy_label = Column(
        String,
        nullable=False,
        comment='The header of vacancy'
    )

    vacancy_info = Column(
        Text,
        nullable=False,
        comment='These are the details of vacancy'
    )

    def __repr__(self):
        return f'{self.department.department_name} - {self.vacancy_label}'


class News(BaseModel):
    __tablename__ = 'news'

    department_id = Column(Integer, ForeignKey('department.id'))

    # department = relationship(
    #     'Department',
    #     back_populates='news',
    #     cascade='all, delete-orphan'
    # )

    news_source = Column(
        String,
        nullable=False,
        comment='The source where the statistic has been taken from'
    )

    news_label = Column(
        String,
        nullable=False,
        comment='The header of an article'
    )

    def __repr__(self):
        return f'{self.department.department_name} - {self.news_label}'


if __name__ == "__main__":
    import asyncio
    async def recreate_database():
        '''
            When you want to set a connection with the database,
            You have to call the .begin() method from engine.
            After this method initialized You will get asynchronous connection with database.
        '''
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)


    asyncio.run(recreate_database())