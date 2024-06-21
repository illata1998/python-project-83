import os
from flask import Flask, render_template, request, flash, get_flashed_messages, url_for, redirect
from dotenv import load_dotenv
import psycopg2
import validators
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    return psycopg2.connect(DATABASE_URL)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def add_url():
    url = request.form.get('url', '', type=str)
    created_at = datetime.now().date()
    if not (validators.url(url) and len(url) <= 255):
        flash('Некорекктный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            messages=messages,
            url=url
        ), 422
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM public.urls WHERE urls.name = '{url}';")
    record = cursor.fetchone()
    if not record:
        flash('Страница успешно добавлена', 'success')
        cursor.execute(f"INSERT INTO public.urls (name, created_at) VALUES ('{url}', '{created_at}');")
        conn.commit()
        cursor.execute(f"SELECT id FROM public.urls WHERE urls.name = '{url}';")
        url_id = cursor.fetchone()[0]
        conn.close()
    else:
        flash('Страница уже существует', 'info')
        url_id = record[0]
    return redirect(url_for('show_url', url_id=url_id), code=302)


@app.get('/urls')
def show_all_urls():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM public.urls ORDER BY urls.id DESC;")
    records = cursor.fetchall()
    urls = []
    for record in records:
        urls.append(
            {
                'id': record[0],
                'name': record[1],
                'created_at': record[2]
            }
        )
    return render_template(
        'show_all_urls.html',
        urls=urls
    )


@app.route('/urls/<url_id>')
def show_url(url_id):
    conn = connect()
    cursor = conn.cursor()
    messages = get_flashed_messages(with_categories=True)
    cursor.execute(f"SELECT * FROM urls WHERE id = {url_id};")
    record = cursor.fetchone()
    url = {
        'id': record[0],
        'name': record[1],
    }
    conn.close()
    return render_template('show_url.html', messages=messages, url=url)
