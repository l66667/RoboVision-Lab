# -*- coding: utf-8 -*-
import json
import urllib.request

base = "http://127.0.0.1:8770"
lessons = json.load(urllib.request.urlopen(base + "/api/lessons"))
index = {l["id"]: l for c in lessons["chapters"] for l in c["lessons"]}
lesson = index["robot-line"]
code = lesson["starter"]
params = {p["key"]: p["value"] for p in lesson.get("params", [])}
body = json.dumps({"code": code, "lesson_id": lesson["id"], "params": params}).encode()
req = urllib.request.Request(base + "/api/run", data=body, headers={"Content-Type": "application/json"})
result = json.load(urllib.request.urlopen(req, timeout=40))
for check in result["checks"]:
    print(check["passed"], check["name"], "|", check["detail"])
