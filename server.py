from flask import Flask, request, jsonify
import random
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3

app = Flask(__name__)

# Словари, содержащие аудиофайлы для разных категорий и уровней сложности
audio_files = {
    "Музыка из кинофильмов": {
        "Лёгкий": {
            '7f2eb1da-330f-48da-97ab-cdc066ca8782': 'Over the Rainbow',
            '59bb4fe4-6a3a-471e-90ff-c6a567f98d97': 'My Heart Will Go On',
            '583a4b4f-19ba-4360-88d6-770e03fac52f': 'Star Wars',
            'ba058234-ba80-4dc1-b996-5c1e45d2158d': 'Eye of the Tiger'
        },
        "Средний": {
            '052b0b3e-303e-439b-b30f-a39bce078757': "Hedwig's Theme",
            'd1cdcd57-acfa-40b8-a8bd-50f4c70ab28b': 'The Good, The Bad and The Ugly',
            '37cd47d2-c34a-46b9-94e9-6adb8f21c1ed': 'A Whole New World',
            '511f21f6-599d-4f0d-8c41-c393d289e087': 'The Circle of Life',
            'd3034d8b-b1c3-4c1d-b38d-0ccbdcdb17c4': 'Time'
        },
        "Сложный": {
            'ac76fd99-5ec9-4b80-873e-6100721c66a5': 'Lux Aeterna',
            '079f8ee4-3c2b-4650-8d37-a3b6317b89d7': 'The Ecstasy of Gold',
            'd17bb38f-1d47-4dc8-9afb-5bf1df407f99': 'Now We Are Free',
            '74409b3c-bcf5-4e0a-9467-fc4ccac19ba6': 'The Lord of the Rings',
            'bf68335d-c634-4c21-ae16-fdbbfc0cc3a9': 'Main Theme'
        }
    },
    "Зарубежная музыка": {
        "Лёгкий": {
            '28a60845-a0f7-46c9-8341-1af22b29f70a': 'Shape of You',
            'eaee5d0c-7b52-4994-89f7-d74f2e016325': 'Rolling in the Deep',
            '5cd852ee-85f4-4138-8bb5-62e5bc3ebd49': 'Uptown Funk',
            'c847f9cf-7626-4ee0-973a-47604cb9af91': 'Despacito',
            '5a3512d8-71c0-44a1-8b33-49d4f416473e': 'Happy'
        },
        "Средний": {
            'c14ae360-fb66-49f1-83a3-7f5dfe96bd30': 'Someone Like You',
            '9aaf7947-739e-4eef-9022-3bae5df866f1': 'Blinding Lights',
            '3992c23f-156f-4fa0-b865-8fad36caffee': 'Shallow',
            '8530e7fb-6c0f-4f0f-a33d-3b89bd14e0ce': 'Viva La Vida',
            '5324599f-424e-46d3-a20e-291d52f44aa1': 'Thinking Out Loud'
        },
        "Сложный": {
            '3127b320-78d5-4339-95c3-b73e384095e5': 'Bohemian Rhapsody',
            '6112b185-a464-4b1a-9fbf-3364675983d6': 'Stairway to Heaven',
            '7a005f86-ba9f-43ca-86cd-441970ea29a5': 'Hotel California',
            'a142e7f2-7437-4705-ba52-07de53f49b19': 'Blackbird',
            '9d6d997e-3cc6-40da-8be7-5f3696212bfd': 'Creep'
        }
    },
    'Современная музыка': {
        "Лёгкий": {
            '12c6714c-a51d-4fc8-8ce2-fdcf17bd19a1.opus': 'Имя 505',
            '3f11be2f-aa2e-4c3f-ac6f-b2a64d40b161': 'Bad gay',
            'd37d7319-9bf5-4e43-aff6-8d6b64cdd865': 'Watermelon Sugar',
            '7c5b0358-e414-4f02-8baa-8c3d3d5b97d7': 'Old Town Road',
            '89886edc-82ee-467d-8dd9-2794f147f190': 'Повод'
        },
        "Средний": {
            'c2a9e9f3-795d-4428-9533-37076eadfd50': 'Party Tyme',
            '9aaf7947-739e-4eef-9022-3bae5df866f1': 'Blinding Lights',
            '5f68a605-6f71-4fdc-98d0-ef810b016615': 'Stay',
            '824393d5-d0e7-49f4-a226-5fd8f2c8f401': 'Твои глаза',
            '65b4d681-6e20-4cdd-8f82-2eb7fd89ccc0': 'Сансара'
        },
        "Сложный": {
            'e49696e0-7b66-4af0-8b28-9f2fb75efa80': 'Царица',
            '9d6d997e-3cc6-40da-8be7-5f3696212bfd': 'Creep',
            '53bc0e1e-7cf6-4d67-9379-1ff445267feb': 'Мама, я танцую',
            'e93de048-5921-46dd-9b1a-220206ec51be': 'INDUSTRY BABY',
            '219f666c-7e43-4a79-8894-3e605bc145e1': 'Save Your Tears'
        }
    },
    'Советская музыка': {
        "Лёгкий": {
            '615f9cf6-c479-4481-a157-ddae86c577fa': 'В лесу родилась ёлочка',
            'b33aacf7-e723-4d1a-bd52-9f5f7bf6a4b1': 'Звезда по имени солнце',
            '718860b7-d4d4-4bf2-a7b2-3b8b594e0937': 'Калинка',
            '4c3bb49e-ea02-4f24-b59b-a1fd753f4a60': 'Синий платочек',
            'bbdf7375-9070-40f9-87aa-df135a09d026': 'Подмосковные вечера'
        },
        "Средний": {
            'a3be7364-2f30-46ed-a85b-a31ae4311549': 'Старый Клён',
            '48fe8ca1-ea5b-4238-a6c2-e445a8ff6e7b': 'Песня о нейтральной полосе',
            'a2875a42-100a-48a3-98e7-15bf57ad912c': 'Миллион алых роз',
            '503f8c4f-a5f8-4b44-bf1e-a2235b956dcf': 'Течёт река Волга',
            'c5ed79cf-e848-4192-a749-3b42a5208a24': 'Где-то далеко'
        },
        "Сложный": {
            '23859071-e372-4daf-89a0-84c6d899b4d2': 'Очи черные',
            '9e976477-6108-4e1f-a784-a9acd5766480': 'Песенка о переселении душ',
            '15fef0ec-ebc9-42a3-9a9b-85dad26c94be': 'Солнечный день',
            '5cb81f8b-a764-4bbd-a2e5-02e51bb30a61': 'Я спросил у ясеня',
            '821c69db-7e53-43ba-85fc-44b92b48a422': 'Спокойная ночь'
        }
    },
    'Классическая музыка': {
        "Лёгкий": {
            'c3e3f4ed-528d-44b0-a4c1-6c8f83525250': 'Лунная соната',
            '99af93f6-d7b4-4fef-ad11-f39a8b80d676': 'Танец фей драже',
            '9aaff662-15e7-427a-8802-0baa8b5f4c2e': 'В пещере горного короля',
            '01ed0c16-c862-4d65-9b04-0f5c4aef6bbc': 'Поль Мориа',
            '7c9c0be6-7d74-458e-b878-bca7618bd928': 'Вальс цветов'
        },
        "Средний": {
            '78b18941-ad33-4c8f-b562-e91dbe1e7716': 'Симфония № 9',
            '6fed6b8b-597f-40df-8347-2907e499ba41': 'Симфония № 5',
            '85b87065-d8f8-4982-ac04-0dd74e54457d': 'Лакримоза',
            'f97b2818-f087-4cd8-a47a-7316703b8896': 'Кармен-Сюита, Марш тореадоров',
            '4ebe5765-4317-41ad-87f3-97b1eaa1fb05': 'К Элизе'
        },
        "Сложный": {
            '1a538128-4960-43c3-a5e6-e2bee19e9871': 'Симфония № 1',
            'ee38a2ed-69ce-4867-b211-dd70413d3ca0': 'Симфония № 9',
            '41b541cf-272a-4c30-ae37-046f68faf910': 'Песня Юродивого',
            '42d87cd4-6011-4c5e-8d6c-49fb1f77ab9f': 'Токката и фуга ре минор',
            'c1ae5c59-234e-45e2-ad7e-4a995daeb3bf': 'Симфония № 9'
        }
    },
}

