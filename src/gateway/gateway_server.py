import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo

from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config['MONGO_URI'] = "mongodb://localhost:27017/videos"

mongo = PyMongo(server)
fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route('/login', methods=['POST'])
def login():
    token, error = access.login(request)

    if error:
        return error

    return token, 200

@server.route('/upload', methods=['POST'])
def upload():
    access, error = validate.token(request)
    if error:
        return error

    if access['admin']:
        if not request.files or len(request.files) != 0:
            return {'message': 'No file uploaded or more than 1 file'}, 400
        file = request.files['file']
        err = util.upload_file(file, fs, channel, access)
        if err:
            return err
        return {'message': 'File uploaded successfully'}, 200
    else:
        return {'message': 'User not admin'}, 403

@server.route('/download', methods=['POST'])
def download():
    pass

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)

