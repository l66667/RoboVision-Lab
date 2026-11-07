# -*- coding: utf-8 -*-
"""第六章：Halcon 与手眼引导（初步）。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "halcon-intro",
    "Halcon 入门：从 Region 到 Blob 分析",
    "HDevelop 语法、区域/元组、阈值+连通+特征筛选，以及 OpenCV 对照实现",
    chapter="halcon",
    mode="vision",
    sample="parts.jpg",
    difficulty=2,
    minutes=35,
    tags=["Halcon", "Blob", "Region"],
    objectives=[
        "看懂 HDevelop 的 tuple / region / operator 写法",
        "把 Halcon 的 threshold→connection→select_shape→area_center 映射到 OpenCV",
        "输出每个目标的面积与质心，作为抓取候选",
    ],
    concept=[
        P("Halcon 是机器视觉里最常见的商业库之一，强项是 Blob 分析、模板匹配、标定、测量和手眼引导。它的代码运行在 HDevelop 里，部署时通过 HDevEngine、C#、C++ 或 Python 接口调用。"),
        TABLE(
            ["概念", "Halcon", "OpenCV / Python"],
            [
                ["图像", "HObject（Image）", "numpy.ndarray"],
                ["区域", "Region（像素集合）", "掩膜 / 轮廓点集"],
                ["数组", "Tuple（可混合类型）", "list / ndarray"],
                ["连通域", "connection", "findContours / connectedComponents"],
                ["特征筛选", "select_shape", "按 area/bbox/circularity 过滤"],
                ["质心", "area_center", "cv2.moments"],
            ],
        ),
        CODE(
            """* HDevelop 的典型 Blob 流程
