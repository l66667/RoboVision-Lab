# -*- coding: utf-8 -*-
"""Quick probes used while authoring lessons (kept as a maintenance tool)."""

import glob
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "data", "samples")


def img(name):
    return cv2.imdecode(np.fromfile(os.path.join(S, name), np.uint8), cv2.IMREAD_COLOR)


def probe_dock():
    image = img("dock.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    corners, ids, rejected = aruco.detectMarkers(gray, dictionary)
    print("dock markers:", None if ids is None else ids.ravel().tolist())
    if ids is not None:
        print("  first corner:", corners[0].reshape(-1, 2)[0])
        K = np.array([[900, 0, 640], [0, 900, 400], [0, 0, 1]], np.float32)
        dist = np.zeros(5)
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, 0.12, K, dist)
        print("  tvec:", tvecs[0].ravel(), "dist:", float(np.linalg.norm(tvecs[0])))


def probe_calib():
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((6 * 9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * 25.0
    object_points, image_points = [], []
    shape = None
    for path in sorted(glob.glob(os.path.join(S, "calib", "left*.jpg"))):
        image = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, (9, 6), None)
        print("calib", os.path.basename(path), "found", found)
        if not found:
            continue
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        object_points.append(objp)
        image_points.append(corners)
        shape = gray.shape[::-1]
    if len(object_points) >= 3:
        rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, shape, None, None)
        print("calib rms", rms, "K", K.ravel(), "dist", dist.ravel())


def probe_pcb():
    image = img("pcb.jpg")
    template = cv2.imread(os.path.join(S, "pcb_template.png"))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    tpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    score = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_score, _, max_loc = cv2.minMaxLoc(score)
    print("pcb template max", max_score, max_loc)
    orb = cv2.ORB_create(nfeatures=2500)
    kp1, des1 = orb.detectAndCompute(tpl, None)
    kp2, des2 = orb.detectAndCompute(gray, None)
    print("pcb orb kp", len(kp1), len(kp2))
    if des1 is not None and des2 is not None:
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        knn = matcher.knnMatch(des1, des2, k=2)
        good = [m for m, n in knn if m.distance < 0.75 * n.distance]
        print("pcb good", len(good))
        if len(good) >= 8:
            src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
            print("pcb H", H is not None, "inliers", int(mask.sum()) if mask is not None else 0)


def probe_flow():
    a = cv2.cvtColor(img("flow_a.jpg"), cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(img("flow_b.jpg"), cv2.COLOR_BGR2GRAY)
    pts = cv2.goodFeaturesToTrack(a, maxCorners=300, qualityLevel=0.01, minDistance=7)
    nxt, status, err = cv2.calcOpticalFlowPyrLK(a, b, pts, None)
    good = status.ravel() == 1
    d = (nxt[good] - pts[good]).reshape(-1, 2)
    print("flow tracked", int(good.sum()), "median", np.median(d, axis=0))


def probe_workcell():
    image = img("workcell.jpg")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([140, 120, 100]), np.array([170, 255, 255]))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pts = []
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:4]:
        M = cv2.moments(c)
        pts.append((M["m10"] / M["m00"], M["m01"] / M["m00"]))
    print("workcell tabs", len(pts), [tuple(round(v, 1) for v in p) for p in pts])


def probe_track():
    image = img("track.jpg")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 190]), np.array([180, 55, 255]))
    roi = mask[400:540, :]
    ys, xs = np.nonzero(roi)
    print("track white px", len(xs), "centroid", xs.mean() if len(xs) else None)


def probe_coins():
    image = img("coins.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    k = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print("coins contours", len(cnts), "area>2000", sum(1 for c in cnts if cv2.contourArea(c) > 2000))


def probe_doc():
    image = img("document.jpg")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 140]), np.array([180, 60, 255]))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(big)
    peri = cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, 0.08 * peri, True)
    print("doc approx", len(approx), approx.reshape(-1, 2).tolist())


if __name__ == "__main__":
    for fn in (probe_dock, probe_calib, probe_pcb, probe_flow, probe_workcell,
               probe_track, probe_coins, probe_doc):
        try:
            fn()
        except Exception as exc:
            print(fn.__name__, "ERROR", type(exc).__name__, exc)
