import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Subjects(SqlAlchemyBase):
    __tablename__ = 'subjects'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    topics = orm.relation("Topics", back_populates='subjects')
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation("Users", back_populates='subject')



class Topics(SqlAlchemyBase):
    __tablename__ = 'topics'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    subjects_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.id"))
    name = sqlalchemy.Column(sqlalchemy.String)
    subjects = orm.relation('Subjects')
    subtopics = orm.relation("Subtopics", back_populates='topics')


class Subtopics(SqlAlchemyBase):
    __tablename__ = 'subtopics'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    topic_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("topics.id"))
    name = sqlalchemy.Column(sqlalchemy.String)
    topics = orm.relation('Topics')
    exercises = orm.relation('Exercises')
    forum = orm.relation("Forum", back_populates="subtopic")




class Exercises(SqlAlchemyBase):
    __tablename__ = 'exercises'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    subtopics_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subtopics.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    answer = sqlalchemy.Column(sqlalchemy.String)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    solution = sqlalchemy.Column(sqlalchemy.String)
    message = sqlalchemy.Column(sqlalchemy.String)
    subtopics = orm.relation("Subtopics", back_populates='exercises')
    user_exercises = orm.relation("User_exercises", back_populates='exercises')
    forum = orm.relation("Forum", back_populates="exercise")


class Theory(SqlAlchemyBase):
    __tablename__ = 'theory'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sb_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subtopics.id"))
    data = sqlalchemy.Column(sqlalchemy.String)

class Forum(SqlAlchemyBase):
    __tablename__ = 'forum'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    exercise_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exercises.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    parent_id = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relation("Users", back_populates='forum')
    exercise = orm.relation("Exercises")
    subtopic_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subtopics.id"))
    subtopic = orm.relation("Subtopics")







