import unittest
from uuid import uuid4

from jsonschema import Draft4Validator, FormatChecker
from openapi_spec_validator import validate_spec
from app import app, spec, tasks, TOKEN


class TasksTest(unittest.TestCase):
    def setUp(self):
        tasks.clear()
        self.client = app.test_client()
        self.headers = {'Authorization': f'Bearer {TOKEN}'}

    def call(self, method, path, **kwargs):
        response = self.client.open(path, method=method, headers=self.headers, **kwargs)
        route = '/tasks/{taskId}' if path.split('?')[0].startswith('/tasks/') else '/tasks'
        definition = spec['paths'][route][method.lower()]['responses'][str(response.status_code)]
        definition = spec['components']['responses'][definition['$ref'].split('/')[-1]]
        if 'content' in definition:
            schema = definition['content'][response.mimetype]['schema']
            Draft4Validator({**schema, 'components': spec['components']},
                            format_checker=FormatChecker()).validate(response.get_json())
        else:
            self.assertEqual(response.data, b'')
        return response

    def test_spec_and_docs(self):
        validate_spec(spec)
        self.assertEqual(spec['openapi'], '3.0.3')
        self.assertEqual(self.client.get('/openapi.json').json, spec)
        self.assertIn(b"url: '/openapi.json'", self.client.get('/docs').data)

    def test_lifecycle(self):
        self.assertEqual(self.client.get('/tasks').status_code, 401)
        response = self.call('POST', '/tasks', json={'title': 'Bài tập B4'})
        self.assertEqual(response.status_code, 201)
        path = response.headers['Location']
        self.assertEqual(response.json['status'], 'open')
        self.assertEqual(response.json['priority'], 'normal')
        self.assertEqual(self.call('GET', path).json, response.json)
        changed = self.call('PATCH', path, json={'status': 'done'})
        self.assertEqual(changed.json['title'], 'Bài tập B4')
        self.assertEqual(self.call('GET', '/tasks?status=open').json['total'], 0)
        self.assertEqual(self.call('GET', '/tasks?status=done&limit=1').json['total'], 1)
        self.assertEqual(self.call('DELETE', path).status_code, 204)
        self.assertEqual(self.call('GET', path).status_code, 404)
        self.assertEqual(self.call('DELETE', path).status_code, 404)

    def test_invalid_input_does_not_mutate(self):
        for data in [{}, [], {'title': ''}, {'title': '  '}, {'title': 'X', 'status': 'bad'},
                     {'title': 'X', 'dueDate': '2026-02-30'}, {'title': 'X', 'id': 'custom'},
                     {'title': 'X', 'assigneeId': 'bad'}, {'title': 'X', 'priority': 1}]:
            self.assertEqual(self.call('POST', '/tasks', json=data).status_code, 422)
        self.assertEqual(tasks, {})
        self.assertEqual(self.call('POST', '/tasks', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.call('POST', '/tasks', data='text').status_code, 400)
        path = self.call('POST', '/tasks', json={'title': 'Keep'}).headers['Location']
        for data in [{}, {'title': None}, {'id': str(uuid4())}, {'unknown': True}]:
            self.assertEqual(self.call('PATCH', path, json=data).status_code, 422)
        self.assertEqual(self.call('GET', path).json['title'], 'Keep')
        for query in ['limit=0', 'limit=101', 'limit=a', 'limit=1.5', 'status=bad']:
            self.assertEqual(self.call('GET', '/tasks?' + query).status_code, 400)
        self.assertEqual(self.call('GET', '/tasks/not-a-uuid').status_code, 400)
        self.assertEqual(self.call('PATCH', '/tasks/' + str(uuid4()), json={'status':'done'}).status_code, 404)


if __name__ == '__main__':
    unittest.main()
