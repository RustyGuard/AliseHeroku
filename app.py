import os

from flask import Flask, request
import logging
import json
from geo import get_country, get_distance, get_coordinates

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        print('No name')
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я могу показать город или сказать расстояние между городами!'
    else:
        print('Stonks')
        first_name = sessionStorage[user_id]['first_name']

        cities = get_cities(req)

        if len(cities) == 0:
            print('Stonks 0')
            res['response']['text'] = 'Ты не написал название не одного города!'

        elif len(cities) == 1:
            print('Stonks 1')
            res['response']['text'] = 'Этот город в стране - ' + get_country(cities[0])

        elif len(cities) == 2:
            print('Stonks 2')
            distance = get_distance(get_coordinates(cities[0]), get_coordinates(cities[1]))
            res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'

        else:
            print('Stonks >2')
            res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':

            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])

    return cities


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
