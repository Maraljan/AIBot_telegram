from pony import orm

from models import User
from settings import DEFAULT_TOPIC


@orm.db_session
def get(user_id: int) -> User:
    return User[user_id]


@orm.db_session
def create(user_id: int, topic: str = DEFAULT_TOPIC) -> User:
    return User(id=user_id, current_topic=topic)


@orm.db_session
def get_or_create(user_id: int) -> User:
    try:
        return get(user_id)
    except orm.ObjectNotFound:
        return create(user_id)


@orm.db_session
def update(user_id: int, topic: str) -> User:
    user = get(user_id)
    user.current_topic = topic
    return user
