import unittest
import json

from flask import Flask
from flask_proxy import Proxy, Upstream


class TestProxy(unittest.TestCase):
    def setUp(self):
        class HttpbinBase(Upstream):
            prefix = '/httpbin'
            host = 'httpbin.org'

        self.HttpbinBase = HttpbinBase

        class HttpbinGet(self.HttpbinBase):
            routes = [{
                'url': '/get',
                'methods': ['GET'],
            }]

        class HttpbinPost(self.HttpbinBase):
            routes = [{'url': '/post', 'methods': ['POST']}]

        class HttpbinDelete(self.HttpbinBase):
            routes = [{'url': '/delete', 'methods': ['DELETE']}]

        class HttpbinPut(self.HttpbinBase):
            routes = [{'url': '/put', 'methods': ['PUT']}]

        class HttpbinPatch(self.HttpbinBase):
            routes = [{'url': '/patch', 'methods': ['PATCH']}]

        self.HttpbinGet = HttpbinGet
        self.HttpbinPost = HttpbinPost
        self.HttpbinDelete = HttpbinDelete
        self.HttpbinPut = HttpbinPut
        self.HttpbinPatch = HttpbinPatch

    def test_get(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinGet)

        with app.test_client() as client:
            resp = client.get('/httpbin/get')
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/get', resp_json_data['url'])
            self.assertIn('origin', resp_json_data)
            self.assertIn('args', resp_json_data)
            self.assertIn('headers', resp_json_data)

            resp = client.get('/httpbin/get1')
            self.assertEqual('404 NOT FOUND', resp.status)

    def test_get_with_params(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinGet)

        with app.test_client() as client:
            resp = client.get('/httpbin/get?a=1')
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertIn('origin', resp_json_data)
            self.assertIn('headers', resp_json_data)
            self.assertEqual('http://httpbin.org/get?a=1',
                             resp_json_data['url'])
            self.assertEqual({'a': '1'}, resp_json_data['args'])

    def test_post_form(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinPost)

        with app.test_client() as client:
            resp = client.post('/httpbin/post', data=dict(a=1, b=2))
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/post', resp_json_data['url'])
            self.assertEqual({'a': '1', 'b': '2'}, resp_json_data['form'])

    def test_post_json(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinPost)

        with app.test_client() as client:
            resp = client.post(
                '/httpbin/post',
                data=json.dumps(dict(
                    a=1, b=2)),
                content_type='application/json')
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/post', resp_json_data['url'])
            self.assertEqual({'a': 1, 'b': 2}, resp_json_data['json'])

    def test_delete(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinDelete)

        with app.test_client() as client:
            resp = client.delete('/httpbin/delete', data=dict(a=1, b=2))
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/delete',
                             resp_json_data['url'])
            self.assertEqual({'a': '1', 'b': '2'}, resp_json_data['form'])

    def test_put(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinPut)

        with app.test_client() as client:
            resp = client.put('/httpbin/put', data=dict(a=1, b=2))
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/put', resp_json_data['url'])
            self.assertEqual({'a': '1', 'b': '2'}, resp_json_data['form'])

    def test_patch(self):
        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(self.HttpbinPatch)

        with app.test_client() as client:
            resp = client.patch('/httpbin/patch', data=dict(a=1, b=2))
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/patch', resp_json_data['url'])
            self.assertEqual({'a': '1', 'b': '2'}, resp_json_data['form'])

    def test_add_params(self):
        class HttpbinGetWithParams(self.HttpbinGet):
            params = {'foo': 'foo'}

        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(HttpbinGetWithParams)

        with app.test_client() as client:
            resp = client.get('/httpbin/get')
            self.assertEqual('200 OK', resp.status)
            resp_json_data = json.loads(resp.data)
            self.assertEqual('http://httpbin.org/get?foo=foo',
                             resp_json_data['url'])
            self.assertEqual({'foo': 'foo'}, resp_json_data['args'])

    def test_decorators(self):
        def return_ok(func):
            def wrapper(*args, **kwargs):
                return 'ok'

            return wrapper

        class HttpbinGetWithDec(self.HttpbinGet):
            decorators = [return_ok]

        app = Flask(__name__)
        proxy = Proxy(app)
        proxy.add_upstream(HttpbinGetWithDec)

        with app.test_client() as client:
            resp = client.get('/httpbin/get')
            self.assertEqual('200 OK', resp.status)
            self.assertEqual('ok', resp.data.decode('utf-8'))