# Списки категорий и уровней сложности для выбора
CATEGORIES = list(audio_files.keys())
DIFFICULTIES = ['Лёгкий', 'Средний', 'Сложный']

# Словарь для хранения баллов пользователей (не используется при работе с БД)
user_scores = {}

# Словарь для хранения состояния текущей игровой сессии
sessionStorage = {}

# Настройка SQLAlchemy для работы с базой данных через ORM
Base = declarative_base()

# Определение модели для таблицы сессий
class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    user_score = Column(Integer, default=0)

# Модель для таблицы отзывов, где session_id связывается с таблицей sessions
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    comment = Column(String, nullable=False)

# Создание подключения к базе данных SQLite
DATABASE_URL = 'sqlite:///sessions.db'
engine = create_engine(DATABASE_URL)

# Создание таблиц в базе данных, если их ещё нет
Base.metadata.create_all(engine)

# Создание объекта сессии для работы с БД через SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция-генератор для получения сессии БД (SQLAlchemy)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания соединения с SQLite (без SQLAlchemy)
def get_db_connection():
    conn = sqlite3.connect('sessions.db')
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по именам
    return conn

# Создание таблиц через sqlite3, если они отсутствуют (резервный вариант)
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_score INTEGER DEFAULT 0
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    conn.commit()
    conn.close()

