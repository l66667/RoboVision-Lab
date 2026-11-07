# -*- coding: utf-8 -*-
"""第五章：结课项目。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, seg, param, test, task, quiz, target, lesson, chapter,
)

L1 = lesson(
    "capstone-cell",
    "结课项目：搭一个完整的智能分拣站",
    "视觉标定 → 多目标检测 → 抓取规划 → 串口指令 → 状态机节拍",
    chapter="capstone",
    mode="vision",
    sample="workcell.jpg",
    difficulty=5,
    minutes=90,
    tags=["项目", "集成", "节拍"],
    objectives=[
        "把单应性标定、颜色检测、坐标变换串成一条稳定流水线",
        "生成带 CRC 的机械臂指令，并验证每一帧都能被解析",
        "用状态机估算节拍，输出可交付的检测报告与指标",
    ],
    concept=[
        P("这一课不再引入新算法，而是把前面学的东西接成一个「能交付」的系统。真实项目和课堂练习最大的差别是：接口要稳定、失败要能看见、指标要能复现。"),
        TABLE(
            ["模块", "输入", "输出", "本课实现"],
            [
                ["标定", "四个角标像素", "单应矩阵 H", "四角色标 + getPerspectiveTransform"],
                ["检测", "工作台图像", "物块颜色/像素/毫米/角度", "HSV 多色 + 轮廓 + minAreaRect"],
                ["规划", "物块列表", "抓取顺序 + 料框", "行优先排序 + 颜色分箱"],
                ["通信", "位姿/动作", "带 CRC 的串口帧", "encode_frame + parse_stream"],
                ["控制", "指令序列", "节拍/状态日志", "状态机 + 时间预算"],
            ],
        ),
        H("交付前必须回答的四个问题"),
        UL(
            "**精度**：像素→毫米的误差有多大？角标是否覆盖工作区？",
            "**节拍**：一个完整循环多少秒？瓶颈在抓取、移动还是视觉？",
            "**鲁棒性**：少一个物块、颜色误判、CRC 错时，系统怎么表现？",
            "**可维护性**：参数在配置文件里吗？日志能复现现场吗？",
        ),
        NOTE("安全边界", "真实工作站还要有急停、光栅、碰撞检测、力控和权限管理。本课只做视觉与指令层，不能直接驱动真实机械臂。", "warn"),
    ],
    walkthrough=[
        seg(
            "标定工作台",
            r'''
import cv2
import json
import os
import struct
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
magenta = cv2.inRange(hsv, np.array([140, 120, 100]),
                      np.array([170, 255, 255]))
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
mapped = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2)
calib_error = float(np.sqrt(np.mean(np.sum((mapped - dst) ** 2, axis=1))))
print("角标:", len(tabs), " 重投影误差: %.2f mm" % calib_error)
metric("标定误差(mm)", round(calib_error, 2))
''',
            "和分拣课一样，四角标 → 排序 → 单应矩阵。把四个角标像素用 H 映射回毫米，与已知坐标比较，得到标定残差；这个数比「H 长什么样」更有意义。",
            "真实项目会把 H 和角标像素一起存档；相机一动，H 就失效。",
        ),
        seg(
            "检测并换算所有物块",
            r'''
COLOR_RANGES = {
    "red": [((0, 150, 120), (10, 255, 255)),
            ((170, 150, 120), (180, 255, 255))],
    "green": [((35, 100, 60), (85, 255, 255))],
    "blue": [((90, 100, 60), (130, 255, 255))],
    "yellow": [((20, 120, 120), (35, 255, 255))],
}
blocks = []
for color_name, ranges in COLOR_RANGES.items():
    mask = np.zeros(image.shape[:2], np.uint8)
    for low, high in ranges:
        mask |= cv2.inRange(hsv, np.array(low), np.array(high))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        if cv2.contourArea(c) < 700:
            continue
        M = cv2.moments(c)
        px = np.array([[[M["m10"] / M["m00"], M["m01"] / M["m00"]]]], np.float32)
        mm = cv2.perspectiveTransform(px, H)[0, 0]
        rect = cv2.minAreaRect(c)
        (_, _), (rw, rh), angle = rect
        grab_angle = (angle if rw >= rh else angle + 90) % 180
        blocks.append({"color": color_name, "px": px[0, 0].copy(),
                       "mm": mm, "angle": grab_angle})
blocks.sort(key=lambda b: (round(b["mm"][1] / 50), b["mm"][0]))
for i, b in enumerate(blocks):
    b["seq"] = i + 1
print("物块:", len(blocks), [b["color"] for b in blocks])
metric("物块数量", len(blocks))
''',
            "每种颜色单独检测，再统一做透视变换。排序用「毫米 y 分带 + x」，保证机械臂从近到远、从左到右。角度按长边归一化。",
        ),
        seg(
            "生成带 CRC 的指令",
            r'''
def crc16_modbus(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc & 0xFFFF

HEADER = b"\xAA\x55"
def encode_frame(cmd, payload=b""):
    body = bytes([len(payload), cmd]) + payload
    return HEADER + body + struct.pack("<H", crc16_modbus(body))

BINS = {"red": (100, 540), "green": (300, 540),
        "blue": (500, 540), "yellow": (700, 540)}
commands = []
for b in blocks:
    x, y, a = float(b["mm"][0]), float(b["mm"][1]), float(b["angle"])
    bx, by = BINS[b["color"]]
    commands.append(encode_frame(0x10, struct.pack("<fff", x, y, a)))
    commands.append(encode_frame(0x20, b"\x01"))
    commands.append(encode_frame(0x10, struct.pack("<fff", bx, by, 0.0)))
    commands.append(encode_frame(0x20, b"\x00"))
print("指令帧数:", len(commands), "总字节:", sum(len(c) for c in commands))
metric("指令帧数", len(commands))
''',
            "每个物块四帧：移动到抓取位姿、开吸盘、移动到料框、关吸盘。`0x10` 携带 3 个 float，`0x20` 携带 1 字节开关。所有帧都带 CRC，接收方能丢弃坏帧。",
            "真实协议还要有坐标单位、速度、加速度、夹爪开度；这里用最小字段演示链路。",
        ),
        seg(
            "验证协议与节拍",
            r'''
def parse_stream(buffer):
    frames = []
    while True:
        start = buffer.find(HEADER)
        if start < 0:
            return frames, b""
        buffer = buffer[start:]
        if len(buffer) < 4:
            return frames, buffer
        total = 6 + buffer[2]
        if len(buffer) < total:
            return frames, buffer
        frame = buffer[:total]
        body = frame[2:4 + buffer[2]]
        crc_recv = struct.unpack("<H", frame[4 + buffer[2]:6 + buffer[2]])[0]
        if crc16_modbus(body) == crc_recv:
            frames.append({"cmd": frame[3], "payload": frame[4:4 + buffer[2]]})
            buffer = buffer[total:]
        else:
            buffer = buffer[1:]

crc_ok = 0
for frame in commands:
    parsed, rest = parse_stream(frame)
    if len(parsed) == 1 and rest == b"":
        crc_ok += 1
print("CRC/解析通过:", crc_ok, "/", len(commands))

pick_time = float(p["pick_time"])
T_APPROACH, T_PLACE, T_HOME = 1.2, 1.5, 0.6
state_log = []
for b in blocks:
    for state, duration in [("APPROACH", T_APPROACH),
                            ("PICK", pick_time),
                            ("PLACE", T_PLACE),
                            ("HOME", T_HOME)]:
        state_log.append({"seq": b["seq"], "state": state, "seconds": duration})
cycle_time = len(blocks) * (T_APPROACH + pick_time + T_PLACE + T_HOME)
print("预计节拍: %.1f s" % cycle_time)
metric("CRC通过", crc_ok)
metric("预计节拍(s)", round(cycle_time, 1))
''',
            "把生成的每一帧再喂给解析器，形成「编码→解码」闭环测试。节拍按每个物块四段动作累加；真实节拍要用 `time.perf_counter` 在产线上测，不能只靠估算。",
        ),
        seg(
            "生成交付报告",
            r'''
vis = image.copy()
for b in blocks:
    x, y = int(b["px"][0]), int(b["px"][1])
    cv2.circle(vis, (x, y), 18, (255, 255, 255), 2)
    cv2.putText(vis, "%d %s" % (b["seq"], b["color"]), (x - 40, y - 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

H_inv = np.linalg.inv(H)
bin_pts = np.array([BINS[b["color"]] for b in blocks], np.float32).reshape(-1, 1, 2)
bin_px = cv2.perspectiveTransform(bin_pts, H_inv).reshape(-1, 2)
for b, target_px in zip(blocks, bin_px):
    cv2.arrowedLine(vis, tuple(b["px"].astype(int)), tuple(target_px.astype(int)),
                    (120, 220, 120), 2, tipLength=0.04)
cv2.putText(vis, "blocks=%d  crc=%d/%d  cycle=%.1fs" % (
            len(blocks), crc_ok, len(commands), cycle_time),
            (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

panel = np.full((800, 460, 3), 18, np.uint8)
cv2.putText(panel, "CELL REPORT", (24, 46), cv2.FONT_HERSHEY_SIMPLEX,
            0.9, (235, 235, 235), 2, cv2.LINE_AA)
cv2.putText(panel, "calib residual: %.2f mm" % calib_error, (24, 86),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 220, 255), 1, cv2.LINE_AA)
for i, b in enumerate(blocks):
    yy = 130 + i * 38
    cv2.putText(panel, "#%d %-6s x=%5.1f y=%5.1f a=%4.1f" % (
                b["seq"], b["color"], b["mm"][0], b["mm"][1], b["angle"]),
                (24, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1, cv2.LINE_AA)
cv2.putText(panel, "cycle = %.1f s" % cycle_time, (24, 730),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 230, 160), 2, cv2.LINE_AA)
result = np.hstack([vis, panel])
metric("标定误差(mm)", round(calib_error, 2))
''',
            "左侧是检测与抓取路径，右侧是交付报告：物块序号、颜色、毫米坐标、角度、标定残差和节拍。这张图可以直接贴进实验报告或项目复盘。",
            "真实交付还要加：版本号、相机序列号、标定日期、操作员、失败样本截图。",
        ),
    ],
    tests=[
        test("至少五个物块", "len(blocks) >= 5"),
        test("所有指令可解析", "crc_ok == len(commands)"),
        test("节拍在目标内", "cycle_time < 30"),
        test("报告图已生成", "result.ndim == 3 and result.shape[0] > 0"),
    ],
    params=[
        param("pick_time", "单次抓取耗时（秒）", 0.8, 0.4, 3.0, 0.1),
    ],
    tasks=[
        task("dev", "加一个失败分支", "模拟第 3 个物块抓取失败：跳过它的剩余指令，记录 ERROR，并重算节拍。"),
        task("dev", "输出项目报告", "把 blocks、cycle_time、crc_ok、K/H 写入 `work_dir/report.json`。"),
        task("tune", "读代码改接口", "只改 `cmds` 里的一个字段（例如给抓取指令加 `seq`），保证原有测试仍通过，并写出 diff 说明。"),
        task("observe", "改料框布局", "把料框改到 y=300 的一排，观察箭头和节拍是否变化，说明布局对节拍的影响。"),
    ],
    quiz_items=[
        quiz("单应矩阵的条件数过大说明？", ["标定很准", "四点几何差/接近共线", "图像太亮", "CRC 错"], 1,
             "条件数大表示方程病态，H 对噪声敏感。"),
        quiz("每个物块四帧的作用是？", ["冗余", "移动/开吸盘/移动/关吸盘", "四种颜色", "四个相机"], 1,
             "两帧位姿 + 两帧执行器开关。"),
        quiz("节拍估算和实测不一致时，先看？", ["颜色", "每段动作的真实耗时和等待", "分辨率", "CRC"], 1,
             "估算通常漏掉通信、等待、加减速和异常重试。"),
    ],
    industry="智能分拣站是机器人工程的典型集成项目：相机标定、视觉检测、坐标变换、机械臂通信、状态机、节拍优化、安全互锁。FAT/SAT 验收时看的就是精度、节拍、良率和稳定性。",
    career="开发型岗位负责模块接口、协议、回归测试；调控型岗位负责现场标定、光照、料框布局、误抓分析和节拍瓶颈。把这一课的报告整理进作品集，就是一份能讲清楚的项目经历。",
    target_spec=target("预计节拍(s)", "<=", 26, "默认参数下整站节拍不超过 26 秒"),
    next_step="课程到这里结束。回到「学习路线」页，按 12 周计划复习，或直接做自己的项目。",
)

CHAPTER = chapter(
    "capstone", "05", "结课项目",
    "把标定、检测、规划、通信、状态机接成一个可交付的智能分拣站。",
    [L1],
    color="#fb7185", icon="05",
)
