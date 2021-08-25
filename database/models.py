"""The module is responsible for tables and relations betweeen them inside of the database."""
# Standard library imports
import datetime

# Third party imports
from sqlalchemy import (
    Column, ForeignKey,
    Integer, String, TIMESTAMP,
    SmallInteger, BigInteger, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import insert

# Local application imports
from database.settings import engine
from configs.constants import (
    PYTHON_INFO_TEXT_RU, PYTHON_INFO_TEXT_KG,
    SYS_ADMIN_INFO_TEXT_RU, SYS_ADMIN_INFO_TEXT_KG,
    JAVASCRIPT_INFO_TEXT_RU, JAVASCRIPT_INFO_TEXT_KG,
    JAVA_INFO_TEXT_RU, JAVA_INFO_TEXT_KG,
    ABOUT_COMPANY_RU, ABOUT_COMPANY_KG
)

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

    about_company_text = Column(
        Text,
        nullable=False,
        comment='The general information about company'
    )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Department(BaseModel):
    __tablename__ = 'department'

    department_name = Column(
        String,
        nullable=False,
        unique=True,
        comment='Programming language name'
    )

    customers = relationship('Customer', back_populates='department')
    courses = relationship('Course', back_populates='department')
    news = relationship('News', back_populates='department')

    def __repr__(self):
        return self.department_name


class Customer(BaseModel):
    __tablename__ = 'customer'

    chat_id = Column(
        Integer,
        nullable=False,
        comment='The chat id of User who applied for registration'
    )

    first_name = Column(
        String,
        nullable=False,
        comment='How much times the apply button has been pressed'
    )

    last_name = Column(
        String,
        nullable=True,
        comment='How much times the apply button has been pressed'
    )

    phone = Column(
        BigInteger,
        nullable=True,
        comment='How much times the apply button has been pressed'
    )

    time = Column(
        SmallInteger,
        nullable=True,
        comment='The time when a group start to study. Morning or Evening'
    )

    department_name = Column(
        String,
        ForeignKey('department.department_name'),
        nullable=False
    )

    department = relationship(
        "Department",
        back_populates="customers"
    )

    def __repr__(self):
        return f'{self.department_name} | {self.first_name} | {self.last_name}'


class Course(BaseModel):
    __tablename__ = 'course'

    department_id = Column(
        Integer,
        ForeignKey('department.id'),
        nullable=False
    )

    department = relationship(
        "Department",
        back_populates="courses"
    )

    department_info = Column(
        Text,
        nullable=False,
        comment='The information about course'
    )

    def __repr__(self):
        return f'{self.department}'


class Vacancy(BaseModel):
    __tablename__ = 'vacancy'

    vacancy_type = Column(
        SmallInteger,
        nullable=False,
        comment='If VACANCY_TYPE = 0 it means that vacancy provided by P-Programist, otherwise the vacancy provided by another resource'
    )

    position = Column(
        String,
        nullable=False,
        comment='The header of vacancy'
    )

    time = Column(
        String,
        nullable=False,
        comment='The time of lesson'
    )

    salary = Column(
        String,
        nullable=False,
        comment='The salary of a mentor'
    )

    details = Column(
        Text,
        nullable=False,
        comment='These are the details of vacancy'
    )

    # This line is binded with the VACANCY field in VacancyApplicants class.
    applicants = relationship('VacancyApplicants', back_populates='vacancy')

    def __repr__(self):
        return f'{self.position}'


class VacancyApplicants(BaseModel):
    __tablename__ = 'vacancy_applicants'

    vacancy_id = Column(
        Integer,
        ForeignKey('vacancy.id'),
        nullable=False
    )

    vacancy = relationship(
        "Vacancy",
        back_populates="applicants"
    )

    chat_id = Column(
        Integer,
        nullable=False,
        comment='The chat id of User who applied for vacancy'
    )

    full_name = Column(
        String,
        nullable=True,
        comment='The full name of applicant'
    )

    cover_letter = Column(
        Text,
        nullable=True,
        comment='This cover letter has to be written in order to see applicants\'s interests'
    )

    github_link = Column(
        String,
        nullable=True,
        comment='A GitHub link to check applicant\'s experience'
    )

    phone_number = Column(
        BigInteger,
        nullable=True,
        comment='The contact number of applicant'
    )

    def __repr__(self):
        return f'{self.full_name} - {self.phone_number}'


class News(BaseModel):
    __tablename__ = 'news'

    department_id = Column(
        Integer,
        ForeignKey('department.id'),
        nullable=False
    )

    department = relationship(
        "Department",
        back_populates="news"
    )

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
    from sqlalchemy.ext.asyncio import AsyncSession

    async def recreate_database():
        '''
            When you want to set a connection with the database,
            You have to call the .begin() method from engine.
            After this method initialized You will get asynchronous connection with database.
        '''
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                python = Department(id=1, department_name='Python')
                sys_admin = Department(
                    id=2, department_name='System Administrator')
                javascript = Department(id=3, department_name='Javascript')
                java = Department(id=4, department_name='Java')
                about = Reception(
                    apply=0, about_courses=0,
                    about_company=0, vacancies=0,
                    news=0, about_company_text=ABOUT_COMPANY_RU
                )
                session.add_all(
                    [about,
                        python,
                        sys_admin,
                        javascript,
                        java
                     ]
                )

            python_info = insert(Course).values(
                {
                    "department_info": PYTHON_INFO_TEXT_RU,
                    "department_id": python.id
                }
            )
            sys_admin_info = insert(Course).values(
                {
                    "department_info": SYS_ADMIN_INFO_TEXT_RU,
                    "department_id": sys_admin.id
                }
            )
            javascript_info = insert(Course).values(
                {
                    "department_info": JAVASCRIPT_INFO_TEXT_RU,
                    "department_id": javascript.id
                }
            )

            sys_admin_vacancy = insert(Vacancy).values(
                {
                    "vacancy_type": 0,
                    "position": "*М-Ментор на курс `Системный Администратор`*",
                    "time": "Договорный",
                    "salary": "*15000 - 25000 com*",
                    "details": '''Требования:

    ✅ Чёткое понимание и возможность объяснить зачем нужна эта должность
    ✅ Опыт администрирования операционных систем Linux и Windows Server
    ✅ Английский - Pre-Intermediate | Intermediate
    ✅ Основы стека TCP/IP
    ✅ Умение использовать ActiveDirectory, DNS, DHCP
    ✅ Знание и понимание протоколов (FTP, SSH, SMTP, POP3, SAMBA)
    ✅ Знание любового скриптового ЯП
    ✅ Навыки работы с СУБД приветствуется
    ✅ Комерческий опыт работы от 1-2х лет


Обязанности:
    ⚜️ Разработка и поддержка учебного плана
    ⚜️ Обучение студентов, проведение занятий'''
                }
            )

            await session.execute(python_info)
            await session.execute(sys_admin_info)
            await session.execute(javascript_info)
            await session.execute(sys_admin_vacancy)
            await session.commit()

    asyncio.run(recreate_database())




