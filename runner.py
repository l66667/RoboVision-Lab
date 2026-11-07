#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run one lesson script.

The lesson can be text-only (Python basics) or image-based (OpenCV).
Every run writes a meta.json next to the generated images.  The server
reads that file, so the runner never needs to know about HTTP.
"""

import json
import os
import sys
import traceback

import cv2
import numpy as np

MAX_OUTPUTS = 12
MAX_OUTPUT_SIDE = 4096


def read_image(path):
    """Read an image through np.fromfile so Chinese paths keep working."""
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path, image):
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("结果无法编码为 PNG。")
    encoded.tofile(path)


def normalize_image(image):
    if not isinstance(image, np.ndarray):
        raise TypeError(
            "result 必须是 NumPy 图像数组，例如 cv2.cvtColor 的返回值。"
        )
    if image.size == 0:
        raise ValueError("result 是空图像。")
    if image.dtype == np.bool_:
        image = image.astype(np.uint8) * 255
    elif image.dtype in (np.float32, np.float64):
        if image.size and image.max() <= 1.0 and image.min() >= 0.0:
            image = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        else:
            image = np.clip(image, 0, 255).astype(np.uint8)
    elif image.dtype not in (np.uint8, np.uint16):
        image = cv2.convertScaleAbs(image)
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.ndim == 3 and image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("结果必须是灰度图、BGR 图或 BGRA 图。")
    if max(image.shape[:2]) > MAX_OUTPUT_SIDE:
        scale = float(MAX_OUTPUT_SIDE) / max(image.shape[:2])
        image = cv2.resize(
            image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
        )
    return np.ascontiguousarray(image)


def read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload
    except Exception:
        return fallback


def media_size(image):
    return {
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "channels": int(image.shape[2]) if image.ndim == 3 else 1,
    }


def json_safe(value, depth=0):
    """Keep only JSON-friendly values so one metric cannot break the run."""
    if depth > 4:
        return str(value)[:300]
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and (
            value != value or value in (float("inf"), float("-inf"))
        ):
            return str(value)
        return value
    if isinstance(value, np.generic):
        return json_safe(value.item(), depth + 1)
    if isinstance(value, dict):
        result = {}
        for key, item in list(value.items())[:50]:
            result[str(key)[:80]] = json_safe(item, depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [json_safe(item, depth + 1) for item in list(value)[:50]]
    if isinstance(value, np.ndarray):
        return "ndarray%s" % (value.shape,)
    return str(value)[:300]


def main():
    if len(sys.argv) < 7:
        print("usage: runner.py script sample output meta template params [checks]")
        return 2
    (script_path, sample_path, output_path, meta_path,
     template_path, params_path) = sys.argv[1:7]
    checks_path = sys.argv[7] if len(sys.argv) > 7 else ""

    meta = {
        "ok": False,
        "error": "",
        "outputs": [],
        "metrics": {},
        "notes": [],
        "checks": [],
    }
    params = read_json(params_path, {})
    if not isinstance(params, dict):
        params = {}
    metrics = {}

    image = None
    if sample_path:
        image = read_image(sample_path)
        if image is None:
            meta["error"] = "无法读取示例图片。"
            write_meta(meta_path, meta)
            print(meta["error"], file=sys.stderr)
            return 1

    template = None
    if template_path:
        template = read_image(template_path)
        if template is None:
            meta["error"] = "无法读取课程模板图片。"
            write_meta(meta_path, meta)
            print(meta["error"], file=sys.stderr)
            return 1

    captures = []

    def capture(name, frame):
        """Register an intermediate image; the UI shows them in order."""
        if len(captures) >= MAX_OUTPUTS:
            raise ValueError("capture() 最多保存 %d 张图。" % MAX_OUTPUTS)
        if frame is None:
            raise ValueError("capture('%s', None) 拿到了一张空图。" % name)
        captures.append((str(name)[:80], frame))
        return frame

    def record_metric(key, value):
        metrics[str(key)[:80]] = value
        return value

    def headless_imshow(name, frame):
        capture(name, frame)

    # Tutorial code can call cv2.imshow/waitKey without opening a window.
    cv2.imshow = headless_imshow
    cv2.namedWindow = lambda *args, **kwargs: None
    cv2.waitKey = lambda *args, **kwargs: 0
    cv2.destroyWindow = lambda *args, **kwargs: None
    cv2.destroyAllWindows = lambda *args, **kwargs: None

    run_dir = os.path.dirname(os.path.abspath(output_path))
    scope = {
        "__name__": "__main__",
        "__file__": script_path,
        "cv2": cv2,
        "np": np,
        "numpy": np,
        "image": image,
        "src": image,
        "template": template,
        "sample_path": sample_path,
        "sample_dir": os.path.dirname(sample_path) if sample_path else "",
        "template_path": template_path,
        "work_dir": run_dir,
        "read_image": read_image,
        "params": params,
        "p": params,
        "capture": capture,
        "metric": record_metric,
        "metrics": metrics,
    }

    code_ok = True
    try:
        with open(script_path, "r", encoding="utf-8") as handle:
            code = handle.read()
        exec(compile(code, "<lesson>", "exec"), scope, scope)
    except BaseException:
        code_ok = False
        meta["error"] = traceback.format_exc()

    # Run the lesson's automatic checks even when the script failed: every
    # check then shows as failed, which is clearer than an empty list.
    checks = read_json(checks_path, [])
    if not isinstance(checks, list):
        checks = []
    for item in checks:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "检查"))[:80]
        expr = str(item.get("expr", "False"))
        record = {"name": name, "passed": False, "detail": ""}
        if not code_ok:
            record["detail"] = "代码没有成功运行"
        else:
            try:
                value = eval(compile(expr, "<check>", "eval"), scope, scope)
                record["passed"] = bool(value)
                record["detail"] = "通过" if record["passed"] else "未通过（表达式结果：%s）" % repr(value)[:120]
            except Exception as exc:
                record["detail"] = "%s: %s" % (type(exc).__name__, exc)
        meta["checks"].append(record)

    if code_ok:
        candidates = []
        result = scope.get("result")
        if isinstance(result, np.ndarray):
            candidates.append(("最终结果", result))
        candidates.extend(captures)
        explicit = scope.get("outputs")
        if isinstance(explicit, dict):
            for name, frame in list(explicit.items())[:MAX_OUTPUTS]:
                if isinstance(frame, np.ndarray):
                    candidates.append((str(name), frame))
        # A vision lesson that only prints still shows its input image.
        if not candidates and image is not None:
            candidates.append(("输入图像", image))

        saved = []
        primary = None
        try:
            for index, (title, frame) in enumerate(candidates[:MAX_OUTPUTS]):
                normalized = normalize_image(frame)
                if primary is None:
                    primary = normalized
                filename = "output_%02d.png" % (index + 1)
                write_image(os.path.join(run_dir, filename), normalized)
                item_meta = {
                    "name": title,
                    "url": "output_%02d.png" % (index + 1),
                }
                item_meta.update(media_size(normalized))
                saved.append(item_meta)
            if primary is not None:
                write_image(output_path, primary)
                meta.update(media_size(primary))
            meta.update({
                "ok": True,
                "outputs": saved,
                "metrics": json_safe(metrics),
                "params": json_safe(params),
            })
        except BaseException:
            meta["ok"] = False
            meta["error"] = traceback.format_exc()
    else:
        meta["ok"] = False
        meta["metrics"] = json_safe(metrics)

    write_meta(meta_path, meta)
    if not meta.get("ok"):
        print(meta.get("error", "运行失败。"), file=sys.stderr)
        return 1
    return 0


def write_meta(path, meta):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