read_image (Image, 'parts')
rgb1_to_gray (Image, Gray)
threshold (Gray, Region, 0, 120)
connection (Region, Connected)
select_shape (Connected, Selected, 'area', 'and', 500, 20000)
area_center (Selected, Area, Row, Column)
* Row 是行(y)，Column 是列(x)""",
            "halcon",
        ),
        NOTE("Halcon 不是免费的", "学习阶段可以先用 30 天试用版或学校授权；没有授权时，用本课的 Python 对照代码理解同一套流程。HDevelop 代码在本软件里只展示、不执行。", "warn"),
        P("Halcon 的 `Row, Column` 对应图像的 `y, x`，和 OpenCV 的 `x, y` 相反。手眼引导时这个顺序错一次，机械臂就会抓到画面外。"),
    ],
    walkthrough=[
        seg(
            "用饱和度把彩色目标从灰底中分离",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([0, 80, 40]), np.array([180, 255, 255]))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
capture("彩色区域掩膜", mask)
print("前景像素:", int(mask.sum() // 255))
''',
            "Halcon 常用 `threshold` 做灰度分割；彩色目标更适合在 HSV 里按饱和度分割。先开运算去噪，再闭运算补洞，和 Halcon 的 `opening_circle` / `closing_circle` 思路一致。",
        ),
        seg(
            "找连通域并筛面积",
            r'''
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
objects = []
for c in contours:
    area = float(cv2.contourArea(c))
    if area < 500:
        continue
    M = cv2.moments(c)
    if M["m00"] == 0:
        continue
    objects.append({
        "area": area,
        "cx": M["m10"] / M["m00"],
        "cy": M["m01"] / M["m00"],
        "contour": c,
    })
print("目标数:", len(objects))
metric("目标数", len(objects))
''',
            "`findContours(RETR_EXTERNAL)` 对应 Halcon 的 `connection`；按面积过滤对应 `select_shape('area')`。`moments` 的 `m10/m00`、`m01/m00` 就是 `area_center` 返回的 Column/Row。",
            "Halcon 的 select_shape 可以用多个特征组合；OpenCV 里就自己写条件，或先算特征再过滤。",
        ),
        seg(
            "按面积排序并画质心",
            r'''
objects.sort(key=lambda o: o["area"], reverse=True)
result = image.copy()
for i, obj in enumerate(objects):
    x, y = int(obj["cx"]), int(obj["cy"])
    cv2.drawContours(result, [obj["contour"]], -1, (80, 220, 160), 2)
    cv2.circle(result, (x, y), 5, (0, 220, 255), -1)
    cv2.putText(result, str(i + 1), (x + 8, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
''',
            "把面积从大到小排序，编号稳定，方便和 PLC/机械臂的抓取顺序对应。Halcon 里对应 `tuple_sort` 或 `select_shape` 后按 `Area` 排序。",
        ),
        seg(
            "输出抓取候选表",
            r'''
for i, obj in enumerate(objects[:8]):
    print("#%d area=%.0f  row=%.1f  col=%.1f" % (
        i + 1, obj["area"], obj["cy"], obj["cx"]))
metric("最大面积", round(max(o["area"] for o in objects), 1))
metric("平均面积", round(sum(o["area"] for o in objects) / len(objects), 1))
''',
            "工业上不会只打印；会把 `(row, col, area, score)` 组成结构体，交给手眼变换或机器人接口。面积可以用来过滤噪声和判断目标规格。",
        ),
        seg(
            "Halcon → OpenCV 对照",
            r'''
print("Halcon: threshold -> connection -> select_shape -> area_center")
print("OpenCV: inRange -> findContours -> area filter -> moments")
print("注意：Halcon 的 Row/Column 对应 OpenCV 的 y/x。")
''',
            "记住这条映射，读 Halcon 项目时就能快速翻译成 Python 原型；反过来，把 Python 原型交给 Halcon 工程师，也知道该用哪些算子。",
        ),
    ],
    tests=[
        test("至少 10 个目标", "len(objects) >= 10"),
        test("面积都超过 500", "all(o['area'] >= 500 for o in objects)"),
        test("结果图尺寸不变", "result.shape == image.shape"),
    ],
    tasks=[
        task("dev", "只保留圆形", "用轮廓的圆度（4πA/P²）过滤，输出圆度 > 0.8 的目标数量。"),
        task("dev", "写 Halcon 伪代码", "把本课流程写成 6 行 HDevelop 伪代码，标出 Row/Column 与 x/y 的对应。"),
        task("observe", "改面积下限", "把 500 改成 3000，观察目标数和最大面积的变化。"),
    ],
    quiz_items=[
        quiz("Halcon 的 area_center 返回的 Row 对应 OpenCV 的？", ["x", "y", "通道", "面积"], 1,
             "Row 是行号，对应 y；Column 对应 x。"),
        quiz("connection 最接近 OpenCV 的哪个操作？", ["cvtColor", "findContours", "resize", "Canny"], 1,
             "connection 把二值区域拆成连通域，OpenCV 用 findContours/connectedComponents。"),
        quiz("select_shape 的作用？", ["改变颜色", "按面积/形状等特征筛选区域", "缩放图像", "保存图片"], 1,
             "按特征过滤区域，是 Blob 分析的核心。"),
    ],
    industry="Halcon 在 3C 制造、半导体、医药、汽车零部件检测里非常常见；很多产线软件就是 HDevelop 流程 + C# 界面 + 运动控制卡。会 Halcon 不等于会视觉，但它是视觉应用开发的重要工具。",
    career="视觉应用开发岗位要能把 Halcon 流程、标定、手眼和机器人接口串起来；调控岗位要会调阈值、形态学、特征区间和节拍。",
    next_step="下一课进入手眼标定：把相机坐标变成机器人坐标。",
)

L2 = lesson(
    "hand-eye-calib",
    "手眼标定：AX=XB 到底在解什么",
    "eye-in-hand / eye-to-hand、calibrateHandEye、合成数据验证与误差指标",
    chapter="halcon",
    difficulty=5,
    minutes=55,
    tags=["手眼标定", "AX=XB", "标定"],
    objectives=[
        "说清 eye-in-hand 与 eye-to-hand 的坐标链",
        "用合成数据跑通 cv2.calibrateHandEye，并验证平移/旋转误差",
        "知道 Halcon calibrate_hand_eye 的输入输出与本课代码的对应关系",
    ],
    concept=[
        P("手眼标定回答：相机看到的点，怎么变到机器人基坐标？核心方程是 AX=XB：机器人动一次，相机也动一次，两个相对变换必须闭合。"),
        TABLE(
            ["安装方式", "相机在哪", "典型场景", "标定目标"],
            [
                ["eye-in-hand", "固定在机械臂末端", "抓取、随臂移动", "T_cam2gripper"],
                ["eye-to-hand", "固定在支架/工作台", "分拣、传送带", "T_cam2base"],
            ],
        ),
        FORMULA("T_base_target = T_base_gripper · T_gripper_camera · T_camera_target", "eye-in-hand 坐标链"),
        CODE(
            """* Halcon 的典型手眼流程
