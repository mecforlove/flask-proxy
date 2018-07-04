# coding: utf-8
import requests

from flask import request, Response


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
        if upstream.decorators:
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
    host = None
    scheme = None
    port = None
    decorators = None
    params = None

    @staticmethod
    def _get_attr(attr, default=None):
        if callable(attr):
            return attr() or default
        return attr or default

    @classmethod
    def as_view(cls):
        def _view(*args, **kwargs):
            host = cls._get_attr(cls.host)
            scheme = cls._get_attr(cls.scheme, 'http')
            params = cls._get_attr(cls.params)
            port = cls._get_attr(cls.port, 80)
            method = request.method
            uri = request.url.split(cls.prefix)[1]
            base_url = '%s://%s:%s' % (scheme, host, port)
            url = base_url + uri
            headers = dict(request.headers)
            # Change `Host` in request header.
            headers['Host'] = host
            resp = requests.request(
                method,
                url,
                params=params,
                headers=headers,
                data=request.get_data(),
                stream=True)
            # Remove some response headers.
            excluded_headers = [
                'content-length', 'transfer-encoding', 'connection'
            ]
            for h in excluded_headers:
                if h in resp.headers:
                    resp.headers.pop(h)
            return Response(resp.raw.read(), resp.status_code, dict(resp.headers))

        return _view
