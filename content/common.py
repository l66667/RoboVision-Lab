# -*- coding: utf-8 -*-
"""Small helpers that keep the lesson content readable in Python source."""


def P(x):
    return {"t": "p", "x": x}


def H(x):
    return {"t": "h", "x": x}


def UL(*items):
    return {"t": "ul", "x": list(items)}


def OL(*items):
    return {"t": "ol", "x": list(items)}


def NOTE(title, x, tone="info"):
    return {"t": "note", "x": x, "title": title, "tone": tone}


def CODE(x, lang="text"):
    return {"t": "code", "x": x, "lang": lang}


def FORMULA(x, label=""):
    return {"t": "formula", "x": x, "label": label}


def TABLE(head, rows):
    return {"t": "table", "head": head, "rows": rows}


def seg(title, code, explain, tip="", lang="python"):
    return {
        "title": title,
        "code": code.strip("\n"),
        "explain": explain.strip(),
        "tip": tip.strip(),
        "lang": lang,
    }


def param(key, label, value, low, high, step, unit="", hint=""):
    return {
        "key": key, "label": label, "value": value,
        "min": low, "max": high, "step": step,
        "unit": unit, "hint": hint,
    }


def test(name, expr):
    return {"name": name, "expr": expr}


def task(kind, title, detail):
    return {"kind": kind, "title": title, "detail": detail}


def quiz(q, options, answer, why):
    return {"q": q, "options": options, "answer": answer, "why": why}


def target(metric, op, value, label):
    return {"metric": metric, "op": op, "value": value, "label": label}


def lesson(
    id, title, subtitle, *, chapter, mode="text", sample=None, template=None,
    difficulty=1, minutes=20, tags=(), objectives=(), concept=(),
    walkthrough=(), tests=(), params=(), tasks=(), quiz_items=(),
    industry="", career="", target_spec=None, next_step="",
):
    for i, item in enumerate(walkthrough):
        item.setdefault("index", i + 1)
    header = [
        "# " + "=" * 66,
        "#  " + title + "  ·  " + subtitle,
        "#  运行：Ctrl + Enter 或点右上角「运行」",
    ]
    if mode == "vision":
        header.append("#  可用：image（BGR 输入图）、capture(名称, 图)、metric(名称, 值)")
    else:
        header.append("#  这一课只用 Python 标准库，输出显示在「控制台」。")
    header.append("# " + "=" * 66)
    starter = "\n".join(header) + "\n\n" + "\n\n".join(
        item["code"] for item in walkthrough
    ) + "\n"

    return {
        "id": id,
        "chapter": chapter,
        "title": title,
        "subtitle": subtitle,
        "mode": mode,
        "sample": sample,
        "template": template,
        "difficulty": difficulty,
        "minutes": minutes,
        "tags": list(tags),
        "objectives": list(objectives),
        "concept": list(concept),
        "walkthrough": list(walkthrough),
        "starter": starter,
        "tests": list(tests),
        "params": list(params),
        "tasks": list(tasks),
        "quiz": list(quiz_items),
        "industry": industry,
        "career": career,
        "target": target_spec,
        "nextStep": next_step,
    }


def chapter(id, number, title, subtitle, lessons, color="#7dd3fc", icon="01"):
    return {
        "id": id,
        "number": number,
        "title": title,
        "subtitle": subtitle,
        "color": color,
        "icon": icon,
        "lessons": list(lessons),
    }
