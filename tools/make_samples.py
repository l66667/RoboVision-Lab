# -*- coding: utf-8 -*-
"""Generate the synthetic robot-vision scenes used by the lessons.

Everything is drawn locally so the course has no external image downloads.
Run with the app's own interpreter:
    runtime\\Scripts\\python.exe tools\\make_samples.py
"""

import math
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "samples")


def ensure():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "calib"), exist_ok=True)


def save(name, image, quality=92):
    path = os.path.join(OUT, name)
    if name.lower().endswith(".png"):
        cv2.imwrite(path, image)
    else:
        cv2.imwrite(path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    print("wrote", path, image.shape)


def add_noise(image, sigma=3.0):
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    return np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def gradient_background(width, height, top=(18, 22, 28), bottom=(40, 46, 54)):
    top = np.array(top, np.float32)
    bottom = np.array(bottom, np.float32)
    rows = np.linspace(0, 1, height, dtype=np.float32)[:, None, None]
    image = top[None, None, :] * (1 - rows) + bottom[None, None, :] * rows
    return np.repeat(image, width, axis=1).astype(np.uint8)


def put(image, text, org, scale=0.8, color=(240, 240, 240), thickness=2):
    cv2.putText(image, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thickness, cv2.LINE_AA)


def warp_onto(board, dst_quad, size):
    """Warp a board (top-down) onto a destination quad, returning image + mask."""
    width, height = size
    src = np.float32([
        [0, 0], [board.shape[1] - 1, 0],
        [board.shape[1] - 1, board.shape[0] - 1], [0, board.shape[0] - 1],
    ])
    matrix = cv2.getPerspectiveTransform(src, np.float32(dst_quad))
    warped = cv2.warpPerspective(board, matrix, (width, height),
                                 flags=cv2.INTER_LINEAR)
    mask = cv2.warpPerspective(
        np.full(board.shape[:2], 255, np.uint8), matrix, (width, height),
        flags=cv2.INTER_NEAREST,
    )
    return warped, mask


def composite(background, warped, mask, shadow=True):
    if shadow:
        shift = np.float32([[1, 0, 10], [0, 1, 16]])
        shadow_mask = cv2.warpAffine(mask, shift, (mask.shape[1], mask.shape[0]))
        shadow_mask = cv2.GaussianBlur(shadow_mask, (31, 31), 0)
        shade = (shadow_mask.astype(np.float32) / 255.0 * 0.55)[:, :, None]
        background = (background.astype(np.float32) * (1 - shade)).astype(np.uint8)
    background[mask > 0] = warped[mask > 0]
    return background


def make_track():
    """A top-down S-curve track, then a camera-like perspective warp."""
    top = np.zeros((900, 1200, 3), np.uint8)
    top[:] = (44, 47, 50)
    top = add_noise(top, 4)
    # subtle asphalt texture
    for _ in range(1800):
        x = np.random.randint(0, 1200)
        y = np.random.randint(0, 900)
        value = np.random.randint(38, 58)
        top[y, x] = (value, value, value)

    def curve_x(y):
        t = (900 - y) / 900.0
        return int(600 + 150 * math.sin(t * math.pi * 1.7) + 60 * math.sin(t * math.pi * 4.0))

    center = np.array([[curve_x(y), y] for y in range(900, -1, -4)], np.int32)
    left = np.array([[curve_x(y) - 270, y] for y in range(900, -1, -4)], np.int32)
    right = np.array([[curve_x(y) + 270, y] for y in range(900, -1, -4)], np.int32)

    cv2.polylines(top, [left], False, (80, 180, 215), 10, cv2.LINE_AA)
    cv2.polylines(top, [right], False, (80, 180, 215), 10, cv2.LINE_AA)
    cv2.polylines(top, [center], False, (245, 245, 245), 22, cv2.LINE_AA)
    # dashed lane edges for a road feel
    for y in range(80, 860, 110):
        x = curve_x(y)
        cv2.line(top, (x - 220, y), (x - 190, y - 40), (210, 210, 210), 6, cv2.LINE_AA)
        cv2.line(top, (x + 190, y), (x + 220, y - 40), (210, 210, 210), 6, cv2.LINE_AA)

    cv2.rectangle(top, (540, 820), (660, 900), (30, 30, 30), -1)
    cv2.rectangle(top, (540, 820), (660, 900), (90, 220, 255), 4)
    put(top, "AGV", (565, 870), 0.8, (90, 220, 255), 2)

    background = gradient_background(1280, 720, (20, 24, 30), (54, 58, 62))
    # factory wall details
    for x in range(0, 1280, 160):
        cv2.line(background, (x, 0), (x + 120, 90), (30, 35, 42), 2)
    for x in range(40, 1240, 220):
        cv2.circle(background, (x, 26), 5, (120, 200, 230), -1)
    dst = np.float32([[470, 40], [810, 40], [1260, 720], [20, 720]])
    warped, mask = warp_onto(top, dst, (1280, 720))
    image = composite(background, warped, mask, shadow=False)
    save("track.jpg", image)


def make_workcell():
    """A 800 x 600 mm table seen by an angled camera with four magenta tabs."""
    width, height = 800, 600
    table = np.full((height, width, 3), (196, 198, 196), np.uint8)
    table = add_noise(table, 3)
    for x in range(0, width, 50):
        cv2.line(table, (x, 0), (x, height), (182, 184, 182), 1)
    for y in range(0, height, 50):
        cv2.line(table, (0, y), (width, y), (182, 184, 182), 1)
    # 1 mm / px  (table is exactly 800 x 600 mm)
    tabs = [(35, 35), (765, 35), (765, 565), (35, 565)]
    for i, (x, y) in enumerate(tabs):
        cv2.rectangle(table, (x - 24, y - 24), (x + 24, y + 24), (255, 0, 255), -1)
        cv2.rectangle(table, (x - 26, y - 26), (x + 26, y + 26), (40, 40, 40), 2)
        put(table, chr(65 + i), (x - 9, y + 9), 0.7, (255, 255, 255), 2)

    blocks = [
        ("R", 220, 180, (36, 36, 220), 78),
        ("G", 420, 135, (48, 178, 72), 70),
        ("B", 610, 250, (220, 82, 36), 66),
        ("Y", 300, 400, (36, 205, 232), 84),
        ("R", 620, 430, (36, 36, 220), 74),
        ("G", 490, 500, (48, 178, 72), 62),
    ]
    for label, x, y, color, size in blocks:
        cv2.circle(table, (x, y), size // 2 + 4, (55, 55, 55), -1)
        cv2.circle(table, (x, y), size // 2, color, -1)
        cv2.circle(table, (x - size // 6, y - size // 6), size // 10,
                   (245, 245, 245), -1)
        put(table, label, (x - 8, y + 8), 0.6, (255, 255, 255), 1)
    # robot base at the left edge
    cv2.circle(table, (75, 300), 48, (70, 72, 74), -1)
    cv2.circle(table, (75, 300), 30, (100, 104, 108), -1)
    put(table, "R-01", (35, 300), 0.55, (235, 235, 235), 2)

    background = gradient_background(1280, 800, (18, 22, 28), (38, 42, 48))
    for y in range(0, 800, 40):
        cv2.line(background, (0, y), (1280, y), (28, 33, 40), 1)
    dst = np.float32([[175, 70], [1105, 60], [1225, 750], [55, 770]])
    warped, mask = warp_onto(table, dst, (1280, 800))
    image = composite(background, warped, mask)
    save("workcell.jpg", image)


def make_pcb():
    width, height = 1080, 760
    board = np.full((height, width, 3), (38, 78, 58), np.uint8)
    board = add_noise(board, 2)
    # copper traces
    for _ in range(70):
        x = np.random.randint(20, width - 20)
        y = np.random.randint(20, height - 20)
        length = np.random.randint(80, 260)
        dx = np.random.choice([-1, 0, 1]) * length
        dy = np.random.choice([-1, 0, 1]) * length
        cv2.line(board, (x, y), (int(x + dx), int(y + dy)), (120, 92, 45), 3)
    # gold pads and vias
    for _ in range(55):
        x = np.random.randint(30, width - 30)
        y = np.random.randint(30, height - 30)
        cv2.circle(board, (x, y), np.random.randint(4, 9), (86, 170, 214), -1)
        cv2.circle(board, (x, y), 3, (24, 34, 30), -1)
    # chips
    chips = [(140, 120, 150, 100, "U3"), (430, 230, 190, 150, "U1"),
             (720, 120, 130, 90, "U4"), (700, 470, 170, 120, "U2")]
    for x, y, w, h, name in chips:
        cv2.rectangle(board, (x, y), (x + w, y + h), (24, 26, 28), -1)
        cv2.rectangle(board, (x, y), (x + w, y + h), (12, 14, 16), 3)
        for i in range(0, w, 18):
            cv2.rectangle(board, (x + i, y - 10), (x + i + 9, y), (190, 190, 185), -1)
            cv2.rectangle(board, (x + i, y + h), (x + i + 9, y + h + 10), (190, 190, 185), -1)
        put(board, name, (x + 8, y + h - 10), 0.5, (210, 210, 205), 1)
    put(board, "ROBO-7", (452, 320), 0.95, (238, 238, 228), 2)
    put(board, "VISION CONTROL BOARD", (120, 680), 0.7, (238, 238, 228), 2)
    cv2.drawMarker(board, (620, 330), (238, 238, 228), cv2.MARKER_CROSS, 34, 3)
    cv2.rectangle(board, (400, 200), (660, 430), (230, 230, 220), 2)
    # template crop from the unrotated board
    template = board[200:430, 400:660].copy()
    cv2.imwrite(os.path.join(OUT, "pcb_template.png"), template)

    rotated = cv2.warpAffine(
        board, cv2.getRotationMatrix2D((width / 2, height / 2), 15, 1.0),
        (width, height), flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(20, 24, 28),
    )
    background = gradient_background(1280, 800, (16, 19, 24), (30, 34, 40))
    canvas = background.copy()
    x0, y0 = 70, 20
    canvas[y0:y0 + rotated.shape[0], x0:x0 + rotated.shape[1]] = rotated
    save("pcb.jpg", canvas)
    print("wrote", os.path.join(OUT, "pcb_template.png"), template.shape)


def make_dock():
    size = 300
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    if hasattr(cv2.aruco, "generateImageMarker"):
        marker = cv2.aruco.generateImageMarker(dictionary, 7, size)
    else:
        marker = cv2.aruco.drawMarker(dictionary, 7, size)
    marker = cv2.copyMakeBorder(marker, 36, 36, 36, 36,
                                cv2.BORDER_CONSTANT, value=255)

    panel = np.full((520, 560, 3), (52, 56, 60), np.uint8)
    panel = add_noise(panel, 2)
    cv2.rectangle(panel, (0, 0), (559, 519), (28, 31, 35), 8)
    cv2.rectangle(panel, (36, 36), (523, 483), (72, 78, 84), 2)
    put(panel, "DOCK 07", (46, 72), 1.0, (90, 230, 190), 2)
    put(panel, "CHARGING STATION", (46, 500), 0.6, (200, 205, 210), 1)
    cv2.circle(panel, (500, 58), 9, (60, 240, 140), -1)
    # marker is pasted with a slight in-plane rotation
    mh, mw = marker.shape
    m = cv2.getRotationMatrix2D((mw / 2, mh / 2), -7, 0.62)
    marker_w = cv2.warpAffine(marker, m, (mw, mh), borderValue=255)
    marker_bgr = cv2.cvtColor(marker_w, cv2.COLOR_GRAY2BGR)
    px, py = 146, 132
    panel[py:py + mh, px:px + mw] = marker_bgr
    # metal contacts below
    cv2.rectangle(panel, (150, 440), (410, 470), (130, 134, 138), 3)
    cv2.rectangle(panel, (175, 440), (225, 470), (196, 170, 90), -1)
    cv2.rectangle(panel, (335, 440), (385, 470), (196, 170, 90), -1)

    background = gradient_background(1280, 800, (18, 22, 28), (46, 50, 56))
    for y in range(0, 800, 50):
        cv2.line(background, (0, y), (1280, y), (30, 35, 42), 1)
    dst = np.float32([[350, 90], [1040, 60], [1100, 760], [260, 760]])
    warped, mask = warp_onto(panel, dst, (1280, 800))
    image = composite(background, warped, mask)
    save("dock.jpg", image)


def make_calib():
    square = 42
    cols, rows = 10, 7
    margin = 50
    board = np.full((rows * square + 2 * margin, cols * square + 2 * margin),
                    245, np.uint8)
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                y0 = margin + r * square
                x0 = margin + c * square
                board[y0:y0 + square, x0:x0 + square] = 20
    cv2.imwrite(os.path.join(OUT, "calib", "board.png"), board)
    board_bgr = cv2.cvtColor(board, cv2.COLOR_GRAY2BGR)

    rng = np.random.default_rng(7)
    K0 = np.array([[760.0, 0, 400.0], [0, 760.0, 300.0], [0, 0, 1]], np.float64)
    dist0 = np.zeros(5)
    board_w_mm = board.shape[1] * 25.0 / square
    board_h_mm = board.shape[0] * 25.0 / square
    corners_3d = np.float32([
        [0, 0, 0], [board_w_mm, 0, 0],
        [board_w_mm, board_h_mm, 0], [0, board_h_mm, 0],
    ])
    for index in range(6):
        # Project a physical board through a known camera.  Using a real
        # projection (instead of an arbitrary trapezoid) keeps the six views
        # geometrically consistent, so calibration recovers a sane K.
        for _ in range(40):
            rvec = np.float32([
                rng.uniform(-0.35, 0.35),
                rng.uniform(-0.35, 0.35),
                rng.uniform(-0.40, 0.40),
            ])
            tvec = np.float32([
                rng.uniform(-70, 70), rng.uniform(-50, 50), rng.uniform(560, 760),
            ])
            projected, _ = cv2.projectPoints(corners_3d, rvec, tvec, K0, dist0)
            pts = projected.reshape(4, 2)
            if (pts[:, 0].min() > 15 and pts[:, 0].max() < 785 and
                    pts[:, 1].min() > 15 and pts[:, 1].max() < 585):
                break
        src = np.float32([
            [0, 0], [board.shape[1] - 1, 0],
            [board.shape[1] - 1, board.shape[0] - 1], [0, board.shape[0] - 1],
        ])
        matrix = cv2.getPerspectiveTransform(src, pts.astype(np.float32))
        background = gradient_background(800, 600, (38, 42, 46), (70, 74, 78))
        warped = cv2.warpPerspective(
            board_bgr, matrix, (800, 600), flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=(58, 62, 66),
        )
        mask = cv2.warpPerspective(
            np.full(board_bgr.shape[:2], 255, np.uint8), matrix, (800, 600),
            flags=cv2.INTER_NEAREST,
        )
        image = composite(background, warped, mask, shadow=True)
        image = add_noise(image, 2.5)
        cv2.imwrite(os.path.join(OUT, "calib", "left%02d.jpg" % (index + 1)), image)
    print("wrote calib/left01..06.jpg  (K0 fx=760)")


def make_flow():
    path = os.path.join(OUT, "pcb.jpg")
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (960, 600))
    a = image[30:570, 40:920].copy()
    matrix = cv2.getRotationMatrix2D((a.shape[1] / 2, a.shape[0] / 2), 0.5, 1.0)
    matrix[0, 2] += 9
    matrix[1, 2] += 3
    b = cv2.warpAffine(a, matrix, (a.shape[1], a.shape[0]),
                       flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REFLECT)
    a = add_noise(a, 1.5)
    b = add_noise(b, 1.5)
    save("flow_a.jpg", a)
    save("flow_b.jpg", b)


def main():
    ensure()
    np.random.seed(20261101)
    make_track()
    make_workcell()
    make_pcb()
    make_dock()
    make_calib()
    make_flow()


if __name__ == "__main__":
    main()
