from flask import Flask, request, session, jsonify, send_file, make_response
from flask_cors import CORS, cross_origin
from datetime import timedelta
import openai
import os
import logging
import subprocess
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = "kumailweb"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
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

@app.route('/api/ytb-download', methods=['POST'])
@cross_origin(supports_credentials=True)
def ytb_download():
    data = request.get_json()
    url = data["video_url"]

    # get video title
    try:
        command = "python -m youtube_dl --get-title {}".format(url)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        title = result.stdout
    except subprocess.CalledProcessError as e:
        app.logger.info("命令执行失败，返回码:", e.returncode)
        app.logger.info("错误输出:", e.stderr)
        return jsonify({'status': "failed", "title":"", "file_name":""})

    if title == "":
        return jsonify({'status': "failed", "title":"", "file_name":""})
    app.logger.info('video_title: %s', title)
    app.logger.info('video_url: %s', url)

    # get video
    try:
        command = "python -m youtube_dl -f 'bestvideo[height<=1080]+bestaudio/best' -o - {}".format(url)
        result = subprocess.run(command, shell=True, capture_output=True)
        video_stream = result.stdout
        headers = {'Content-Type': 'video/mp4'}

    except subprocess.CalledProcessError as e:
        app.logger.info("命令执行失败，返回码:", e.returncode)
        app.logger.info("错误输出:", e.stderr)
        return jsonify({'status': "failed", "title":""})

    response = make_response(video_stream)
    response.headers.set('Content-Disposition', 'attachment', filename='video.mp4')
    response.headers.set('Content-Type', 'video/mp4')
    return response
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)

## https://www.youtube.com/watch?v=SYjanMT-bpY
