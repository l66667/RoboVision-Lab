# -*- coding: utf-8 -*-
"""Ask the local server to shut down; used by 停止学习软件.bat."""
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFO = os.path.join(ROOT, ".server.json")

if not os.path.isfile(INFO):
    print("没有找到运行记录，服务可能已经停止。")
    raise SystemExit(0)

with open(INFO, "r", encoding="utf-8") as handle:
    info = json.load(handle)

url = "http://127.0.0.1:%s/api/shutdown" % info.get("port", 8770)
try:
    request = urllib.request.Request(url, data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json"})
    urllib.request.urlopen(request, timeout=5).read()
    print("已发送关闭指令。")
except Exception as exc:
    print("关闭失败（服务可能已停止）：%s" % exc)
