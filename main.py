from flask import Flask, request, session, jsonify, send_file, make_response
from flask_cors import CORS, cross_origin
from datetime import timedelta
import openai
import os
import logging
import subprocess
import uuid
import random
import re 

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
    
@app.route('/api/draw', methods=['POST'])
@cross_origin(supports_credentials=True)
def draw():
    participant_list = []

    data = request.get_json()
    weibo_link = data.get('weiboLink', '')
    # get weibo_id
    pattern = r"/([^/]+)$"
    # 使用正则表达式进行匹配
    match = re.search(pattern, weibo_link)

    # 检查是否找到匹配
    if match:
        # 提取匹配的部分
        weibo_id = match.group(1)
    else: 
        app.logger.info("未找到匹配")
        return jsonify({'winner': "链接错误（大概），无法使用请微博私信我"})


    lottery_type = data.get('selectedLotteryType', '')
    winning_count = data.get('winningCount', 1)  # 默认中奖人数为1

    # get participant_list
    get_list = subprocess.run(['python', '/root/code/WeiboSpider/weibospider/run_spider.py', lottery_type, weibo_id], capture_output=True, text=True)
    log_content = get_list.stdout

    # 使用正则表达式匹配 nick_name 字段对应的值
    pattern = re.compile(r'"nick_name":\s*"([^"]+)"')
    participant_list = pattern.findall(log_content)
    participant_list = list(set(participant_list))
    app.logger.info("参与名单： %s", participant_list)
    if participant_list == [] or not participant_list:
        return jsonify({'winner': "链接错误（大概），无法使用请微博私信我"})

    winners = random.sample(participant_list, min(winning_count, len(participant_list)))
    winner = ', '.join(winners)
    if winner == "":
        return jsonify({'winner': "链接错误（大概），无法使用请微博私信我"})
    app.logger.info("中奖者：%s", winner)
    return jsonify({'winner': winner})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)

