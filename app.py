import logging
from flask import Flask, request, render_template, jsonify
import sqlite3
import os

# ТЕПЕРЬ СОЗДАЕТСЯ ФАЙЛ, ГДЕ ПОКАЗЫВАЮТСЯ СЕСИИ.
# ТАК ЖЕ В ФАЙЛЕ app.log
# ПОСЛЕ ЗАПУСКА ЭТОГО СКРИПТА, БУДЕТ ССЫЛКА ГДЕ ОТКРЫТЬ СТРАНИЦУ БРАУЗЕРА

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

app = Flask(__name__, template_folder='../front/templates', static_folder='../front/static')

def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            about TEXT NOT NULL,
            avatar TEXT
        )''')
        conn.commit()
        conn.close()
        logging.info("База данных успешно инициализирована")

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        about = request.form.get('about')
        avatar = request.form.get('avatar')

        print(f"Login: {login}, Password: {password}, Confirm: {confirm_password}")
        logging.info(f"Попытка регистрации: login={login}, full_name={full_name}, email={email}, phone={phone}, about={about}, avatar={avatar}")

        if password != confirm_password:
            logging.warning(f"Ошибка регистрации: пароли не совпадают для login={login}")
            return "Пароли не совпадают!"

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('''INSERT INTO users (login, password, full_name, email, phone, about, avatar)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (login, password, full_name, email, phone, about, avatar))
            conn.commit()
            conn.close()
            logging.info(f"Пользователь успешно зарегистрирован: login={login}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении пользователя login={login}: {str(e)}")
            return f"Ошибка при сохранении: {str(e)}"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()

    return render_template('index.html', users=users)

@app.route('/api/users', methods=['POST'])
def api_users():
    data = request.form
    login = data.get('login')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')
    about = data.get('about')
    avatar = data.get('avatar')

    logging.info(f"API: Попытка регистрации: login={login}, full_name={full_name}, email={email}, phone={phone}, about={about}, avatar={avatar}")

    if not all([login, password, confirm_password, full_name, email, phone, about]):
        logging.warning(f"API: Ошибка регистрации: не все обязательные поля заполнены для login={login}")
        return jsonify({
            'status': 'error',
            'message': 'Все обязательные поля должны быть заполнены'
        }), 400

    if password != confirm_password:
        logging.warning(f"API: Ошибка регистрации: пароли не совпадают для login={login}")
        return jsonify({
            'status': 'error',
            'message': 'Пароли не совпадают'
        }), 400

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO users (login, password, full_name, email, phone, about, avatar)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (login, password, full_name, email, phone, about, avatar))
        conn.commit()
        conn.close()
        logging.info(f"API: Пользователь успешно зарегистрирован: login={login}")
        return jsonify({
            'status': 'success',
            'message': 'Пользователь успешно зарегистрирован',
            'data': {
                'login': login,
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'about': about,
                'avatar': avatar
            }
        }), 201
    except Exception as e:
        logging.error(f"API: Ошибка при сохранении пользователя login={login}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Ошибка при сохранении: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)