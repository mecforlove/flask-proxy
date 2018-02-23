# coding: utf-8
import requests

from flask import request


class Proxy(object):
    def __init__(self, app=None):
        self.upstreams = []
        self.init_app(app)

    def init_app(self, app):
        """Initialize this class with the given :class:`flask.Flask`
        application.

        :param app: the Flask application
        :type app: flask.Flask
        """
        self.app = app

    def add_upstream(self, upstream):
        """Add a upstream to the proxy.

        """
        endpoint = getattr(upstream, 'endpoint',
                           None) or upstream.__name__.lower()
        upstream.endpoint = endpoint
        self.upstreams.append(upstream)
        view_func = upstream.as_view()
        for dec in upstream.decorators:
            view_func = dec(view_func)
        for route in upstream.routes:
            rule = upstream.prefix + route['url']
            self.app.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=view_func,
                methods=route['methods'])


class Upstream(object):
    scheme = 'http'
    port = 80
    decorators = []
    params = {}

    @classmethod
    def as_view(cls):
        base_url = '%s://%s:%s' % (cls.scheme, cls.host, cls.port)

        def _view(*args, **kwargs):
            method = request.method
            uri = request.url.split(cls.prefix)[1]
            url = base_url + uri
            params = cls.params
            if callable(params):
                params = params()
            headers = dict(request.headers)
            headers['Host'] = cls.host
            resp = requests.request(
                method,
                url,
                params=params,
                headers=headers,
                data=request.get_data())
            return resp.content, dict(resp.headers)

        return _view
