import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

with open('txts\\dsn.txt') as f:
    DSN = f.readline()

engine = sq.create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_vk_id = sq.Column(sq.Integer)
    data = sq.Column(sq.JSON)
    offset = sq.Column(sq.Integer)


user_pair = sq.Table(
    'user_pair', Base.metadata,
    sq.Column('user_id', sq.Integer, sq.ForeignKey('user.id')),
    sq.Column('pair_id', sq.Integer, sq.ForeignKey('pair.id')),
)


class Pair(Base):
    __tablename__ = 'pair'

    id = sq.Column(sq.Integer, primary_key=True)
    # id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ))
    pair_vk_id = sq.Column(sq.Integer)
    users = relationship(User, secondary=user_pair, backref='pairs')


def create_schema():
    Base.metadata.create_all(bind=engine)
