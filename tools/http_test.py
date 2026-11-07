# -*- coding: utf-8 -*-
"""Smoke-test the HTTP layer: lessons, run, outputs, history, export."""

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8770"


def post(path, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as response:
        return response.read()


def main():
    lessons = json.loads(get("/api/lessons").decode("utf-8"))
    index = {}
    for chapter in lessons["chapters"]:
        for lesson in chapter["lessons"]:
            index[lesson["id"]] = lesson

    for lesson_id in ("py-first-run", "robot-line", "capstone-cell"):
        lesson = index[lesson_id]
        payload = {"code": lesson["starter"], "lesson_id": lesson_id, "params": {}}
        for item in lesson.get("params", []):
            payload["params"][item["key"]] = item["value"]
        result = post("/api/run", payload)
        print(lesson_id, "ok=", result.get("ok"), "checks=",
              sum(1 for c in result.get("checks", []) if c.get("passed")),
              "/", len(result.get("checks", [])),
              "images=", len(result.get("outputs", [])),
              "metrics=", len(result.get("metrics", {})))
        if not result.get("ok"):
            print(result.get("error", "")[-600:])
        if result.get("outputs"):
            url = result["outputs"][0]["url"]
            blob = get(url)
            print("  first image", url, len(blob), "bytes")
        if result.get("run_id"):
            zipped = get("/api/export/" + result["run_id"])
            print("  zip", len(zipped), "bytes")

    history = json.loads(get("/api/history?limit=5").decode("utf-8"))
    print("history", len(history.get("runs", [])))


if __name__ == "__main__":
    main()
