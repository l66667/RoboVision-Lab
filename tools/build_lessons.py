# -*- coding: utf-8 -*-
"""Assemble content/ch*.py into data/lessons.json."""

import argparse
import importlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "data", "lessons.json")
MODULES = [
    "ch1_python",
    "ch2_opencv",
    "ch3_robot",
    "ch4_engineer",
    "ch5_capstone",
    "ch6_ros2_basics",
    "ch7_ros2_advanced",
    "ch8_ros2_engineering",
    "ch9_ros2_vision",
    "ch10_project",
]

sys.path.insert(0, CONTENT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="all chapters must exist")
    args = parser.parse_args()

    chapters = []
    missing = []
    for name in MODULES:
        try:
            module = importlib.import_module(name)
            chapters.append(module.CHAPTER)
        except ImportError as exc:
            missing.append("%s (%s)" % (name, exc))
        except Exception as exc:
            raise SystemExit("构建 %s 失败：%s" % (name, exc))

    if missing and args.strict:
        raise SystemExit("缺少章节：" + ", ".join(missing))

    ids = set()
    total = 0
    for ch in chapters:
        for item in ch["lessons"]:
            if item["id"] in ids:
                raise SystemExit("课程 id 重复：%s" % item["id"])
            ids.add(item["id"])
            total += 1
            if len(item.get("objectives", [])) < 3:
                raise SystemExit("%s 的目标少于 3 条" % item["id"])
            if len(item.get("walkthrough", [])) < 3:
                raise SystemExit("%s 的代码段少于 3 段" % item["id"])
            if not item.get("tests"):
                raise SystemExit("%s 没有自动检查" % item["id"])
            for segment in item["walkthrough"]:
                if not segment["code"]:
                    raise SystemExit("%s 有空代码段" % item["id"])
                if not segment["explain"]:
                    raise SystemExit("%s 的「%s」没有解释" % (item["id"], segment["title"]))
                if segment["code"] not in item["starter"]:
                    raise SystemExit(
                        "%s 的代码段「%s」没有出现在 starter 里" % (item["id"], segment["title"])
                    )

    payload = {
        "title": "RoboVision Lab",
        "subtitle": "从 Python 零基础到机器人视觉实战",
        "version": "3.0",
        "chapters": chapters,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    size = os.path.getsize(OUT)
    print("已生成 %s" % OUT)
    print("章节 %d 个，课程 %d 节，%.1f KB" % (len(chapters), total, size / 1024.0))
    if missing:
        print("未加载：" + ", ".join(missing))


if __name__ == "__main__":
    main()