calibrate_cameras (CalibDataID, Errors)
calibrate_hand_eye (CalibDataID, Errors)
get_calib_data (CalibDataID, 'camera', 0, 'params', CamParam)
* 之后用 affine_trans_point_3d 把相机点变到机器人坐标""",
            "halcon",
        ),
        NOTE("标定不是一次性的", "换镜头、动相机支架、碰撞、温度漂移都可能让标定失效。工业项目要保存标定日期、RMS、验证点，并定期复标。", "warn"),
    ],
    walkthrough=[
        seg(
            "齐次变换与求逆",
            r'''
import cv2
import numpy as np

def make_T(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = np.asarray(t).reshape(3)
    return T

def inv_T(T):
    R, t = T[:3, :3], T[:3, 3]
    out = np.eye(4)
    out[:3, :3] = R.T
    out[:3, 3] = -R.T @ t
    return out

print("齐次矩阵 4x4：旋转 + 平移")
''',
            "三维位姿用 4×4 齐次矩阵表示：左上 3×3 是旋转，右上 3×1 是平移。求逆不是简单转置，平移要一起变：`-Rᵀt`。",
        ),
        seg(
            "设定真值并生成机器人位姿",
            r'''
rng = np.random.default_rng(3)
R_x, _ = cv2.Rodrigues(np.array([0.0, 0.35, 0.0]))
X = make_T(R_x, [0.03, -0.02, 0.08])          # 真相机→夹爪
R_t, _ = cv2.Rodrigues(np.array([0.1, 0.2, 0.05]))
T_base_target = make_T(R_t, [0.5, 0.1, 0.2])  # 固定目标

R_g2b, t_g2b, R_t2c, t_t2c = [], [], [], []
for _ in range(15):
    rvec = rng.uniform(-0.5, 0.5, 3)
    R, _ = cv2.Rodrigues(rvec)
    t = rng.uniform(-0.2, 0.2, 3) + np.array([0.4, 0.0, 0.3])
    T_base_g = make_T(R, t)
    # 由真值反推：目标在相机里的位姿
    T_cam_t = inv_T(T_base_g @ X) @ T_base_target
    R_g2b.append(R)
    t_g2b.append(t.reshape(3, 1))
    R_t2c.append(T_cam_t[:3, :3])
    t_t2c.append(T_cam_t[:3, 3].reshape(3, 1))
print("样本数:", len(R_g2b))
metric("样本数", len(R_g2b))
''',
            "真实标定里这些位姿由机器人控制器和标定板检测给出；这里用已知 X 反推，方便验证算法是否真的能恢复 X。15 组位姿要覆盖不同旋转，否则方程欠约束。",
        ),
        seg(
            "调用 calibrateHandEye",
            r'''
R_c2g, t_c2g = cv2.calibrateHandEye(
    R_g2b, t_g2b, R_t2c, t_t2c,
    method=cv2.CALIB_HAND_EYE_TSAI)
print("R_c2g=\n", np.round(R_c2g, 4))
print("t_c2g=", np.round(t_c2g.ravel(), 4))
''',
            "OpenCV 的输入顺序是 gripper→base、target→camera，输出 camera→gripper。Halcon 的 `calibrate_hand_eye` 也是同样的几何问题，只是数据容器和坐标系命名不同。",
        ),
        seg(
            "计算误差",
            r'''
t_error = float(np.linalg.norm(t_c2g.ravel() - X[:3, 3]))
cos_angle = (np.trace(R_c2g.T @ X[:3, :3]) - 1) / 2
r_error = float(np.degrees(np.arccos(np.clip(cos_angle, -1, 1))))
print("平移误差: %.5f m" % t_error)
print("旋转误差: %.5f deg" % r_error)
metric("平移误差(m)", round(t_error, 5))
metric("旋转误差(deg)", round(r_error, 5))
''',
            "标定结果不能只看“跑通了”，要看误差。真实项目里平移误差和旋转误差要结合抓取公差；比如 ±2 mm、±1° 是否够用。",
        ),
        seg(
            "画一张坐标链示意",
            r'''
canvas = np.full((420, 960, 3), 18, np.uint8)
points = {"BASE": (110, 300), "GRIPPER": (330, 210), "CAMERA": (500, 210), "TARGET": (760, 300)}
for name, (x, y) in points.items():
    cv2.circle(canvas, (x, y), 26, (80, 220, 160), 2)
    cv2.putText(canvas, name, (x - 28, y + 48), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (230, 230, 230), 2, cv2.LINE_AA)
for a, b in (("BASE", "GRIPPER"), ("GRIPPER", "CAMERA"), ("CAMERA", "TARGET")):
    cv2.arrowedLine(canvas, points[a], points[b], (120, 200, 255), 2, tipLength=0.06)
cv2.putText(canvas, "eye-in-hand: base -> gripper -> camera -> target",
            (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), 2, cv2.LINE_AA)
result = canvas
''',
            "手眼引导不是“把像素乘一个比例”，而是沿坐标链做矩阵乘法。把链画出来，检查每一段的方向和单位，是现场最有效的排错方法。",
        ),
    ],
    tests=[
        test("样本数足够", "len(R_g2b) == 15"),
        test("平移误差小于 1mm", "t_error < 0.001"),
        test("旋转误差小于 0.1 度", "r_error < 0.1"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    tasks=[
        task("dev", "加噪声", "给 R_t2c/t_t2c 加 0.2° 和 0.5 mm 噪声，观察误差变化。"),
        task("dev", "换方法", "把 method 改成 CALIB_HAND_EYE_PARK 或 HORAUD，比较误差。"),
        task("observe", "减少位姿", "只用 3 组位姿，观察误差是否稳定，并解释为什么。"),
    ],
    quiz_items=[
        quiz("eye-in-hand 的相机固定在哪？", ["机器人基座", "机械臂末端", "工作台", "传送带"], 1,
             "相机随末端一起动，标定 T_cam2gripper。"),
        quiz("AX=XB 描述的是什么？", ["图像缩放", "两个相对变换的闭环", "相机内参", "电机电流"], 1,
             "机器人动一次、相机动一次，两条路径必须得到同一个目标位姿。"),
        quiz("手眼标定后，像素点要经过什么才能变机器人坐标？", ["只乘比例尺", "相机内参/畸变 + 手眼矩阵", "只做灰度化", "只做阈值"], 1,
             "先由相机模型得到相机坐标，再乘手眼变换到机器人坐标。"),
    ],
    industry="手眼引导是抓取、装配、涂胶、焊接的核心。Halcon 的 calibrate_hand_eye、OpenCV 的 calibrateHandEye、机器人厂商的 hand-eye 向导，底层都是 AX=XB。",
    career="视觉应用开发要能设计标定流程、验证误差、把结果接进机器人；调控岗位要会复标、检查验证点、判断漂移。",
    next_step="下一课把 Blob、单应性和抓取位姿串成一条 Halcon 风格的 Pick 流程。",
)

L3 = lesson(
    "halcon-pick",
    "Halcon 风格 Pick：从 Blob 到抓取位姿",
    "标定四角、颜色 Blob、像素→毫米、抓取角、抓取顺序",
    chapter="halcon",
    mode="vision",
    sample="workcell.jpg",
    difficulty=4,
    minutes=50,
    tags=["Halcon", "Pick", "手眼引导"],
    objectives=[
        "用四角标建立像素→工作台毫米的单应矩阵",
        "把颜色 Blob 转成 (x, y, angle) 抓取位姿",
        "按行优先规划抓取顺序，并输出 Halcon 风格的算子映射",
    ],
    concept=[
        P("Halcon 的 Pick 流程通常是：采集 → 标定 → Blob/模板 → 位姿 → 手眼 → 机器人。算子看起来多，但每一步都能在 OpenCV/Python 里找到对应实现。"),
        CODE(
            """* Halcon 风格 Pick（伪代码）
