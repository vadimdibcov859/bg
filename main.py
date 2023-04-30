import time
import os.path
import threading

from flask import Flask
from flask_restful import Api, Resource

from waitress import serve

app = Flask(__name__)

api = Api()

server_threads_count = 128

phone_numbers = dict()

country = [380, 998, 1, 86, 49, 33, 81]


def detect_county(number):
    for code in country:
        if str(code) == str(number)[:len(str(code))]:
            return code

    return 0


def add_number(number, is_an_apple_num):
    with open('checked_numbers.txt', 'r') as checked_numbers_file:
        if str(number) in checked_numbers_file.read().split():
            return

    country_data_file = f'{detect_county(number)}{["green", "blue"][is_an_apple_num]}.txt'

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(os.path.join('data', country_data_file), 'a') as file:
        file.write(str(number) + '\n')

    with open('checked_numbers.txt', 'a') as checked_numbers_file:
        checked_numbers_file.write(str(number) + '\n')


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
            return 'TO DO "EMPTY" NUMBER'


class StartTask(Resource):
    def get(self, start_number, end_number):
        if threading.active_count() == (server_threads_count + 1):
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


class AddGreen(Resource):
    def get(self, number):
        add_number(number, False)


class AddBlue(Resource):
    def get(self, number):
        add_number(number, True)


api.add_resource(GetNumber, '/get_number/<int:phone_id>')
api.add_resource(StartTask, '/start_task/<int:start_number>/<int:end_number>/')
api.add_resource(GetData, '/get_data/<string:country>')
api.add_resource(SetPhonesCount, '/set_max_id/<int:phones_count>')
api.add_resource(AddGreen, '/add_green/<int:number>')
api.add_resource(AddBlue, '/add_blue/<int:number>')
api.init_app(app)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80, threads=server_threads_count)
