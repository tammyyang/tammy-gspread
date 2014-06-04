#!flask/bin/python

from flask import Flask, jsonify, abort, make_response, request
import datetime

test = Flask(__name__)

tasks = [
    {
        'timestamp': datetime.datetime(2014, 6, 4, 18, 34, 49, 11111),
        'value': 1,
        'id': 1
    },
    {
        'timestamp': datetime.datetime(2014, 6, 4, 18, 35, 49, 11111),
        'value': 7,
        'id': 2
    },
    {
        'timestamp': datetime.datetime(2014, 6, 4, 18, 34, 48, 11111),
        'value': 2,
        'id': 3
    },
    {
        'timestamp': datetime.datetime(2014, 6, 4, 18, 35, 47, 11111),
        'value': -2,
        'id': 4
    },
]

#curl -i http://localhost:5000/todo/api/v1.0/tasks
@test.route('/todo/api/v1.0/tasks', methods = ['GET'])
def get_tasks():
    return jsonify( { 'tasks': tasks } )

#curl -i http://localhost:5000/todo/api/v1.0/tasks/latest
@test.route('/todo/api/v1.0/tasks/<latest>', methods = ['GET'])
def get_task(latest):
    filtered_data = [data for data in tasks if (datetime.datetime.now() - data['timestamp']).seconds < 120]
    return jsonify( { 'task': filtered_data } )

#curl -i http://localhost:5000/todo/api/v1.0/tasks/30
@test.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

from flask import request

#curl -i -H "Content-Type: application/json" -X POST -d '{"value": 7}' http://localhost:5000/todo/api/v1.0/tasks
@test.route('/todo/api/v1.0/tasks', methods = ['POST'])
def create_task():
    if not request.json or not 'value' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'timestamp': datetime.datetime.now(),
        'value': request.json['value'],
    }
    tasks.append(task)
    return jsonify( { 'task': task } ), 201


#curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/todo/api/v1.0/tasks/2
@test.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify( { 'result': True } )

if __name__ == '__main__':
    test.run(debug = True)