read_image (Image, 'workcell')
* 1) 找标定点/标定板，得到像素->毫米的变换
vector_to_hom_mat2d (PX, PY, MX, MY, HomMat2D)
* 2) Blob 分割 + 特征筛选
threshold (Image, Region, 0, 120)
connection (Region, Connected)
select_shape (Connected, Blocks, 'area', 'and', 700, 50000)
* 3) 位姿：质心 + 方向
area_center (Blocks, Area, Row, Column)
orientation_region (Blocks, Phi)
* 4) 像素->毫米，再手眼->机器人
affine_trans_point_2d (HomMat2D, Column, Row, X, Y)
* 5) 发给机器人 (X, Y, Phi, ...)""",
            "halcon",
        ),
        FORMULA("p_mm = H · p_px", "平面单应；三维场景要再乘手眼矩阵"),
        NOTE("角度定义要统一", "Halcon 的 orientation_region、OpenCV 的 minAreaRect、机器人控制器的欧拉角，三套角度定义可能不同。接机器人前必须用同一个基准和旋转方向验证。", "warn"),
    ],
    walkthrough=[
        seg(
            "找四角标并求单应矩阵",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
magenta = cv2.inRange(hsv, np.array([140, 120, 100]), np.array([170, 255, 255]))
magenta = cv2.morphologyEx(magenta, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
cnts, _ = cv2.findContours(magenta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:4]
tabs = []
for c in cnts:
    if cv2.contourArea(c) < 1500:
        continue
    M = cv2.moments(c)
    tabs.append((M["m10"] / M["m00"], M["m01"] / M["m00"]))
pts = np.array(tabs, np.float32)
s, d = pts.sum(axis=1), pts[:, 0] - pts[:, 1]
src = np.array([pts[np.argmin(s)], pts[np.argmax(d)],
                pts[np.argmax(s)], pts[np.argmin(d)]], np.float32)
dst = np.array([[35, 35], [765, 35], [765, 565], [35, 565]], np.float32)
H = cv2.getPerspectiveTransform(src, dst)
print("角标数:", len(tabs))
metric("角标数", len(tabs))
''',
            "四角标是像素→毫米的锚点。Halcon 里对应 `vector_to_hom_mat2d`；OpenCV 用四对点 `getPerspectiveTransform`。角标要覆盖工作区，别都挤在一角。",
        ),
        seg(
            "颜色 Blob + 位姿",
            r'''
COLORS = {
    "red": [((0, 150, 120), (10, 255, 255)), ((170, 150, 120), (180, 255, 255))],
    "green": [((35, 100, 60), (85, 255, 255))],
    "blue": [((90, 100, 60), (130, 255, 255))],
    "yellow": [((20, 120, 120), (35, 255, 255))],
}
blocks = []
for color, ranges in COLORS.items():
    mask = np.zeros(image.shape[:2], np.uint8)
    for lo, hi in ranges:
        mask |= cv2.inRange(hsv, np.array(lo), np.array(hi))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        if cv2.contourArea(c) < 700:
            continue
        M = cv2.moments(c)
        px = np.array([[[M["m10"] / M["m00"], M["m01"] / M["m00"]]]], np.float32)
        mm = cv2.perspectiveTransform(px, H)[0, 0]
        (_, _), (w, h), angle = cv2.minAreaRect(c)
        blocks.append({"color": color, "px": px[0, 0], "mm": mm,
                       "angle": (angle if w >= h else angle + 90) % 180})
print("物块:", len(blocks))
metric("物块数", len(blocks))
''',
            "颜色分割对应 Halcon 的 threshold/select_shape；`minAreaRect` 给出方向，对应 `orientation_region`。抓取角要按长边归一化，否则夹爪会转 90°。",
        ),
        seg(
            "排序与料框分配",
            r'''
blocks.sort(key=lambda b: (round(b["mm"][1] / 50), b["mm"][0]))
BINS = {"red": (100, 540), "green": (300, 540),
        "blue": (500, 540), "yellow": (700, 540)}
for i, b in enumerate(blocks):
    b["seq"] = i + 1
    b["bin"] = BINS[b["color"]]
    print("#%d %-6s mm=(%5.1f,%5.1f) angle=%5.1f -> %s"
          % (b["seq"], b["color"], b["mm"][0], b["mm"][1], b["angle"], b["bin"]))
''',
            "行优先排序让机械臂从近到远、从左到右，减少空行程。料框坐标是工艺布局，通常从配置文件读，不应写死在视觉脚本里。",
        ),
        seg(
            "画抓取结果",
            r'''
result = image.copy()
H_inv = np.linalg.inv(H)
for b in blocks:
    x, y = int(b["px"][0]), int(b["px"][1])
    cv2.circle(result, (x, y), 18, (255, 255, 255), 2)
    cv2.putText(result, "%d %s" % (b["seq"], b["color"]), (x - 36, y - 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
    target = cv2.perspectiveTransform(
        np.array([[b["bin"]]], np.float32), H_inv)[0, 0]
    cv2.arrowedLine(result, (x, y), tuple(target.astype(int)),
                    (120, 220, 120), 2, tipLength=0.04)
''',
            "把抓取点、颜色、序号和料框方向画出来，现场一眼就能核对“抓哪个、放哪里”。Halcon 里会用 `dev_display` + `disp_arrow` 做同样的可视化。",
        ),
        seg(
            "输出给机器人",
            r'''
pose = [{"x": round(float(b["mm"][0]), 1),
         "y": round(float(b["mm"][1]), 1),
         "angle": round(float(b["angle"]), 1),
         "bin": b["bin"]} for b in blocks]
print("robot poses:", pose[:3])
metric("抓取顺序", " -> ".join(b["color"] for b in blocks))
''',
            "实际接口可能是 JSON、TCP、Modbus 或 ROS2 action。先定义字段和单位（mm/度），再做协议；不要到现场才发现一边用米、一边用毫米。",
        ),
    ],
    tests=[
        test("四个角标", "len(tabs) == 4"),
        test("至少五个物块", "len(blocks) >= 5"),
        test("毫米坐标在工作台内", "all(0 <= b['mm'][0] <= 800 and 0 <= b['mm'][1] <= 600 for b in blocks)"),
        test("抓取位姿非空", "len(pose) == len(blocks) and all('angle' in p for p in pose)"),
    ],
    tasks=[
        task("dev", "按颜色优先级排序", "改成红→黄→蓝→绿，再按 y 排序，打印新的抓取序列。"),
        task("dev", "加置信度", "给每个物块加一个 0–1 的 score（面积/最大面积），低于阈值的不抓。"),
        task("observe", "把 H 用反", "交换 H 和 H_inv，观察毫米坐标和箭头如何变化。"),
    ],
    quiz_items=[
        quiz("Halcon 的 orientation_region 最接近 OpenCV 的？", ["cvtColor", "minAreaRect 的角度", "Canny", "resize"], 1,
             "两者都给出区域的主方向，但角度定义要核对。"),
        quiz("像素→毫米需要几对点？", ["2", "3", "4", "8"], 2,
             "平面单应 8 个自由度，需要 4 对点。"),
        quiz("抓取顺序为什么要排序？", ["好看", "减少空行程/节拍", "改变颜色", "增大分辨率"], 1,
             "合理的抓取顺序能减少机械臂移动距离和节拍。"),
    ],
    industry="Halcon + 手眼 + 机器人接口是 3C、汽车零部件、医药分拣的典型组合。真正的难点是标定、角度定义、节拍和异常处理，而不是单个算子。",
    career="视觉应用开发要能把 Blob/模板/标定/手眼接到机器人；调控岗位要会检查角标、角度方向、抓取顺序和误抓。",
    next_step="视觉应用线先到这里。下一章进入电机与运动控制：FOC、EtherCAT、驱控一体。",
)

CHAPTER = chapter(
    "halcon", "06", "Halcon 与手眼引导",
    "商业视觉库的工作方式、手眼标定 AX=XB，以及从 Blob 到抓取位姿的完整链路。",
    [L1, L2, L3],
    color="#38bdf8", icon="06",
)
