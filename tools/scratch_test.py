# -*- coding: utf-8 -*-
import json
import urllib.request

base = "http://127.0.0.1:8770"
code = 'print("my scratch")\nprint("image", image.shape)\nresult = image.copy()\n'
body = json.dumps({
    "code": code,
    "lesson_id": "robot-line",
    "params": {},
    "mode": "scratch",
}).encode()
request = urllib.request.Request(base + "/api/run", data=body, headers={"Content-Type": "application/json"})
result = json.load(urllib.request.urlopen(request, timeout=40))
print("ok", result["ok"], "checks", len(result["checks"]), "images", len(result["outputs"]))
print("title", result["lesson_title"])
print("stdout", result["stdout"].replace("\n", " | "))
