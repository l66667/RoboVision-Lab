#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RoboVision Lab - local learning server (no third-party web framework)."""

import argparse
import base64
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, unquote, urlparse

try:
    import cv2
    import numpy as np
except ImportError:
    print("OpenCV / NumPy 未安装，请先运行 setup.bat。")
    raise


APP_VERSION = "3.0"
APP_NAME = "RoboVision Lab"
ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT, "web")
DATA_DIR = os.path.join(ROOT, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "samples")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
RUNS_DIR = os.path.join(ROOT, "runs")
LESSONS_FILE = os.path.join(DATA_DIR, "lessons.json")
RUNNER_FILE = os.path.join(ROOT, "runner.py")
AI_CONFIG = os.path.join(DATA_DIR, "ai_config.json")
SERVER_INFO = os.path.join(ROOT, ".server.json")
MAX_BODY_BYTES = 12 * 1024 * 1024
MAX_CODE_BYTES = 240 * 1024
RUN_TIMEOUT_SECONDS = 25
RUN_ID_RE = re.compile(r"^[a-f0-9]{32}$")
DEFAULT_PORT = 8770

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


def ensure_directories():
    for path in (SAMPLE_DIR, UPLOAD_DIR, RUNS_DIR):
        if not os.path.isdir(path):
            os.makedirs(path)


def read_json_file(path, fallback=None):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return fallback


def write_json_file(path, payload):
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    os.replace(temporary, path)


def load_lessons():
    data = read_json_file(LESSONS_FILE)
    if not isinstance(data, dict):
        raise ValueError("data/lessons.json 缺失或格式错误。")
    return data


def lesson_index():
    data = load_lessons()
    result = {}
    for chapter in data.get("chapters", []):
        for lesson in chapter.get("lessons", []):
            result[lesson["id"]] = lesson
    return data, result


def load_ai_config():
    payload = read_json_file(AI_CONFIG, {})
    return payload if isinstance(payload, dict) else {}


def safe_join(base, relative_path):
    relative_path = unquote(relative_path).replace("\\", "/")
    candidate = os.path.abspath(os.path.join(base, relative_path))
    base_abs = os.path.abspath(base)
    if candidate != base_abs and not candidate.startswith(base_abs + os.sep):
        return None
    return candidate


