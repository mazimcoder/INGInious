# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Google auth plugin """

import json
import os

import web
from requests_oauthlib import OAuth2Session

from inginious.frontend.user_manager import AuthMethod

authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_url = 'https://www.googleapis.com/oauth2/v4/token'
scope = [
    "email",
    "profile"
]

class GoogleAuthMethod(AuthMethod):
    """
    Google auth method
    """

    def get_auth_link(self, auth_storage, share=False):
        google = OAuth2Session(self._client_id, scope=scope, redirect_uri=web.ctx.home + self._callback_page)
        authorization_url, state = google.authorization_url(authorization_base_url)
        auth_storage["oauth_state"] = state
        return authorization_url

    def callback(self, auth_storage):
        google = OAuth2Session(self._client_id, state=auth_storage["oauth_state"],
            redirect_uri=web.ctx.home + self._callback_page, scope=scope)

        try:
            google.fetch_token(token_url, client_secret=self._client_secret,
                authorization_response=web.ctx.home + web.ctx.fullpath)

            response = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            profile = json.loads(response.content.decode('utf-8'))
            auth_storage["session"] = google
            return str(profile["sub"]), profile["name"], profile["email"]
        except Exception as e:
            return None

    def share(self, auth_storage, course, task, submission, language):
        raise web.seeother("https://plus.google.com/share?url=" + web.ctx.home + "/course/" + course.get_id() + "/" + task.get_id())

    def allow_share(self):
        return True

    def get_id(self):
        return self._id

    def __init__(self, id, name, client_id, client_secret):
        self._id = id
        self._name = name
        self._client_id = client_id
        self._client_secret = client_secret
        self._callback_page = '/auth/callback/' + self._id

    def get_name(self):
        return self._name

    def get_imlink(self):
        return '<img src="/static/icons/google-icon.svg" ' \
               'style="-moz-user-select: none; -webkit-user-select: none;' \
               'user-select: none; width: 50px; height:50px;" >'


def init(plugin_manager, course_factory, client, conf):
    if conf.get("debug", False):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    client_id = conf.get("client_id", "")
    client_secret = conf.get("client_secret", "")

    plugin_manager.register_auth_method(GoogleAuthMethod(conf.get("id"),
        conf.get('name', 'Google'), client_id, client_secret))