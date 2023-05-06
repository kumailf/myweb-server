from flask import Flask, request, session, jsonify
from flask_cors import CORS, cross_origin
from datetime import timedelta
import openai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "kumailweb"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) 
cors = CORS(app)  # 启用跨域支持

openai.api_key = os.environ.get("OPENAI_API_KEY")
    
@app.route('/api/chat', methods=['POST'])
@cross_origin() 
def chat():
    usermsg = request.form.get('usermsg')
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
    return botmsg

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
