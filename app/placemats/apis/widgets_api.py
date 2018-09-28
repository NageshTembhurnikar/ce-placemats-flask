from flask.views import MethodView
from app.placemats.data.auth0_validator import requires_auth, get_token_auth_header
from app.placemats.stores.store_config import widgets_store, query_log_store
from app.placemats.apis.base_api import BaseApi
from flask import abort
from app.placemats.data.auth0_config import AUTH0_DOMAIN
from datetime import datetime
import requests
import json


class WidgetsApi(MethodView, BaseApi):
    LIMIT_MAX = 10

    @requires_auth
    def get_one(self, pk):
        store = widgets_store()
        widget = store.get(pk=pk)
        self._add_to_query_log(widget)
        if widget is not None:
            return widget
        abort(404)

    @requires_auth
    def get_list(self, skip=None, limit=None):
        return widgets_store().get(skip=skip, limit=limit)


    def _add_to_query_log(self, widget):
        try:
            token = get_token_auth_header()

            url = 'https://' + AUTH0_DOMAIN + '/userinfo'
            headers = {'Authorization': "Bearer " + token}
            response = requests.get(url, headers=headers).content
            response = json.loads(response)

            str_split = widget['_id'].split('_[\'')
            term = str_split[1][:-2]

            q_store = query_log_store()
            q_store.add({
                'term': term,
                'widget': widget['spec_type'],
                'name': response['name'],
                'time': datetime.now()
            })
        except:
            pass