# -*- coding: utf-8 -*-
"""第三章：机器人视觉实战。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, seg, param, test, task, quiz, target, lesson, chapter,
)

L1 = lesson(
    "robot-line",
    "循迹 AGV：从像素偏差到 PID 转向",
    "ROI、逐行中心线、cross-track error、P/I/D 三项与输出限幅",
    chapter="robot",
    mode="vision",
    sample="track.jpg",
    difficulty=4,
    minutes=55,
    tags=["循迹", "PID", "AGV"],
    objectives=[
        "只保留白色中心线，并在每一行提取最长白色线段的中点",
        "把「机器人偏离中心线多少像素」变成控制误差",
        "实现带积分限幅和输出限幅的 PID，观察 settling time 与超调",
    ],
    concept=[
        P("循迹小车的相机看到的是透视画面：线在远处窄、近处宽。工业上不会直接拿整张图算，而是裁一条靠近车头的 ROI，逐行找线的中心，再用最近几行的中心估计车头相对线的横向偏差。"),
        FORMULA("error = x_line − x_robot", "横向偏差（cross-track error）"),
        H("PID 三项分别在做什么"),
        UL(
            "**P（比例）**：误差越大，转向越猛。只有 P 会稳态误差，也可能震荡。",
            "**I（积分）**：累积历史误差，消掉持续偏置（比如轮子轻微跑偏）。积分要限幅，否则会 windup。",
            "**D（微分）**：看误差变化速度，提前刹车，抑制超调。它对噪声敏感。",
        ),
        FORMULA("u = Kp·e + Ki·∫e dt + Kd·de/dt", "输出再限幅到 ±max_steer"),
        NOTE("这是简化模型", "真实 AGV 还有航向角、轮距、编码器、IMU 和延迟。这一课只控制横向位置，目的是把「视觉误差 → 控制量」这条链路讲清楚；真车要把同样的误差送进速度环/转向环。", "info"),
    ],
    walkthrough=[
        seg(
            "提取白色中心线掩膜",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([0, 0, 190]), np.array([180, 60, 255]))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
roi_top, roi_bottom = 120, 545
print("白色像素:", int(mask.sum() // 255))
''',
            "白色线的 V 很高、S 很低，所以用低饱和 + 高明度提取。黄色边线 S 高，会被排除。闭运算把虚线/反光造成的小断点接上。ROI 去掉画面顶部的墙面和底部的车体。",
            "如果现场灯光偏黄，白色线的 S 会升高，需要把 S 上限调大，或改用灰度阈值。",
        ),
        seg(
            "逐行取最长白段的中点",
            r'''
def longest_run(row):
    xs = np.flatnonzero(row > 0)
    if xs.size == 0:
        return None
    groups = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
    run = max(groups, key=len)
    if len(run) < 4:
        return None
    return float(run.mean())

center_x = {}
for y in range(roi_top, roi_bottom):
    value = longest_run(mask[y])
    if value is not None:
        center_x[y] = value
print("可用行数:", len(center_x), "底部中心:", round(center_x[max(center_x)], 1))
''',
            "每一行可能同时有中心线、边线虚线、反光。取「最长连续白段」可以稳定选中粗的中心线，而不是短虚线。保存成 `{y: x}` 字典，后面按行查。",
            "不要对整张掩膜求一个质心：弯道时左右边线会把质心拉偏。逐行处理才能保留弯道形状。",
        ),
        seg(
            "可视化检测结果",
            r'''
vis = image.copy()
for y, x in center_x.items():
    cv2.circle(vis, (int(x), y), 1, (0, 255, 120), -1)
metric("中心线行数", len(center_x))
''',
            "把每一行检测到的中心点画出来，能立刻看出线是否连续、是否被边线带偏。调试视觉时，先看掩膜和叠加图，再看数值。",
        ),
        seg(
            "PID 循迹仿真",
            r'''
kp, ki, kd = float(p["kp"]), float(p["ki"]), float(p["kd"])
speed = int(p["speed"])
max_steer = 8.0

x = center_x[max(center_x)] + 90.0
y = max(center_x)
integral = 0.0
previous_error = 0.0
history = []

for step in range(130):
    y -= speed
    if y < min(center_x):
        break
    setpoint = center_x[y]
    error = setpoint - x
    integral = max(-200.0, min(200.0, integral + error))
    derivative = error - previous_error
    steer = kp * error + ki * integral + kd * derivative
    steer = max(-max_steer, min(max_steer, steer))
    x += steer
    history.append({"step": step, "y": y, "error": error, "steer": steer, "x": x})
    previous_error = error
    cv2.circle(vis, (int(x), int(y)), 2, (0, 220, 255), -1)

final_error = history[-1]["error"]
max_error = max(abs(h["error"]) for h in history)
settling_step = len(history)
for i in range(len(history)):
    if all(abs(h["error"]) < 5 for h in history[i:]):
        settling_step = i
        break
print("最终误差: %.2f px  最大误差: %.2f px" % (final_error, max_error))
print("进入 ±5 px 的步数:", settling_step)
metric("最终误差", round(final_error, 2))
metric("最大误差", round(max_error, 2))
metric("settling_step", settling_step)
''',
            "机器人从中心线右侧 90 px 出发，每步向上移动 `speed` 像素，PID 根据当前行的中心线位置修正 x。积分限幅 ±200 防止 windup，输出限幅 ±8 像素/步模拟最大转向。`settling_step` 是第一次进入 ±5 px 并一直保持的步数。",
            "先调 P 让车能回线，再加 D 抑制超调，最后用很小的 I 消稳态误差。一次只改一个参数。",
        ),
        seg(
            "画出误差与转向曲线",
            r'''
plot = np.full((340, 860, 3), 18, np.uint8)
cv2.line(plot, (50, 170), (830, 170), (70, 70, 70), 1)
for i, item in enumerate(history):
    px = 50 + int(i * 780 / max(1, len(history) - 1))
    ey = 170 - int(max(-60, min(60, item["error"])) * 2.2)
    uy = 170 - int(max(-8, min(8, item["steer"])) * 14)
    if i == 0:
        prev_e = (px, ey)
        prev_u = (px, uy)
        continue
    cv2.line(plot, prev_e, (px, ey), (80, 120, 255), 2)
    cv2.line(plot, prev_u, (px, uy), (90, 230, 210), 2)
    prev_e = (px, ey)
    prev_u = (px, uy)
cv2.putText(plot, "error (red) / steer (cyan)", (50, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 230), 2, cv2.LINE_AA)
cv2.putText(plot, "step ->", (740, 320), cv2.FONT_HERSHEY_SIMPLEX,
            0.55, (180, 180, 180), 1, cv2.LINE_AA)
capture("PID 响应曲线", plot)
capture("循迹轨迹", vis)
result = vis
''',
            "红色是横向误差，青色是转向量。理想响应是快速下降、少量超调、最后贴近 0。曲线震荡说明 P 太大或 D 太小；长时间不归零说明需要一点 I。",
        ),
    ],
    tests=[
        test("中心线覆盖足够行", "len(center_x) > 300"),
        test("仿真有足够步数", "len(history) > 50"),
        test("最终误差收敛", "abs(final_error) < 15"),
        test("结果图尺寸不变", "result.shape == image.shape"),
    ],
    params=[
        param("kp", "比例增益 Kp", 0.35, 0.05, 1.2, 0.01),
        param("ki", "积分增益 Ki", 0.01, 0.0, 0.08, 0.005),
        param("kd", "微分增益 Kd", 0.08, 0.0, 0.6, 0.01),
        param("speed", "每步前进像素", 4, 2, 6, 1),
    ],
    tasks=[
        task("tune", "把 settling 压到 70 步内", "先只调 Kp，再加 Kd，最后加很小的 Ki，记录每次的 settling_step。"),
        task("dev", "加转向角限幅", "把输出限幅从 ±8 改成 ±4，观察最大误差和收敛速度的变化。"),
        task("observe", "制造震荡", "把 Kp 调到 1.0、Kd 调到 0，观察误差曲线是否来回震荡。"),
    ],
    quiz_items=[
        quiz("只有 P 控制时，最常见的稳态问题是？", ["超调", "稳态误差", "积分饱和", "噪声"], 1,
             "P 输出与误差成正比，误差很小时输出不足以克服摩擦/偏置，留下稳态误差。"),
        quiz("积分限幅的目的是？", ["加快响应", "防止 windup", "降低噪声", "改变颜色"], 1,
             "误差长时间累积会让积分项过大，限幅可避免退饱和时的严重超调。"),
        quiz("D 项对什么最敏感？", ["稳态误差", "噪声", "颜色", "分辨率"], 1,
             "微分放大高频变化，噪声大时通常要滤波或降低 Kd。"),
    ],
    industry="AGV/AMR 的循迹、车道保持、视觉伺服都用同一套「检测偏差 → 控制器 → 执行器」结构。量产车还会融合里程计、IMU、激光，PID 只是最内层的基线。",
    career="调控型岗位的核心工作就是整定 Kp/Ki/Kd、看阶跃响应、判断震荡来自控制还是视觉延迟；开发型岗位要把控制器做成可配置、可回放的模块。",
    target_spec=target("settling_step", "<=", 70, "误差进入 ±5 px 并保持，且不超过 70 步"),
    next_step="下一课把像素坐标变成机械臂能用的毫米坐标：颜色分拣 + 单应性。",
)

L2 = lesson(
    "robot-color-sort",
    "颜色分拣：从像素坐标到机械臂坐标",
    "四角标定、单应矩阵、HSV 多色检测、抓取顺序与料框分配",
    chapter="robot",
    mode="vision",
    sample="workcell.jpg",
    difficulty=4,
    minutes=55,
    tags=["分拣", "单应性", "手眼"],
    objectives=[
        "用四个已知颜色的角标建立像素→工作台毫米坐标的单应矩阵",
        "同时检测红/绿/蓝/黄物块，输出像素坐标、毫米坐标和抓取角度",
        "按行优先规划抓取顺序，并把每个物块分配到对应料框",
    ],
    concept=[
        P("相机看到的是像素，机械臂需要的是工作台毫米坐标。两者之间隔着一个平面单应变换：只要知道工作台上四个点的像素坐标和真实毫米坐标，就能解出 3×3 的 H，把任意像素点映射到毫米。"),
        FORMULA("p_mm = H · p_px（齐次坐标，最后除以 w）", "像素→工作台"),
        H("为什么用四个角色标而不是直接量比例"),
        P("相机是斜装的，近处 1 px 对应的毫米数和远处不同。单应矩阵同时处理旋转、平移、透视缩放；比例尺只是它的一个特例。四个角标要尽量分散，覆盖整个工作区，标定误差才会小。"),
        NOTE("抓取角度", "`minAreaRect` 返回的 angle 在 OpenCV 4.x 里范围是 [0, 90)，不同版本定义可能变。做夹爪对齐时，要用长边方向重新计算 0–180° 的抓取角，不能直接拿 angle 用。", "warn"),
    ],
    walkthrough=[
        seg(
            "找四个品红色角标",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
magenta = cv2.inRange(hsv, np.array([140, 120, 100]),
                      np.array([170, 255, 255]))
magenta = cv2.morphologyEx(magenta, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
contours, _ = cv2.findContours(magenta, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
tabs = []
for c in contours:
    if cv2.contourArea(c) < 1500:
        continue
    M = cv2.moments(c)
    tabs.append((M["m10"] / M["m00"], M["m01"] / M["m00"]))
print("角标数量:", len(tabs))
metric("角标数量", len(tabs))
''',
            "四个角标用唯一的品红色，避免和红/蓝/黄物块混淆。按面积取前 4 个，再过滤太小的噪点。质心就是角标中心，作为单应性的像素控制点。",
            "如果现场还有品红色物体，要换一种角标颜色，或用 ArUco 标记做唯一编码。",
        ),
        seg(
            "排序并求单应矩阵",
            r'''
pts = np.array(tabs, np.float32)
s = pts.sum(axis=1)
d = pts[:, 0] - pts[:, 1]
tl = pts[np.argmin(s)]
br = pts[np.argmax(s)]
tr = pts[np.argmax(d)]
bl = pts[np.argmin(d)]
src = np.array([tl, tr, br, bl], np.float32)

# 工作台 800 x 600 mm，角标中心在 (35,35) ... (765,565)
dst = np.array([[35, 35], [765, 35], [765, 565], [35, 565]], np.float32)
H = cv2.getPerspectiveTransform(src, dst)
print("H=\n", np.round(H, 3))
metric("单应矩阵", "成功")
''',
            "排序规则和上一章透视校正一致：x+y 最小是左上，x−y 最大是右上。目标坐标按工作台的真实毫米填。`getPerspectiveTransform` 用 4 对点解出 H。",
            "如果角标顺序错，H 会把物块映射到错误象限；先把四个点画出来确认。",
        ),
        seg(
            "检测四种颜色的物块",
            r'''
COLOR_RANGES = {
    "red": [((0, 150, 120), (10, 255, 255)),
            ((170, 150, 120), (180, 255, 255))],
    "green": [((35, 100, 60), (85, 255, 255))],
    "blue": [((90, 100, 60), (130, 255, 255))],
    "yellow": [((20, 120, 120), (35, 255, 255))],
}
blocks = []
min_area = float(p["min_area"])
for color_name, ranges in COLOR_RANGES.items():
    mask = np.zeros(image.shape[:2], np.uint8)
    for low, high in ranges:
        mask |= cv2.inRange(hsv, np.array(low), np.array(high))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        px = np.array([[[M["m10"] / M["m00"], M["m01"] / M["m00"]]]], np.float32)
        mm = cv2.perspectiveTransform(px, H)[0, 0]
        rect = cv2.minAreaRect(c)
        (_, _), (rw, rh), angle = rect
        grab_angle = angle if rw >= rh else angle + 90
        blocks.append({
            "color": color_name, "px": px[0, 0].copy(), "mm": mm,
            "area": area, "angle": grab_angle % 180,
        })
print("物块数量:", len(blocks))
metric("物块数量", len(blocks))
''',
            "每种颜色单独做掩膜，红色仍要两段。`perspectiveTransform` 把像素齐次坐标乘 H，再除以 w。`minAreaRect` 的宽高顺序不固定，所以用长边方向把抓取角归一到 0–180°。",
            "同一颜色的两个物块要分别保留；不要用「每种颜色只取最大轮廓」，否则会漏抓。",
        ),
        seg(
            "规划抓取顺序与料框",
            r'''
blocks.sort(key=lambda b: (round(b["mm"][1] / 50), b["mm"][0]))
BINS = {"red": (100, 540), "green": (300, 540),
        "blue": (500, 540), "yellow": (700, 540)}
for index, b in enumerate(blocks):
    b["seq"] = index + 1
    b["bin"] = BINS[b["color"]]
    print("#%d %-6s px=(%4.0f,%4.0f) mm=(%5.1f,%5.1f) angle=%4.1f"
          % (b["seq"], b["color"], b["px"][0], b["px"][1],
             b["mm"][0], b["mm"][1], b["angle"]))
''',
            "按毫米 y 每 50 mm 分带、再按 x 排序，得到「从近到远、从左到右」的抓取顺序。料框坐标是工艺布局，不是视觉算出来的；真实系统从配置文件读取。",
            "抓取顺序还要考虑机械臂可达性、避障和节拍；这里先用最简单的行优先。",
        ),
        seg(
            "叠加显示与料框",
            r'''
vis = image.copy()
for i, b in enumerate(blocks):
    x, y = int(b["px"][0]), int(b["px"][1])
    cv2.circle(vis, (x, y), 16, (255, 255, 255), 2)
    cv2.putText(vis, "%d %s" % (b["seq"], b["color"]), (x - 34, y - 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

H_inv = np.linalg.inv(H)
bin_points = np.array([BINS[b["color"]] for b in blocks], np.float32).reshape(-1, 1, 2)
bin_px = cv2.perspectiveTransform(bin_points, H_inv).reshape(-1, 2)
for b, target_px in zip(blocks, bin_px):
    cv2.arrowedLine(vis, tuple(b["px"].astype(int)),
                    tuple(target_px.astype(int)), (120, 220, 120), 2,
                    tipLength=0.04)
counts = {c: sum(1 for b in blocks if b["color"] == c) for c in BINS}
cv2.putText(vis, "  ".join("%s:%d" % (k, v) for k, v in counts.items()),
            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
result = vis
''',
            "把物块编号和颜色画在像素位置，再用 `H_inv` 把料框毫米坐标反投影回画面，画箭头。这样一眼能看出「哪个物块去哪个框」，也方便检查 H 是否把方向搞反。",
        ),
    ],
    tests=[
        test("四个角标", "len(tabs) == 4"),
        test("至少五个物块", "len(blocks) >= 5"),
        test("毫米坐标在工作台内", "all(0 <= b['mm'][0] <= 800 and 0 <= b['mm'][1] <= 600 for b in blocks)"),
        test("每个物块有序号", "all(b.get('seq', 0) > 0 for b in blocks)"),
    ],
    params=[
        param("min_area", "物块最小面积", 700, 200, 3000, 100),
    ],
    tasks=[
        task("dev", "按颜色优先级排序", "改成红→黄→蓝→绿，再按 y 排序，打印新的抓取序列。"),
        task("dev", "输出抓取位姿", "给每个物块加一个 `z=0`，组成 (x, y, z, angle) 四元组，模拟发给机械臂的位姿。"),
        task("observe", "把 H 用反", "把 `H_inv` 和 `H` 互换，观察箭头指向和毫米坐标如何变化。"),
    ],
    quiz_items=[
        quiz("单应变换需要几对点？", ["2", "3", "4", "6"], 2,
             "3×3 单应矩阵有 8 个自由度，需要 4 对点。"),
        quiz("角标为什么要分散？", ["好看", "覆盖工作区，降低外推误差", "加快检测", "避免反光"], 1,
             "四点在画面中覆盖越大，H 在工作区内的数值稳定性越好。"),
        quiz("`minAreaRect` 的 angle 能直接用吗？", ["能", "不能，要按长边归一化", "只能用于正方形", "必须是弧度"], 1,
             "OpenCV 4.x 的 angle 定义与长边/短边有关，抓取角要重新归一化。"),
    ],
    industry="视觉分拣站的标准链路是：标定（像素↔毫米）→ 检测（颜色/形状/深度学习）→ 位姿估计（x,y,angle）→ 抓取规划 → 机械臂/吸盘执行。手眼标定、传送带跟踪、节拍优化是现场的核心问题。",
    career="开发型岗位负责标定、坐标变换和抓取位姿接口；调控型岗位负责光照、阈值、料框布局和误抓分析。",
    next_step="下一课用 ArUco 标记做对接：不仅要知道「在哪」，还要知道「离多远、偏多少度」。",
)

L3 = lesson(
    "robot-aruco",
    "ArUco 对接：从标记到距离与航向",
    "标记检测、solvePnP 位姿、相机坐标、对接速度指令",
    chapter="robot",
    mode="vision",
    sample="dock.jpg",
    difficulty=4,
    minutes=50,
    tags=["ArUco", "位姿", "对接"],
    objectives=[
        "用 ArUco 检测标记 ID 和四个角点",
        "用已知相机内参和标记边长估计平移向量 tvec",
        "把距离/方位角变成前进速度和角速度指令",
    ],
    concept=[
        P("ArUco 是一种二维码式的基准标记：黑白方块、自带 ID、四个角点可精确定位。相机看到标记后，结合已知的标记边长和相机内参，就能用 PnP 解出标记相对相机的三维位姿（旋转 + 平移）。"),
        FORMULA("Z ≈ fx · L / w_px", "粗略距离：焦距 × 标记边长 / 像素边长"),
        H("相机坐标系怎么读"),
        UL(
            "**x**：向右，**y**：向下，**z**：向前（沿光轴）。",
            "`tvec` 的 z 约等于正前方距离；x 决定左右；`atan2(x, z)` 是方位角。",
            "`rvec` 是旋转向量，可用 `Rodrigues` 转成旋转矩阵，得到标记相对相机的姿态。",
        ),
        NOTE("内参必须准", "同一个标记，用错焦距会让距离成比例地错。标定课得到的 K 要保存成配置，不要每次手填。标记越大、越正对相机、越靠近画面中心，位姿越稳。", "warn"),
    ],
    walkthrough=[
        seg(
            "检测标记",
            r'''
import cv2
import numpy as np

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
corners, ids, rejected = aruco.detectMarkers(gray, dictionary, parameters=parameters)
found = ids is not None and len(ids) > 0
marker_id = int(ids.ravel()[0]) if found else -1
print("检测到标记:", found, "ID:", marker_id)
metric("标记 ID", marker_id)
''',
            "`DICT_4X4_50` 表示 4×4 位、最多 50 个 ID 的字典。`detectMarkers` 返回角点、ID 和被拒绝的候选。工业上常用 5×5 或 6×6 字典，位越多越不容易误检。",
            "字典必须和打印标记时用的一致；用错字典会检测不到或 ID 错乱。",
        ),
        seg(
            "估计位姿",
            r'''
K = np.array([[900.0, 0, 640.0], [0, 900.0, 400.0], [0, 0, 1.0]], np.float32)
dist = np.zeros((5, 1), np.float32)
marker_size = float(p["marker_size"])
rvec = tvec = None
distance = bearing = 0.0
if found:
    rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
        corners, marker_size, K, dist)
    rvec = rvecs[0][0]
    tvec = tvecs[0][0]
    distance = float(np.linalg.norm(tvec))
    bearing = float(np.degrees(np.arctan2(tvec[0], tvec[2])))
    print("tvec (m):", np.round(tvec, 3))
    print("距离: %.3f m  方位角: %.1f deg" % (distance, bearing))
metric("距离(m)", round(distance, 3))
metric("方位角(deg)", round(bearing, 1))
''',
            "`estimatePoseSingleMarkers` 用四个角点和标记物理边长做 PnP。`tvec` 单位是米（因为 marker_size 用米）。距离是 tvec 的模；方位角用 x/z 的反正切，右偏为正。",
            "如果传的 marker_size 是厘米，距离会差 100 倍；单位必须和 K 的假设一致。",
        ),
        seg(
            "把位姿变成对接指令",
            r'''
v_cmd = w_cmd = 0.0
if found:
    target_distance = float(p["target_distance"])
    v_cmd = float(np.clip(0.6 * (distance - target_distance), -0.25, 0.25))
    w_cmd = float(np.clip(-1.3 * bearing, -1.0, 1.0))
    print("cmd_vel: linear=%.3f m/s  angular=%.3f rad/s" % (v_cmd, w_cmd))
metric("前进速度(m/s)", round(v_cmd, 3))
metric("角速度(rad/s)", round(w_cmd, 3))
''',
            "距离大于目标距离就前进，小于就后退；方位角为正（标记在右）时，机器人应右转，按 REP-103 右转是负角速度，所以取负号。输出限幅防止指令过大。",
            "真实底盘还要考虑死区、加速度限制和里程计闭环；这里是外环的视觉伺服。",
        ),
        seg(
            "画坐标轴与 HUD",
            r'''
result = image.copy()
if found:
    aruco.drawDetectedMarkers(result, corners, ids)
    cv2.drawFrameAxes(result, K, dist, rvec, tvec, 0.08)
    text = "ID %d  Z=%.2fm  bearing=%.1fdeg" % (marker_id, distance, bearing)
    cv2.putText(result, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (80, 230, 160), 2, cv2.LINE_AA)
    cv2.putText(result, "v=%.2f m/s  w=%.2f rad/s" % (v_cmd, w_cmd),
                (30, 86), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 220, 120), 2, cv2.LINE_AA)
else:
    cv2.putText(result, "marker not found", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
''',
            "`drawFrameAxes` 把标记坐标系画出来：红 X、绿 Y、蓝 Z，长度 8 cm。HUD 显示 ID、距离、方位和控制指令，现场调试时不用盯终端。",
        ),
    ],
    tests=[
        test("检测到标记", "found is True"),
        test("ID 是 7", "marker_id == 7"),
        test("距离在合理范围", "0.15 < distance < 1.2"),
        test("方位角不过大", "abs(bearing) < 45"),
    ],
    params=[
        param("marker_size", "标记边长（米）", 0.12, 0.05, 0.30, 0.01),
        param("target_distance", "目标对接距离（米）", 0.35, 0.10, 0.80, 0.01),
    ],
    tasks=[
        task("dev", "加死区", "距离目标 ±0.02 m 内把 v_cmd 设为 0，方位角 ±2° 内把 w_cmd 设为 0，避免抖动。"),
        task("dev", "输出对齐误差", "把 bearing 和 distance 写入一个字典，模拟通过串口发给底盘。"),
        task("observe", "改错内参", "把 fx 从 900 改成 600，观察距离估计如何变化，并解释原因。"),
    ],
    quiz_items=[
        quiz("ArUco 的 tvec 中 z 通常表示？", ["左右", "上下", "前后距离", "旋转"], 2,
             "相机坐标系 z 沿光轴向前。"),
        quiz("marker_size 单位用错会导致？", ["检测不到", "ID 错", "距离成比例错", "图像变灰"], 2,
             "PnP 用物理边长解尺度，单位错会整体缩放平移。"),
        quiz("标记在画面右侧，机器人应？", ["左转", "右转", "后退", "停下"], 1,
             "方位角为正，右转（负角速度）让标记回到画面中心。"),
    ],
    industry="ArUco/AprilTag 常用于充电桩对接、AGV 站点定位、无人机降落、AR 标定。更复杂的场景会用多标记板、Charuco 板，或直接训练关键点网络。",
    career="开发型岗位要处理内参、坐标系、PnP 和滤波；调控型岗位要会看 tvec 抖动、标记反光、安装角度和对接成功率。",
    next_step="下一课把相机本身标定出来：棋盘格、内参、畸变系数和去畸变。",
)

L4 = lesson(
    "robot-calib",
    "相机标定：把像素变成可测量的毫米",
    "棋盘格角点、calibrateCamera、内参矩阵、畸变系数、去畸变",
    chapter="robot",
    mode="vision",
    sample="calib/left01.jpg",
    difficulty=5,
    minutes=60,
    tags=["标定", "内参", "畸变"],
    objectives=[
        "用多张棋盘格图像找 9×6 内角点并做亚像素细化",
        "标定出内参 K、畸变系数和重投影误差 RMS",
        "用 K/dist 去畸变，并理解为什么测量前必须先标定",
    ],
    concept=[
        P("相机标定回答三个问题：焦距是多少、光心在哪、镜头畸变多大。没有标定，像素坐标没有物理意义；标定之后，才能把像素变成角度、毫米，或者做准确的 PnP/三维重建。"),
        TABLE(
            ["输出", "含义", "典型用途"],
            [
                ["K = [[fx,0,cx],[0,fy,cy],[0,0,1]]", "内参矩阵", "去畸变、PnP、三维重建"],
                ["dist = [k1,k2,p1,p2,k3]", "径向/切向畸变", "去畸变、畸变校正"],
                ["RMS", "重投影误差（像素）", "判断标定质量"],
            ],
        ),
        FORMULA("RMS = sqrt( mean( (p_reproj − p_detected)² ) )", "越小越好，通常 < 0.5 px"),
        NOTE("标定板要动起来", "所有图都正对相机、同一个距离，焦距会欠约束。要让标定板覆盖画面四角、不同距离、不同倾角；至少 10–15 张，工业上常拍 30 张以上。", "warn"),
    ],
    walkthrough=[
        seg(
            "准备棋盘格与三维点",
            r'''
import cv2
import glob
import os
import numpy as np

pattern = (9, 6)          # 内角点：9 列 x 6 行
square_mm = float(p["square_size"])
objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2) * square_mm
paths = sorted(glob.glob(os.path.join(sample_dir, "calib", "left*.jpg")))
if not paths:
    paths = sorted(glob.glob(os.path.join(sample_dir, "left*.jpg")))
print("标定图数量:", len(paths), " 方格边长:", square_mm, "mm")
''',
            "`objp` 是标定板在自身坐标系里的三维点：z=0，x/y 按方格边长排成网格。所有图共用同一组三维点，因为标定板是同一个。`mgrid` 的顺序要和 `findChessboardCorners` 返回的角点顺序一致。",
            "`pattern` 是内角点数，不是方格数：10×7 个方格对应 9×6 个内角点。",
        ),
        seg(
            "逐张找角点并亚像素细化",
            r'''
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
object_points, image_points = [], []
first = None
first_corners = None
for path in paths:
    frame = read_image(path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ok, corners = cv2.findChessboardCorners(gray, pattern, None)
    if not ok:
        print("跳过（未找到角点）:", os.path.basename(path))
        continue
    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    object_points.append(objp)
    image_points.append(corners)
    if first is None:
        first = frame
        first_corners = corners
        image_size = (gray.shape[1], gray.shape[0])
print("成功:", len(object_points), "张")
metric("标定图数量", len(object_points))
''',
            "`cornerSubPix` 在初检测的角点附近做亚像素迭代，把精度从整像素提到 0.1 px 量级。`image_size` 是 `(宽, 高)`，顺序不能反。",
            "角点检测失败通常是光照太暗、棋盘格不完整、图案不是标准黑白格；先看 `found` 再调。",
        ),
        seg(
            "执行标定",
            r'''
rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points, image_points, image_size, None, None)
print("RMS 重投影误差: %.3f px" % rms)
print("K=\n", np.round(K, 2))
print("dist=", np.round(dist.ravel(), 4))
metric("RMS(px)", round(float(rms), 3))
metric("fx", round(float(K[0, 0]), 1))
metric("fy", round(float(K[1, 1]), 1))
''',
            "`calibrateCamera` 同时优化 K、dist 和每张图的位姿，让三维点重投影回图像后与检测角点误差最小。RMS 是整体误差，通常要求 < 0.5 px；太大说明某张图角点检测错了。",
            "`dist` 是 1×5 数组，依次是 k1,k2,p1,p2,k3。不要把它当成 5 个独立标量乱序使用。",
        ),
        seg(
            "去畸变与差异放大",
            r'''
undistorted = cv2.undistort(first, K, dist)
diff = cv2.absdiff(first, undistorted)
diff = cv2.convertScaleAbs(diff, alpha=10)
corner_vis = first.copy()
cv2.drawChessboardCorners(corner_vis, pattern, first_corners, True)
capture("角点检测", corner_vis)
capture("畸变差异（放大10倍）", diff)
''',
            "`undistort` 用 K 和 dist 把像素映射回理想针孔模型。差异图放大 10 倍才能看清边缘的弯曲。真实镜头的畸变在画面四角最明显。",
        ),
        seg(
            "拼对比图",
            r'''
def label(img, text):
    out = img.copy()
    out = cv2.resize(out, (600, 450))
    cv2.rectangle(out, (0, 0), (600, 34), (20, 20, 20), -1)
    cv2.putText(out, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2, cv2.LINE_AA)
    return out

result = np.hstack([
    label(first, "original"),
    label(undistorted, "undistorted"),
    label(corner_vis, "corners"),
])
''',
            "原图、去畸变、角点检测三张并排，是最直观的标定报告。工业上会把 RMS、K、dist 和标定日期一起存档，换镜头/摔相机后必须重标。",
        ),
    ],
    tests=[
        test("六张图都找到角点", "len(object_points) == 6"),
        test("RMS 小于 1 px", "rms < 1.0"),
        test("焦距在合理范围", "500 < K[0, 0] < 1200"),
        test("去畸变尺寸不变", "undistorted.shape == first.shape"),
    ],
    params=[
        param("square_size", "棋盘格边长（mm）", 25, 10, 60, 1),
    ],
    tasks=[
        task("dev", "输出每张图误差", "用 `projectPoints` 把每张图的三维点重投影，打印每张的 RMS，找出最差的一张。"),
        task("dev", "保存标定结果", "把 K、dist、RMS 写进 `work_dir/calibration.json`，供其他程序读取。"),
        task("observe", "只用三张图", "把 paths 切片成前 3 张，重新标定，比较 RMS 和 fx 的稳定性。"),
    ],
    quiz_items=[
        quiz("棋盘格 10×7 个方格，内角点是？", ["10×7", "9×6", "8×5", "11×8"], 1,
             "内角点比方格数各少 1。"),
        quiz("RMS 重投影误差主要衡量？", ["颜色误差", "标定质量", "帧率", "畸变类型"], 1,
             "三维点重投影回图像与检测角点的平均距离。"),
        quiz("标定板所有图都正对相机，会怎样？", ["更准", "焦距欠约束", "无法检测角点", "RMS 一定为 0"], 1,
             "缺少不同倾角和覆盖，焦距/畸变参数难以区分。"),
    ],
    industry="相机标定是机器人视觉的「量具校准」。手眼标定、双目测距、结构光、SLAM 都以内参为基础；产线换镜头、碰撞、温度漂移后都要复标。",
    career="开发型岗位要写标定工具、管理参数版本；调控型岗位要会判断标定是否失效（RMS 变大、直线变弯、抓取偏移）。",
    next_step="下一课用光流估计运动：不依赖标记，也能从画面变化算出速度。",
)

L5 = lesson(
    "robot-flow",
    "光流与视觉里程计：从画面运动算速度",
    "goodFeaturesToTrack、Lucas-Kanade、前向追踪、像素位移→m/s",
    chapter="robot",
    mode="vision",
    sample="flow_a.jpg",
    difficulty=4,
    minutes=50,
    tags=["光流", "LK", "里程计"],
    objectives=[
        "用 Shi-Tomasi 找可跟踪的角点",
        "用 Lucas-Kanade 稀疏光流跟踪两帧之间的位移",
        "把像素位移、比例尺和时间间隔换算成机器人速度",
    ],
    concept=[
        P("光流假设「同一点在相邻两帧里亮度不变，且运动很小」。Lucas-Kanade 在每个角点周围取一个小窗口，解一个最小二乘方程，得到该点的位移 (u, v)。"),
        FORMULA("I(x,y,t) = I(x+u, y+v, t+1)", "亮度恒定假设"),
        H("为什么只跟踪角点"),
        P("平坦区域（白墙、桌面）在任何方向移动都长得一样，方程欠定；边缘只能约束法向运动；只有角点在两个方向都有梯度，位移才可解。`goodFeaturesToTrack` 找的就是这种点。"),
        FORMULA("v = Δp · scale / Δt", "像素位移 → 米/秒"),
        NOTE("光流不是万能的", "快速运动、运动模糊、重复纹理、光照突变都会让跟踪失败。工业上会加 IMU/轮速做融合，或用特征点+描述子做重定位。", "warn"),
    ],
    walkthrough=[
        seg(
            "读取两帧",
            r'''
import cv2
import os
import numpy as np

path_b = os.path.join(sample_dir, "flow_b.jpg")
frame_b = read_image(path_b)
gray_a = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)
print("A/B 尺寸:", gray_a.shape, gray_b.shape)
''',
            "光流需要同一场景的连续两帧。这里用两张预先准备好的图模拟 1/30 秒内的运动。真实机器人从相机流里取相邻帧，时间戳要用硬件时间，不能用处理完成时间。",
        ),
        seg(
            "找可跟踪角点",
            r'''
max_corners = int(p["max_corners"])
min_distance = float(p["min_distance"])
points_a = cv2.goodFeaturesToTrack(
    gray_a, maxCorners=max_corners, qualityLevel=0.01,
    minDistance=min_distance, blockSize=7)
print("初始角点:", 0 if points_a is None else len(points_a))
metric("初始角点", 0 if points_a is None else len(points_a))
''',
            "`qualityLevel=0.01` 表示保留最强角点的 1% 作为阈值；`minDistance` 防止角点扎堆。角点太多会拖慢跟踪，太少则估计不稳。",
        ),
        seg(
            "Lucas-Kanade 跟踪",
            r'''
points_b, status, error = cv2.calcOpticalFlowPyrLK(
    gray_a, gray_b, points_a, None,
    winSize=(21, 21), maxLevel=3,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
good_new = points_b[status.ravel() == 1].reshape(-1, 2)
good_old = points_a[status.ravel() == 1].reshape(-1, 2)
print("跟踪成功:", len(good_new))
metric("跟踪成功", len(good_new))
''',
            "`winSize` 是每个角点的搜索窗口，`maxLevel=3` 用图像金字塔处理较大位移。`status==1` 表示该点跟踪成功；失败的点直接丢弃。",
            "窗口太小追不上快速运动，太大容易跟到旁边纹理；金字塔层数可以缓解大位移。",
        ),
        seg(
            "画轨迹并估计位移",
            r'''
vis = image.copy()
for new, old in zip(good_new, good_old):
    x0, y0 = old.ravel()
    x1, y1 = new.ravel()
    cv2.line(vis, (int(x0), int(y0)), (int(x1), int(y1)), (80, 220, 120), 1)
    cv2.circle(vis, (int(x1), int(y1)), 2, (0, 220, 255), -1)

delta = good_new - good_old
median_dx = float(np.median(delta[:, 0]))
median_dy = float(np.median(delta[:, 1]))
print("中位位移: dx=%.2f px  dy=%.2f px" % (median_dx, median_dy))
metric("dx(px)", round(median_dx, 2))
metric("dy(px)", round(median_dy, 2))
''',
            "每个成功点画一条从旧位置到新位置的短线。用中位数而不是平均值，可以抵抗少量错配的离群点。dx 为正表示画面内容向右移动，机器人通常向左运动（取决于相机安装方向）。",
        ),
        seg(
            "换算成速度",
            r'''
scale_m_per_px = float(p["scale_mm_per_px"]) / 1000.0
dt = 1.0 / 30.0
speed = float(np.hypot(median_dx, median_dy) * scale_m_per_px / dt)
print("估计速度: %.3f m/s" % speed)
cv2.putText(vis, "v=%.2f m/s  dx=%.1fpx" % (speed, median_dx),
            (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
metric("速度(m/s)", round(speed, 3))
result = vis
''',
            "比例尺必须由标定或已知地面纹理得到；`dt` 用真实帧间隔。像素位移 × 比例尺 = 米，再除以时间 = 米/秒。没有比例尺，光流只能给出「像素/秒」，不能给出物理速度。",
            "如果相机是斜装的，画面不同位置的像素比例尺不同；高精度要用单应性或深度。",
        ),
    ],
    tests=[
        test("初始角点足够", "points_a is not None and len(points_a) > 100"),
        test("跟踪成功足够", "len(good_new) > 50"),
        test("位移方向正确", "median_dx > 4"),
        test("速度为正", "speed > 0"),
    ],
    params=[
        param("max_corners", "最大角点数", 300, 100, 600, 50),
        param("min_distance", "角点最小间距", 7, 3, 20, 1),
        param("scale_mm_per_px", "比例尺（mm/px）", 2.0, 0.5, 5.0, 0.1),
    ],
    tasks=[
        task("dev", "加前向后向校验", "从 B 再跟踪回 A，丢弃往返误差大于 1 px 的点，比较跟踪数量。"),
        task("dev", "估计旋转", "用位移场的左右差异估计 yaw rate，输出 rad/s。"),
        task("observe", "把帧顺序反过来", "用 B 跟踪 A，观察 dx 的符号，解释和机器人运动方向的关系。"),
    ],
    quiz_items=[
        quiz("为什么选角点而不是平坦区域？", ["更快", "平坦区域位移不可解", "颜色更亮", "角点更大"], 1,
             "平坦区域各方向梯度都小，LK 方程欠定。"),
        quiz("中位数比平均值稳，是因为？", ["计算快", "抵抗离群点", "更准确", "不需要排序"], 1,
             "少量错配会产生极端值，中位数不受影响。"),
        quiz("没有比例尺，光流能给出？", ["米/秒", "像素/秒", "角度", "距离"], 1,
             "像素位移需要比例尺才能变成物理单位。"),
    ],
    industry="光流用于无人机悬停、视觉里程计、运动目标跟踪、视频稳像。现代系统常把稀疏光流和 IMU 预积分、轮速融合；深度学习光流（RAFT）在复杂场景更强，但算力更高。",
    career="开发型岗位要处理跟踪丢失、时间同步、比例尺标定；调控型岗位要会看跟踪点分布，判断是纹理不足、曝光过度还是运动太快。",
    next_step="机器人视觉的五个典型任务到这里。下一章进入控制与工程：串口协议、状态机、调试与测试。",
)

CHAPTER = chapter(
    "robot", "03", "机器人视觉实战",
    "循迹、分拣、对接、标定、光流：把 OpenCV 接到真实机器人任务上。",
    [L1, L2, L3, L4, L5],
    color="#fbbf24", icon="03",
)
