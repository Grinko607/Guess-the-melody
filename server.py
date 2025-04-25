from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Чем я могу помочь?'
        res['response']['buttons'] = get_start_buttons()
        return

    if 'угадай мелодию' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Выбери категорию или ты можешь, сыграть в режим "случайная мелодия":'
        res['response']['buttons'] = get_categories_or_random()
        return

    if 'категор' in req['request']['original_utterance'].lower():
        res['session']['state'] = 'waiting_for_category'
        res['response']['text'] = 'Выбери категорию:'
        res['response']['buttons'] = get_categories()
        return

    if 'узыка' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Выбери уровень сложности:'
        res['response']['buttons'] = get_difficulty_levels()
        return

    if 'случай' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Угадаешь, что за музыка играет?'
        return

    res['response']['text'] = 'Я не понимаю, что ты имеешь в виду. Попробуй снова.'
    res['response']['buttons'] = get_categories_or_random()


def get_start_buttons():
    return [
        {'title': 'играть в угадай мелодию', 'hide': True}
    ]


def get_categories_or_random():
    return [
        {'title': 'Выбрать категорию', 'hide': True},
        {'title': 'Случайная мелодия', 'hide': True}
    ]


def get_categories():
    categories = [
        {'title': 'Музыка из кинофильмов', 'hide': True},
        {'title': 'Зарубежная музыка', 'hide': True},
        {'title': 'Современная музыка', 'hide': True},
        {'title': 'Советская музыка', 'hide': True},
        {'title': 'Классическая музыка', 'hide': True}
    ]
    return categories


def get_difficulty_levels():
    return [
        {'title': 'Лёгкий', 'hide': True},
        {'title': 'Средний', 'hide': True},
        {'title': 'Сложный', 'hide': True}
    ]



if __name__ == '__main__':
    app.run()
