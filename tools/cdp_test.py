# -*- coding: utf-8 -*-
"""Minimal Chrome DevTools Protocol driver used for UI smoke tests."""

import base64
import json
import os
import sys
import time
import urllib.request

import websocket

BASE = "http://127.0.0.1:9222"


class CDP:
    def __init__(self):
        targets = json.loads(urllib.request.urlopen(BASE + "/json").read().decode("utf-8"))
        page = next(t for t in targets if t.get("type") == "page")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True)
        self.next_id = 1
        self.events = []

    def call(self, method, params=None, timeout=20):
        msg_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        self.ws.settimeout(timeout)
        while True:
            raw = self.ws.recv()
            msg = json.loads(raw)
            if msg.get("id") == msg_id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})
            self.events.append(msg)

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result.get("result", {}).get("value")

    def navigate(self, url, wait=3.0):
        self.call("Page.navigate", {"url": url})
        time.sleep(wait)

    def metrics(self, width=1600, height=1200, mobile=False):
        self.call("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        })

    def screenshot(self, path):
        result = self.call("Page.captureScreenshot", {"format": "png"})
        with open(path, "wb") as handle:
            handle.write(base64.b64decode(result["data"]))
        print("screenshot", path)

    def close(self):
        self.ws.close()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8770/"
    shot = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "tmp", "cdp.png")
    cdp = CDP()
    cdp.call("Runtime.enable")
    cdp.call("Page.enable")
    cdp.metrics(1600, 1200)
    cdp.navigate(url, 3.5)
    print("viewport:", cdp.evaluate("[innerWidth, innerHeight]"))
    print("boot:", cdp.evaluate("document.querySelector('#boot') ? document.querySelector('#boot').className : 'missing'"))
    if cdp.evaluate("!!document.querySelector('#code')"):
        print("code length:", cdp.evaluate("document.querySelector('#code').value.length"))
        print("code head:", repr(cdp.evaluate("document.querySelector('#code').value.slice(0,160)")))
        print("pre text head:", repr(cdp.evaluate("document.querySelector('#highlight').innerText.slice(0,160)")))
        print("gutter head:", repr(cdp.evaluate("document.querySelector('#gutter').innerText.slice(0,30)")))
        print("scroll:", cdp.evaluate("[document.querySelector('#code').scrollTop, document.querySelector('#highlight').scrollTop, document.querySelector('#gutter').scrollTop]"))
    print("errors:", [e.get("method") for e in cdp.events if e.get("method") in ("Runtime.exceptionThrown", "Log.entryAdded")])
    for event in cdp.events:
        if event.get("method") == "Runtime.exceptionThrown":
            print(json.dumps(event["params"], ensure_ascii=False)[:800])
    cdp.screenshot(shot)
    cdp.close()


if __name__ == "__main__":
    main()
