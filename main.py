from flask import Flask, request, session, jsonify
from flask_cors import CORS, cross_origin
from datetime import timedelta
import openai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "kumailweb"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/chat', methods=['POST'])
@cross_origin()
def chat():
    data = request.get_json()
    usermsg = data["usermsg"]
    if 'messages' not in session:
        session['messages'] = []

    session.get("messages").append({'role': 'user', 'content': usermsg})
    session.modified = True
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=2048,
        messages=session['messages'],
        temperature=0.7
    )
    botmsg = response.choices[0].message.content

    session['messages'].append({'role': 'assistant', 'content': botmsg})
    session.modified = True
    return jsonify({'chat': botmsg})

@app.route('/api/gene/image', methods=['POST'])
@cross_origin()
def gene_image():
    data = request.get_json()
    image_prompt = data["image_prompt"]
    response = openai.Image.create(
        prompt = image_prompt,
        n = 1,
        size = "1024x1024"
    )
    image_url = response['data'][0]['url']
    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)