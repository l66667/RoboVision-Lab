# -*- coding: utf-8 -*-
"""Run every lesson starter through runner.py and report pass/fail."""

import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RUNS = os.path.join(ROOT, "runs", "_selftest")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="comma separated lesson ids")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    only = set(filter(None, [x.strip() for x in args.only.split(",")]))

    with open(os.path.join(DATA, "lessons.json"), encoding="utf-8") as handle:
        data = json.load(handle)

    if os.path.isdir(RUNS) and not args.keep:
        shutil.rmtree(RUNS)
    os.makedirs(RUNS, exist_ok=True)

    total = 0
    passed = 0
    failures = []
    for chapter in data["chapters"]:
        for lesson in chapter["lessons"]:
            if only and lesson["id"] not in only:
                continue
            total += 1
            run_dir = os.path.join(RUNS, lesson["id"])
            os.makedirs(run_dir, exist_ok=True)
            script = os.path.join(run_dir, "lesson.py")
            meta_path = os.path.join(run_dir, "meta.json")
            params_path = os.path.join(run_dir, "params.json")
            checks_path = os.path.join(run_dir, "checks.json")
            output_path = os.path.join(run_dir, "result.png")
            with open(script, "w", encoding="utf-8") as handle:
                handle.write(lesson["starter"])
            with open(checks_path, "w", encoding="utf-8") as handle:
                json.dump(lesson.get("tests", []), handle, ensure_ascii=False)
            params = {}
            for item in lesson.get("params", []):
                params[item["key"]] = item["value"]
            with open(params_path, "w", encoding="utf-8") as handle:
                json.dump(params, handle, ensure_ascii=False)

            sample = ""
            if lesson.get("mode") != "text" and lesson.get("sample"):
                sample = os.path.join(DATA, "samples", lesson["sample"])
            template = ""
            if lesson.get("template"):
                template = os.path.join(DATA, "samples", lesson["template"])

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            process = subprocess.run(
                [
                    sys.executable, os.path.join(ROOT, "runner.py"), script,
                    sample, output_path, meta_path, template, params_path, checks_path,
                ],
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, timeout=60,
            )
            meta = {}
            if os.path.isfile(meta_path):
                with open(meta_path, encoding="utf-8") as handle:
                    meta = json.load(handle)
            checks = meta.get("checks", [])
            ok = bool(meta.get("ok"))
            checks_ok = all(item.get("passed") for item in checks)
            status = "OK  " if ok and checks_ok else "FAIL"
            if ok and checks_ok:
                passed += 1
            else:
                failures.append(lesson["id"])
            print("%s %-20s %5sms  images=%d  checks=%d/%d" % (
                status, lesson["id"], meta.get("duration_ms", "-"),
                len(meta.get("outputs", [])),
                sum(1 for c in checks if c.get("passed")), len(checks),
            ))
            if not ok:
                err = (meta.get("error") or process.stderr.decode("utf-8", "replace"))
                print("     ERROR:", err.strip().splitlines()[-1][:220] if err.strip() else "unknown")
            for check in checks:
                if not check.get("passed"):
                    print("     CHECK FAIL:", check.get("name"), "|", check.get("detail"))
            stdout = process.stdout.decode("utf-8", "replace").strip()
            if stdout and (not ok or not checks_ok):
                print("     STDOUT:", stdout[-600:].replace("\n", " | "))

    print("\n%d/%d lessons passed" % (passed, total))
    if failures:
        print("failed:", ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
