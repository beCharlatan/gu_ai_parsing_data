'''

Поля документа:

root_user_id - id рутового пользователя (исследуемый пользователь, тот чьи подписки и чьих подписчиков мы исследуем)
root_user_name = имя рутового пользователя
relative_key = ключ отношения пользователя к рутовому (
    'follower' - подписчик рутового пользователя
    'following' - тот, на кого подписан рутовый пользователь
)
target_user_id - id аккаунта подписки/подписчика
target_user_name - имя акаунта подписки/подписчика
target_user_avatar_url - аватар аккаунта подписки/подписчика

'''

from pymongo import MongoClient
from instaparser.settings import MONGO_DB, MONGO_URI
from instaparser.pipelines import InstaparserPipeline


client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[InstaparserPipeline.collection_name]


def get_followers_by_user_id(user_id: int):
    return collection.find({
        'root_user_id': user_id,
        'relative_key': 'follower'
    })


def get_followers_by_user_name(user_name: str):
    return collection.find({
        'root_user_name': user_name,
        'relative_key': 'follower'
    })


def get_following_by_user_id(user_id: int):
    return collection.find({
        'root_user_id': user_id,
        'relative_key': 'following'
    })


def get_following_by_user_name(user_name: str):
    return collection.find({
        'root_user_name': user_name,
        'relative_key': 'following'
    })
