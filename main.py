import time
import gmail
import os.path
import threading

from flask import Flask
from flask_restful import Api, Resource

from waitress import serve

app = Flask(__name__)

api = Api()

server_threads_count = 128

phone_numbers = dict()


def start_preparing_mails():
    while True:
        try:
            gmail.prepare_inbox()
            time.sleep(60)
        except Exception as error:
            print('prepare mail error: ', error)


def start_task(start_number, end_number):
    global phone_numbers
    numbers_count = end_number - start_number + 1

    with open('phones_count.txt', 'r') as max_id_file:
        max_id = int(max_id_file.read())

    if numbers_count % max_id == 0:
        cycles_count = numbers_count // max_id
    else:
        cycles_count = numbers_count // max_id + 1

    for cycle in range(cycles_count):
        for phone_id in range(max_id):
            phone_numbers[phone_id] = start_number + phone_id + cycle * max_id

        time.sleep(60)

    phone_numbers = dict()


class GetNumber(Resource):
    def get(self, phone_id):
        if phone_id in phone_numbers:
            return '+' + phone_numbers[phone_id]
        else:
            return ' '


class StartTask(Resource):
    def get(self, start_number, end_number):
        if threading.active_count() == (server_threads_count + 1 + 1):
            if end_number >= start_number:
                threading.Thread(target=start_task, args=[start_number, end_number]).start()
                return {'started': True}

        return {'started': False}


class GetData(Resource):
    def get(self, country):
        data_path = os.path.join('data', country + '.txt')
        if os.path.exists(data_path):
            with open(data_path, 'r') as data:
                return data.read()

        return 'No data'


class SetPhonesCount(Resource):
    def get(self, phones_count):
        with open('phones_count.txt', 'w') as data:
            return data.write(str(phones_count))


api.add_resource(GetNumber, '/get_number/<int:phone_id>')
api.add_resource(StartTask, '/start_task/<int:start_number>/<int:end_number>/')
api.add_resource(GetData, '/get_data/<string:country>')
api.add_resource(SetPhonesCount, '/set_max_id/<int:phones_count>')
api.init_app(app)

if __name__ == '__main__':
    threading.Thread(target=start_preparing_mails).start()
    serve(app, host="0.0.0.0", port=80, threads=server_threads_count)