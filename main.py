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
import time
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "kumailweb"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
logging.basicConfig(level=logging.DEBUG)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_latest_file(folder_path):
    # 获取指定文件夹中的所有文件
    files = os.listdir(folder_path)
    # 过滤出文件路径
    files = [os.path.join(folder_path, file) for file in files if os.path.isfile(os.path.join(folder_path, file))]
    if not files:
        return None
    # 获取最新的文件
    latest_file = max(files, key=os.path.getctime)
    return latest_file

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
        app.logger.info("链接错误")
        return jsonify({'winner': "链接错误（大概），无法使用请微博私信蓝_ouo"})


    lottery_type = data.get('selectedLotteryType', '')
    winning_count = data.get('winningCount', 1)  # 默认中奖人数为1

    cookie = "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF5kCr1Aeky.Odvw6PH1uew5JpX5K-hUgL.FozRehzEeKqRehz2dJLoI7XLxKnL1KeL1-xkdNHa; ALF=1736167900; SCF=AmN5AQfUvWMpsW3PwlNyA-EIi7hrBwhPoAa97gKWWepHzlBKM6VPIWjmovO8-OZQ7aum9XBgoFYW8rRxZhVsJzI.; SUB=_2A25KUDSMDeRhGeRG61AT8SjEyz6IHXVpLMhErDV6PUJbktAbLWXDkW1NUkeyJk3q7ZC1QTqHwkzOBNtSMSORA8bf; _T_WM=046b0ea0d7d424367c6e39e5239ba23a; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=oid%3D5109640930794331%26lfid%3D5109640930794331%26luicode%3D20000174%26uicode%3D20000174; XSRF-TOKEN=561f8f"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    headers = {"User_Agent": user_agent, "Cookie": cookie}
    max_page = 10
    for p in range(1, max_page):
        req = requests.get(
            url= f"https://m.weibo.cn/api/statuses/repostTimeline?id={weibo_id}&page={p}",
            headers=headers
        )
        if req.json().get("ok") == 1:
            data = req.json().get("data").get("data")
            number = len(data)
            for i in range(number):
                participant_list.append(data[i].get("user").get("screen_name"))
        else:
            break

    if participant_list == []:
        winner = "没人转发"
    else:
        winners = random.sample(participant_list, min(winning_count, len(participant_list)))
        winner = ', '.join(winners)
        if winner == "":
            return jsonify({'winner': "bug了"})
        app.logger.info("中奖者：%s", winner)

    return jsonify({'winner': winner})

@app.route('/api/recommend', methods=['POST'])
@cross_origin(supports_credentials=True)
def recommend():
    data = request.get_json()
    song_title = data.get('song_title', '')
    song_artist = data.get('song_artist', '')
    your_name = data.get('your_name', '')

    app.logger.info("歌名：%s， 演唱者：%s，推荐人： %s ", song_title, song_artist, your_name)

    response = {
        'message': '推荐成功',
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)