# Вызов функции для создания таблиц при старте приложения
create_tables()

# Функция для получения идентификатора сессии из БД или создания новой записи
def get_or_create_session(session_id):
    db = next(get_db())
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if session is None:
        session = Session(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session.id

# Переменная для контроля состояния игры вне контекста отдельной сессии
game_state = None

@app.route('/post', methods=['POST'])
def dialog_handler():
    """
    Основной обработчик запросов.
    В зависимости от типа запроса и состояния сессии выбирается нужная логика обработки.
    """
    event = request.json
    res = {
        'session': event['session'],
        'version': event['version'],
        'response': {
            'end_session': False
        }
    }
    # Получаем идентификатор сессии для работы с БД
    session_id = event['session']['session_id']
    session_id_db = get_or_create_session(session_id)

    # Если это новая сессия, вызываем обработчик старта
    if event['session']['new']:
        return jsonify(start_handler(res))
    # Обработка нажатия кнопки
    elif event['request']['type'] == 'ButtonPressed':
        return jsonify(button_handler(res, event, session_id_db))
    # Если игра находится в состоянии ожидания отзыва, обрабатываем отзыв
    elif game_state == 'waiting_for_feedback':
        return jsonify(leave_feedback_handler(res, event, session_id_db))
    # Остальные случаи — попытка ответа игрока
    else:
        return jsonify(answer_handler(res, event, session_id_db))

def button_handler(res, event, session_id_db):
    """
    Обработка нажатий кнопок, определяет дальнейший путь игры в зависимости
    от информации, полученной в payload.
    """
    global game_state
    if game_state == 'waiting_for_feedback':
        # Сбрасываем состояние ожидания отзыва и обрабатываем отзыв
        game_state = None
        return leave_feedback_handler(res, event, session_id_db)
    elif event['request']['payload']['next_event'][0]['event'] == 'start_game':
        return start_game_handler(res)
    elif event['request']['payload']['next_event'][0]['event'] == 'choose_category':
        return choose_category_handler(res, event, session_id_db)
        elif event['request']['payload']['next_event'][0]['event'] == 'choose_difficulty':
        return choose_difficulty_handler(res, event, session_id_db)
    elif event['request']['payload']['next_event'][0]['event'] == 'end_game':
        return end_game_handler(res, session_id_db)
    elif event['request']['payload']['next_event'][0]['event'] == 'leave_feedback':
        return leave_feedback_handler(res, event, session_id_db)
    elif event['request']['payload']['next_event'][0][
        'event'] == 'view_feedback':  # Обработка нажатия кнопки "Посмотреть отзывы"
        return view_feedback_handler(res)
    elif event['request']['payload']['next_event'][0]['event'] == 'exit_game':
        return exit_game_handler(res)
    else:
        return random_song_handler(res, session_id_db)


def start_game_handler(res):
    """
    Обработчик для старта игры.
    Выбирается случайная категория и уровень сложности, затем выбирается случайный аудиофайл.
    """
    # Выбираем случайную категорию и уровень сложности
    category = random.choice(CATEGORIES)
    difficulty = random.choice(DIFFICULTIES)
    # Выбираем случайный аудиофайл из указанной категории и уровня
    file_id, track_name = random.choice(list(audio_files[category][difficulty].items()))

    # Сохраняем выбранные параметры в sessionStorage для дальнейших обращений
    sessionStorage['current_category'] = category
    sessionStorage['current_difficulty'] = difficulty
    sessionStorage['current_file'] = file_id
    sessionStorage['track_name'] = track_name

    # Формируем сообщение для пользователя с указанием выбранной категории и сложности
    res['response']['text'] = (
        f"Начинаем игру! Ваша категория: {category}, уровень сложности: {difficulty}. \n"
        "Слушайте аудиофайл и угадайте название композиции."
    )
    # Дополнительно можно вернуть аудиофайл в виде ссылки или идентификатора
    res['response']['tts'] = f"Воспроизведение трека {track_name}."
    return res


def choose_category_handler(res, event, session_id_db):
    """
    Обработчик для выбора категории.
    Здесь можно реализовать переключение между категориями или подтверждение выбора игрока.
    """
    # Извлекаем выбранную категорию из payload
    chosen_category = event['request']['payload']['next_event'][0].get('category')
    if chosen_category not in audio_files:
        res['response']['text'] = "Такой категории нет. Пожалуйста, выберите другую категорию."
        return res

    # Сохраняем выбранную категорию в sessionStorage
    sessionStorage['current_category'] = chosen_category
    res['response'][
        'text'] = f"Вы выбрали категорию: {chosen_category}.\nВыберите уровень сложности: Лёгкий, Средний или Сложный."
    return res


def answer_handler(res, event, session_id_db):
    """
    Обработчик для проверки ответа игрока.
    Сравнивается ответ пользователя с правильным названием композиции.
    """
    # Получаем ответ от пользователя
    user_answer = event['request']['command'].strip().lower()
    correct_answer = sessionStorage.get('track_name', '').lower()

    if user_answer == correct_answer:
        # Успешный ответ: начисляем баллы
        db = next(get_db())
        session_obj = db.query(Session).filter(Session.session_id == event['session']['session_id']).first()
        session_obj.user_score += 1
        db.commit()

        res['response']['text'] = "Верно! Вы получаете балл."
    else:
        res['response']['text'] = f"Неверно. Правильный ответ: {sessionStorage.get('track_name')}."

    # Предлагаем продолжить игру или закончить сеанс
    res['response']['text'] += "\nНажмите кнопку 'Далее' для следующего трека или 'Завершить' для окончания игры."
    return res


def leave_feedback_handler(res, event, session_id_db):
    """
    Обработчик для получения отзыва от пользователя.
    Пользователь может оставить комментарий по поводу игры.
    """
    # Извлекаем текст отзыва
    feedback_text = event['request']['command']

    # Добавляем отзыв в БД, связывая его с текущей сессией
    db = next(get_db())
    session_obj = db.query(Session).filter(Session.session_id == event['session']['session_id']).first()
    new_feedback = Feedback(session_id=session_obj.id, comment=feedback_text)
    db.add(new_feedback)
    db.commit()

    res['response']['text'] = "Спасибо за отзыв!"
    return res


# Точка входа для запуска Flask-приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