def json_bytes(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def read_image_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image_unicode(path, image):
    extension = os.path.splitext(path)[1] or ".png"
    ok, encoded = cv2.imencode(extension, image)
    if not ok:
        raise ValueError("OpenCV 无法编码这张图片。")
    encoded.tofile(path)


def cleanup_old_runs():
    if not os.path.isdir(RUNS_DIR):
        return
    cutoff = time.time() - 3 * 24 * 60 * 60
    for name in os.listdir(RUNS_DIR):
        path = os.path.join(RUNS_DIR, name)
        if not RUN_ID_RE.match(name) or not os.path.isdir(path):
            continue
        try:
            if os.path.getmtime(path) < cutoff:
                shutil.rmtree(path)
        except OSError:
            pass


def public_record(record, include_code=False):
    keys = (
        "ok", "run_id", "lesson_id", "lesson_title", "created_at", "duration_ms",
        "stdout", "stderr", "error", "result_url", "original_url", "width", "height",
        "channels", "outputs", "metrics", "params", "notes", "checks",
    )
    result = {}
    for key in keys:
        if key in record:
            result[key] = record[key]
    if include_code:
        result["code"] = record.get("code", "")
    return result


def port_is_free(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def is_running_app(port):
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:%d/api/health" % port, timeout=0.8
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("app") == APP_NAME
    except Exception:
        return False


def find_existing_app():
    for port in range(DEFAULT_PORT, DEFAULT_PORT + 20):
        if not port_is_free(port) and is_running_app(port):
            return port
    return None


def available_port(preferred):
    for port in range(preferred, preferred + 20):
        if port_is_free(port):
            return port
    return preferred


_LOCAL_IP_CACHE = {"value": "", "at": 0.0}


def local_ip():
    """Best-effort LAN IPv4, preferring Wi-Fi/Ethernet over virtual adapters."""
    now = time.time()
    if _LOCAL_IP_CACHE["value"] and now - _LOCAL_IP_CACHE["at"] < 300:
        return _LOCAL_IP_CACHE["value"]

    candidates = []
    if os.name == "nt":
        command = (
            "$ErrorActionPreference='SilentlyContinue'; "
            "Get-NetIPAddress -AddressFamily IPv4 | "
            "Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } | "
            "Select-Object IPAddress,InterfaceAlias | ConvertTo-Json -Compress"
        )
        try:
            raw = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", command],
                stderr=subprocess.DEVNULL, timeout=6,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            payload = json.loads(raw.decode("utf-8", "replace") or "[]")
            if isinstance(payload, dict):
                payload = [payload]
            for item in payload:
                ip = str(item.get("IPAddress", ""))
                alias = str(item.get("InterfaceAlias", ""))
                low = alias.lower()
                score = 40
                if any(k in low for k in ("wi-fi", "wifi", "wlan", "wireless", "无线")):
                    score = 100
                elif any(k in low for k in ("ethernet", "以太网")):
                    score = 80
                if any(k in low for k in ("vmware", "wsl", "vethernet", "virtual", "vbox",
                                          "hyper-v", "vpn", "vgate", "bluetooth")):
                    score = 0
                if ip.startswith("192.168."):
                    score += 15
                elif ip.startswith("10."):
                    score += 10
                elif ip.startswith("172."):
                    score += 5
                if ip and score > 0:
                    candidates.append((score, ip))
        except Exception:
            pass

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            candidates.append((10, sock.getsockname()[0]))
        finally:
            sock.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidates.append((5, info[4][0]))
    except OSError:
        pass

    candidates = [(score, ip) for score, ip in candidates
                  if ip and not ip.startswith("127.") and not ip.startswith("169.254.")]
    candidates.sort(reverse=True)
    value = candidates[0][1] if candidates else "127.0.0.1"
    _LOCAL_IP_CACHE.update({"value": value, "at": now})
    return value


def browser_candidates():
    candidates = []
    for base in (
        os.environ.get("PROGRAMFILES", r"C:\Program Files"),
        os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),
    ):
        if not base:
            continue
        candidates.extend([
            os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
        ])
    return [path for path in candidates if os.path.isfile(path)]


def open_app_window(url):
    """Prefer a chromeless app window; fall back to the default browser."""
    for executable in browser_candidates():
        try:
            subprocess.Popen([
                executable,
                "--app=" + url,
                "--window-size=1560,1000",
                "--no-first-run",
                "--no-default-browser-check",
            ], close_fds=True)
            return "app"
        except OSError:
            continue
    try:
        webbrowser.open(url)
        return "browser"
    except Exception:
        return "none"


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class LabHandler(BaseHTTPRequestHandler):
    server_version = "RoboVisionLab/3.0"

    def log_message(self, fmt, *args):
        if os.environ.get("ROBO_DEBUG"):
            print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def send_payload(self, status, payload, content_type="application/json; charset=utf-8",
                     extra_headers=None):
        if isinstance(payload, (dict, list)):
            body = json_bytes(payload)
        elif isinstance(payload, str):
            body = payload.encode("utf-8")
        else:
            body = payload
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_payload(status, {"ok": False, "error": message})

    def lan_payload(self):
        host, port = self.server.server_address[0], self.server.server_address[1]
        lan = host == "0.0.0.0"
        ip = local_ip() if lan else ""
        return {
            "ok": True,
            "lan": lan,
            "port": port,
            "local_url": "http://127.0.0.1:%d/" % port,
            "lan_url": "http://%s:%d/" % (ip, port) if lan and ip else "",
            "hint": (
                "平板和电脑连同一个 Wi-Fi，用平板浏览器打开 lan_url。"
                if lan else
                "当前只允许本机访问。关闭本窗口后双击 start_tablet.bat，再在平板打开新地址。"
            ),
            "warning": "局域网内能打开这个地址的人都可以运行 Python 代码；只在可信 Wi-Fi 使用，用完关闭服务。",
        }

    def serve_file(self, path):
        if not path or not os.path.isfile(path):
            self.send_error_json(404, "文件不存在。")
            return
        extension = os.path.splitext(path)[1].lower()
        content_type = CONTENT_TYPES.get(extension, "application/octet-stream")
        try:
            with open(path, "rb") as handle:
                body = handle.read()
        except OSError as exc:
            self.send_error_json(500, "无法读取文件：%s" % exc)
            return
        self.send_payload(200, body, content_type)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if route in ("/", "/index.html"):
            self.serve_file(os.path.join(WEB_DIR, "index.html"))
            return
        if route.startswith("/static/"):
            self.serve_file(safe_join(WEB_DIR, route[len("/static/"):]))
            return
        if route.startswith("/samples/"):
            self.serve_file(safe_join(SAMPLE_DIR, route[len("/samples/"):]))
            return
        if route.startswith("/uploads/"):
            self.serve_file(safe_join(UPLOAD_DIR, route[len("/uploads/"):]))
            return
        if route.startswith("/runs/"):
            self.serve_file(safe_join(RUNS_DIR, route[len("/runs/"):]))
            return
        if route == "/api/health":
            try:
                data, _ = lesson_index()
                lan = self.lan_payload()
                self.send_payload(200, {
                    "ok": True,
                    "app": APP_NAME,
                    "version": APP_VERSION,
                    "cv2": cv2.__version__,
                    "numpy": np.__version__,
                    "python": sys.version.split()[0],
                    "lessons": sum(len(c.get("lessons", [])) for c in data["chapters"]),
                    "lan": lan["lan"],
                    "lan_url": lan["lan_url"],
                })
            except Exception as exc:
                self.send_error_json(500, str(exc))
            return
        if route == "/api/lan":
            try:
                self.send_payload(200, self.lan_payload())
            except Exception as exc:
                self.send_error_json(500, str(exc))
            return
        if route == "/api/lessons":
            try:
                self.send_payload(200, load_lessons())
            except Exception as exc:
                self.send_error_json(500, str(exc))
            return
        if route == "/api/history":
            self.handle_history(query)
            return
        if route.startswith("/api/history/"):
            self.handle_history_item(route[len("/api/history/"):])
            return
        if route.startswith("/api/export/"):
            self.handle_export(route[len("/api/export/"):])
            return
        self.send_error_json(404, "未找到请求的地址。")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/run":
            self.handle_run()
            return
        if parsed.path == "/api/upload":
            self.handle_upload()
            return
        if parsed.path == "/api/ai":
            self.handle_ai()
            return
        if parsed.path == "/api/shutdown":
            self.send_payload(200, {"ok": True, "message": "服务正在关闭。"})
            threading.Timer(0.25, self.server.shutdown).start()
            return
        self.send_error_json(404, "未找到请求的地址。")

    def read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError("请求内容为空或过大。")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except ValueError:
            raise ValueError("请求不是有效的 JSON。")
        if not isinstance(payload, dict):
            raise ValueError("请求内容格式不正确。")
        return payload

    def handle_ai(self):
        try:
            payload = self.read_json_body()
            question = str(payload.get("question", "")).strip()
            if not question:
                raise ValueError("问题不能为空。")
            code = str(payload.get("code", ""))[:7000]
            title = str(payload.get("lesson_title", ""))[:120]
            config = load_ai_config()
            key = config.get("key") or os.environ.get("DASHSCOPE_API_KEY", "")
            if not key:
                raise ValueError("AI 助教还没配置：在 data/ai_config.json 里填入 key。")
            base = config.get("base_url") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            model = config.get("model") or "deepseek-v4-pro"
            system = (
                "你是 RoboVision Lab 的机器人视觉助教，面向中国大二机器人工程学生。"
                "中文回答，先给结论，再解释原因。要紧贴当前课程和代码，"
                "指出具体变量、参数或行号；代码改动只给关键几行。"
                "不要编造 API；不确定时明确说不确定。"
            )
            if title:
                system += "\n当前课程：" + title
            user = question
            if code:
                user += "\n\n当前代码：\n```python\n" + code + "\n```"
            body = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 900,
            }).encode("utf-8")
            request = urllib.request.Request(
                base.rstrip("/") + "/chat/completions",
                data=body,
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            )
            response = urllib.request.urlopen(request, timeout=90)
            data = json.loads(response.read().decode("utf-8", "replace"))
            answer = data["choices"][0]["message"]["content"].strip()
            self.send_payload(200, {"ok": True, "answer": answer})
        except Exception as exc:
            self.send_error_json(400, str(exc))

    def handle_upload(self):
        try:
            payload = self.read_json_body()
            data_url = payload.get("data_url", "")
            match = re.match(
                r"^data:image/(png|jpeg|jpg|webp);base64,(.+)$",
                data_url, re.I | re.S,
            )
            if not match:
                raise ValueError("请选择 PNG、JPG 或 WebP 图片。")
            image_bytes = base64.b64decode(match.group(2))
            if len(image_bytes) > MAX_BODY_BYTES:
                raise ValueError("图片文件过大，请控制在 12 MB 以内。")
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("图片无法解码，请换一张。")
            height, width = image.shape[:2]
            if width < 60 or height < 60:
                raise ValueError("图片太小，请至少使用 60 x 60 的图片。")
            if max(width, height) > 6000:
                raise ValueError("图片太大，长边请控制在 6000 像素以内。")
            upload_id = uuid.uuid4().hex + ".png"
            write_image_unicode(os.path.join(UPLOAD_DIR, upload_id), image)
            self.send_payload(200, {
                "ok": True,
                "upload_id": upload_id,
                "url": "/uploads/" + upload_id,
                "width": width,
                "height": height,
            })
        except Exception as exc:
            self.send_error_json(400, str(exc))

    def resolve_sample(self, requested_sample, lesson):
        if lesson.get("mode") == "text":
            return "", ""
        requested_sample = requested_sample or lesson.get("sample") or ""
        requested_sample = requested_sample.replace("\\", "/").lstrip("/")
        if ".." in requested_sample.split("/"):
            raise ValueError("示例图片路径不合法。")
        if not requested_sample:
            return "", ""
        if re.match(r"^[a-f0-9]{32}\.png$", requested_sample):
            path = os.path.join(UPLOAD_DIR, requested_sample)
            if not os.path.isfile(path):
                raise ValueError("上传的图片已失效，请重新上传。")
            return path, "/uploads/" + requested_sample
        sample_path = safe_join(SAMPLE_DIR, requested_sample)
        if not sample_path or not os.path.isfile(sample_path):
            raise ValueError("示例图片不存在：%s" % requested_sample)
        return sample_path, "/samples/" + requested_sample

    def read_run_record(self, run_id):
        if not RUN_ID_RE.match(run_id or ""):
            return None
        record = read_json_file(os.path.join(RUNS_DIR, run_id, "meta.json"))
        return record if isinstance(record, dict) else None

    def handle_history(self, query):
        try:
            limit = int(query.get("limit", ["10"])[0])
        except (ValueError, TypeError):
            limit = 10
        limit = max(1, min(limit, 50))
        items = []
        if os.path.isdir(RUNS_DIR):
            for name in os.listdir(RUNS_DIR):
                if not RUN_ID_RE.match(name):
                    continue
                path = os.path.join(RUNS_DIR, name, "meta.json")
                if not os.path.isfile(path):
                    continue
                record = read_json_file(path)
                if isinstance(record, dict):
                    items.append((os.path.getmtime(path), record))
        items.sort(key=lambda item: item[0], reverse=True)
        self.send_payload(200, {
            "ok": True,
            "runs": [public_record(record) for _, record in items[:limit]],
        })

    def handle_history_item(self, run_id):
        record = self.read_run_record(run_id)
        if record is None:
            self.send_error_json(404, "运行记录不存在。")
            return
        self.send_payload(200, public_record(record, include_code=True))

    def handle_export(self, run_id):
        record = self.read_run_record(run_id)
        if record is None:
            self.send_error_json(404, "运行记录不存在。")
            return
        run_dir = os.path.join(RUNS_DIR, run_id)
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
            for filename in ("lesson.py", "result.png", "meta.json", "params.json", "checks.json"):
                path = os.path.join(run_dir, filename)
                if os.path.isfile(path):
                    archive.write(path, filename)
            for output in record.get("outputs", []):
                filename = os.path.basename(output.get("url", ""))
                path = os.path.join(run_dir, filename)
                if filename and os.path.isfile(path):
                    archive.write(path, "outputs/" + filename)
            for filename in os.listdir(run_dir):
                if filename.startswith("source."):
                    archive.write(os.path.join(run_dir, filename), filename)
            archive.writestr(
                "README.txt",
                "RoboVision Lab run %s\n\nLesson: %s\nStatus: %s\nDuration: %s ms\n"
                % (run_id, record.get("lesson_title", ""),
                   "success" if record.get("ok") else "failed",
                   record.get("duration_ms", "")),
            )
        body = memory.getvalue()
        self.send_payload(
            200, body, "application/zip",
            {"Content-Disposition": 'attachment; filename="robovision-run-%s.zip"' % run_id[:8]},
        )

    def handle_run(self):
        try:
            payload = self.read_json_body()
            code = payload.get("code", "")
            lesson_id = payload.get("lesson_id", "")
            if not isinstance(code, str) or not code.strip():
                raise ValueError("代码不能为空。")
            if len(code.encode("utf-8")) > MAX_CODE_BYTES:
                raise ValueError("代码太长，请控制在 240 KB 以内。")
            _, lessons = lesson_index()
            lesson = lessons.get(lesson_id)
            if lesson is None:
                raise ValueError("课程不存在。")
            is_scratch = str(payload.get("mode", "")) == "scratch"
            params = payload.get("params", {})
            if not isinstance(params, dict):
                raise ValueError("参数格式不正确。")
            defaults = {}
            for item in lesson.get("params", []):
                if isinstance(item, dict) and "key" in item:
                    defaults[item["key"]] = item.get("value")
            defaults.update(params)
            params = defaults
            params_json = json_bytes(params)
            if len(params_json) > 64 * 1024:
                raise ValueError("参数内容过大。")

            sample_path, sample_url = self.resolve_sample(payload.get("sample_id"), lesson)
            template_path = ""
            if lesson.get("template"):
                template_path = safe_join(SAMPLE_DIR, lesson["template"])
                if not template_path or not os.path.isfile(template_path):
                    raise ValueError("课程模板图片不存在。")

            run_id = uuid.uuid4().hex
            run_dir = os.path.join(RUNS_DIR, run_id)
            os.makedirs(run_dir)
            script_path = os.path.join(run_dir, "lesson.py")
            params_path = os.path.join(run_dir, "params.json")
            checks_path = os.path.join(run_dir, "checks.json")
            output_path = os.path.join(run_dir, "result.png")
            meta_path = os.path.join(run_dir, "meta.json")
            with open(script_path, "w", encoding="utf-8") as handle:
                handle.write(code)
            with open(params_path, "w", encoding="utf-8") as handle:
                handle.write(params_json.decode("utf-8"))
            checks = [] if is_scratch else lesson.get("tests", [])
            if not isinstance(checks, list):
                checks = []
            with open(checks_path, "w", encoding="utf-8") as handle:
                json.dump(checks, handle, ensure_ascii=False)
            if sample_path:
                source_path = os.path.join(
                    run_dir, "source" + os.path.splitext(sample_path)[1].lower()
                )
                shutil.copyfile(sample_path, source_path)

            command = [
                sys.executable, RUNNER_FILE, script_path, sample_path, output_path,
                meta_path, template_path or "", params_path, checks_path,
            ]
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            started = time.monotonic()
            process = subprocess.Popen(
                command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
            )
            timed_out = False
            try:
                stdout, stderr = process.communicate(timeout=RUN_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                stdout, stderr = process.communicate()
            duration_ms = int((time.monotonic() - started) * 1000)

            meta = read_json_file(meta_path, {})
            if not isinstance(meta, dict):
                meta = {}
            stdout_text = stdout.decode("utf-8", "replace").strip()
            stderr_text = stderr.decode("utf-8", "replace").strip()
            if timed_out:
                meta["ok"] = False
                meta["error"] = "运行超过 %d 秒，已停止。检查是否有死循环或摄像头读取。" % RUN_TIMEOUT_SECONDS

            result_url = None
            if os.path.isfile(output_path):
                result_url = "/runs/%s/result.png" % run_id
            outputs = []
            for output in meta.get("outputs", []):
                if not isinstance(output, dict):
                    continue
                filename = os.path.basename(output.get("url", ""))
                if filename and os.path.isfile(os.path.join(run_dir, filename)):
                    item = dict(output)
                    item["url"] = "/runs/%s/%s" % (run_id, filename)
                    outputs.append(item)

            record = dict(meta)
            record.update({
                "run_id": run_id,
                "lesson_id": lesson_id,
                "lesson_title": lesson.get("title", lesson_id) + (" · 我的练习" if is_scratch else ""),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_ms": duration_ms,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "error": meta.get("error", ""),
                "ok": bool(meta.get("ok")),
                "result_url": result_url,
                "original_url": sample_url or None,
                "outputs": outputs,
                "params": meta.get("params", params),
                "checks": meta.get("checks", []),
                "code": code,
            })
            write_json_file(meta_path, record)
            self.send_payload(200, public_record(record))
        except Exception as exc:
            self.send_error_json(400, str(exc))


def main():
    parser = argparse.ArgumentParser(description="RoboVision Lab server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--lan", action="store_true",
                        help="listen on 0.0.0.0 so tablets/phones on the same Wi-Fi can connect")
    args = parser.parse_args()

    ensure_directories()
    cleanup_old_runs()

    existing = find_existing_app()
    if existing and not args.no_browser:
        url = "http://127.0.0.1:%d/" % existing
        print("RoboVision Lab 已在运行：%s" % url)
        open_app_window(url)
        return

    port = available_port(args.port)
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    url = "http://127.0.0.1:%d/" % port
    lan_url = "http://%s:%d/" % (local_ip(), port) if args.lan else ""
    server = ThreadingHTTPServer((host, port), LabHandler)
    write_json_file(SERVER_INFO, {
        "pid": os.getpid(), "port": port, "started": time.time(),
        "lan": args.lan, "lan_url": lan_url,
    })

    print("")
    print("  RoboVision Lab 机器人视觉学习台  v%s" % APP_VERSION)
    print("  Python %s | OpenCV %s | NumPy %s" % (
        sys.version.split()[0], cv2.__version__, np.__version__))
    print("  本机：%s" % url)
    if lan_url:
        print("  平板：%s" % lan_url)
        print("  平板和电脑需连同一个 Wi-Fi；首次可能需要在防火墙允许 Python。")
    print("  关闭这个窗口，或在页面左下角点「退出」，即可停止服务。")
    print("")

    if not args.no_browser:
        threading.Timer(0.6, lambda: open_app_window(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
    finally:
        server.server_close()
        try:
            if os.path.isfile(SERVER_INFO):
                os.remove(SERVER_INFO)
        except OSError:
            pass


if __name__ == "__main__":
    main()
