import subprocess



url = "https://www.youtube.com/watch?v=fdFlXmqpiRc"

# get video title
try:
    command = "python -m youtube_dl --get-title {}".format(url)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    title = result.stdout
except subprocess.CalledProcessError as e:
    print("命令执行失败，返回码:", e.returncode)
    print("错误输出:", e.stderr)


if title == "":
    print("err")

# get video
try:
    command = "python -m youtube_dl -o ~/code/kumailf-server/test.mp4 {}".format(title, url)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    res = result.stdout
    print(res)
except subprocess.CalledProcessError as e:
    print("命令执行失败，返回码:", e.returncode)
    print("错误输出:", e.stderr)

print(title)