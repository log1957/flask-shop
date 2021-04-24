import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User2(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'contacts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    number0 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time0 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<user> {self.id} {self.number} {self.time}"

