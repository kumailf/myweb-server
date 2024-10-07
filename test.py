
from datetime import timedelta
import os
import logging
import subprocess
import uuid
import random
import re 



participant_list = []


weibo_link = "https://weibo.com/2802216802/4975926672886885"
# get weibo_id
pattern = r"/([^/]+)$"
# 使用正则表达式进行匹配
match = re.search(pattern, weibo_link)

# 检查是否找到匹配
if match:
    # 提取匹配的部分
    weibo_id = match.group(1)
print(weibo_id)
# else: 
#     app.logger.info("链接错误")
#     return jsonify({'winner': "链接错误（大概），无法使用请微博私信我"})
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

# lottery_type = data.get('selectedLotteryType', '')
# winning_count = data.get('winningCount', 1)  # 默认中奖人数为1
lottery_type = "repost"
# # get participant_list
command = ['python', '/root/code/WeiboSpider/weibospider/run_spider.py', lottery_type, weibo_id]

# 使用subprocess.Popen
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# 获取标准输出和标准错误的输出结果
output_text, error_text = process.communicate()

# 读取最新文件内容
folder_path = '/root/code/output'
latest_file = get_latest_file(folder_path)
if latest_file:
    with open(latest_file, 'r') as file:
        log_content = file.read()
        print("最新文件内容：", log_content)
else:
    print("文件夹中没有文件。")

pattern = re.compile(r'"nick_name":\s*"([^"]+)"')
participant_list = pattern.findall(log_content)
participant_list = list(set(participant_list))
print(participant_list)