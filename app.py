from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import openai
from bson.objectid import ObjectId
import re
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('API_KEY')

uri = os.getenv('uriMongoDB')

client = MongoClient(uri)
db = client['educontabil']
posts_collection = db['posts']
imperatriz_collection = db['imperatriz']
carrossel_collection = db['carrossel']

def add_blog_post(cover, title, description, content):
    posts_collection.insert_one({
        'cover': cover,
        'title': title,
        'description': description,
        'content': content
    })

def get_blog_posts():
    return list(posts_collection.find())

def get_blog_post_by_id(post_id):
    return posts_collection.find_one({'_id': ObjectId(post_id)})

def get_imperatriz_posts():
    return list(imperatriz_collection.find())

def get_imperatriz_post_by_id(post_id):
    return imperatriz_collection.find_one({'_id': ObjectId(post_id)})

def get_carousel_images():
    return list(carrossel_collection.find())

def format_post_content(content):
    lines = content.split('\n')
    formatted_lines = []

    for line in lines:
        if line.startswith('###'):
            formatted_lines.append(f"<h3>{line[3:].strip()}</h3>")
        elif line.startswith('##'):
            formatted_lines.append(f"<h2>{line[2:].strip()}</h2>")
        elif line.startswith('#'):
            formatted_lines.append(f"<h1>{line[1:].strip()}</h1>")
        else:
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if image_match:
                alt_text, image_url = image_match.groups()
                formatted_lines.append(f'<img src="{image_url}" alt="{alt_text}" class="img-fluid">')
            else:
                bold_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                formatted_lines.append(f"<p>{bold_line.strip()}</p>")
    
    return '\n'.join(formatted_lines)

@app.route('/')
def home():
    posts = get_blog_posts()
    imperatriz_posts = get_imperatriz_posts()
    carousel_images = get_carousel_images()
    return render_template('index.html', posts=posts, imperatriz_posts=imperatriz_posts, carousel_images=carousel_images)

@app.route('/post/<post_id>')
def post_detail(post_id):
    post = get_blog_post_by_id(post_id)
    if post:
        post['formatted_content'] = format_post_content(post['content'])
    return render_template('post_detail.html', post=post)

@app.route('/imperatriz_post/<post_id>')
def imperatriz_post_detail(post_id):
    post = get_imperatriz_post_by_id(post_id)
    if post:
        post['formatted_content'] = format_post_content(post['content'])
    return render_template('imperatriz_post_detail.html', post=post)

@app.route('/post_list')
def post_list():
    posts = get_blog_posts()
    return render_template('post_list.html', posts=posts)

@app.route('/financial_education')
def financial_education():
    return render_template('financial_education.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.json.get('message')
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Você é um assistente contábil e responde a perguntas relacionadas à contabilidade. Se a pergunta não for sobre contabilidade, peça para reformular considerando a aplicação contábil. As perguntas podem ser sobre finanças, abertura de empresas, formalização de negócios, legislação, tributos, etc. Resuma as respostas e, se necessário, forneça um passo a passo. Use linguagem informal e cotidiana. A primeira pergunta já será feita a seguir.\nUsuário: {message}\nAssistente:",
        max_tokens=100,
        temperature=0.7,
    )

    response_text = response.choices[0].text.strip()
    
    return jsonify({'message': response_text})

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        cover = request.form['cover']
        title = request.form['title']
        description = request.form['description']
        content = request.form['content']
        add_blog_post(cover, title, description, content)
        return redirect(url_for('home'))
    return render_template('add_post.html')

if __name__ == '__main__':
    app.run(debug=False)