from flask import Flask, request, session, jsonify
from flask_cors import CORS, cross_origin
from datetime import timedelta
import openai
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = "kumailweb"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
logging.basicConfig(level=logging.DEBUG)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/api/chat', methods=['POST'])
@cross_origin(supports_credentials=True)
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
    app.logger.info('usermsg: %s', usermsg)
    app.logger.info('botmsg: %s', botmsg)
    session['messages'].append({'role': 'assistant', 'content': botmsg})
    session.modified = True
    
    return jsonify({'chat': botmsg})

@app.route('/api/gene-image', methods=['POST'])
@cross_origin(supports_credentials=True)
def gene_image():
    data = request.get_json()
    image_prompt = data["image_prompt"]
    response = openai.Image.create(
        prompt = image_prompt,
        n = 1,
        size = "512x512"
    )
    image_url = response['data'][0]['url']
    app.logger.info('image_prompt: %s', image_prompt)
    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)