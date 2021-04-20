from model import *


def add_user(user_id, data, offset=0):
    session = Session()
    user = session.query(User).filter(User.user_vk_id == user_id).first()
    if not user:
        user_vk_id = User(user_vk_id=user_id, data=data, offset=offset)
        session.add(user_vk_id)
        session.commit()
    return


def add_pair(pair_id):
    session = Session()
    pair = session.query(Pair).filter(Pair.pair_vk_id == pair_id).first()
    if not pair:
        pair_vk_id = Pair(pair_vk_id=pair_id)
        session.add(pair_vk_id)
        session.commit()
    return


def add_relation(user_id, pair_id, offset):
    session = Session()

    user = session.query(User).filter(User.user_vk_id == user_id).first()
    pair = session.query(Pair).filter(Pair.pair_vk_id == pair_id).first()
    pair.users.extend([user])
    session.query(User).filter(User.user_vk_id == user_id).update({"offset": offset})
    session.commit()
    return


session = Session()
create_schema()
