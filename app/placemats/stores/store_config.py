import logging
from app.placemats.stores.mongo_store import MongoStore
from app.placemats.stores.store import BaseStore
from app.placemats.stores.mongo_client import mongo_db

logger = logging.getLogger(__name__)

store_class = MongoStore


def _get_store(resource_name) -> BaseStore:
    if store_class is MongoStore:
        return MongoStore(mongo_db()[resource_name], '/{}/'.format(resource_name))


def layouts_store() -> BaseStore:
    return _get_store('layouts')


def widgets_store() -> BaseStore:
    return _get_store('widgets')


def query_log_store() -> BaseStore:
    return _get_store('query_log')
