# -*- coding: utf-8 -*-
"""第四章：控制、通信与工程化。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, seg, param, test, task, quiz, target, lesson, chapter,
)

L1 = lesson(
    "ctrl-serial",
    "串口协议：让视觉和底盘说同一种语言",
    "帧头、长度、命令、CRC16、分包粘包与噪声",
    chapter="engineer",
    difficulty=4,
    minutes=50,
    tags=["串口", "CRC", "协议"],
    objectives=[
        "设计一个带帧头、长度、命令、CRC 的二进制帧",
        "用 struct/bytes 编码，处理小端序和十六进制显示",
        "写一个能处理分包、粘包、噪声和坏 CRC 的流式解析器",
    ],
    concept=[
        P("视觉程序算出目标坐标后，要把结果发给底盘/机械臂。串口是 UART 字节流，没有消息边界；如果直接发 `x,y`，接收方不知道一帧从哪开始、到哪结束，噪声一来就全乱。所以需要协议：帧头 + 长度 + 命令 + 数据 + 校验。"),
        FORMULA("AA 55 | LEN | CMD | PAYLOAD(LEN) | CRC16(LE)", "本课协议"),
        H("为什么用 CRC 而不是简单求和"),
        P("累加和挡不住字节顺序错误、双比特翻转等常见错误。CRC16 用多项式除法生成 16 位校验，检错能力强得多，计算也足够快。Modbus RTU 用的就是 CRC-16/MODBUS。"),
        NOTE("分包与粘包", "串口一次 read 可能只收到半帧，也可能一次收到两帧。解析器必须维护缓冲区：不够长就等，够长就解，坏了就丢一个字节重新找帧头。绝不能假设「一次 read = 一帧」。", "warn"),
    ],
    walkthrough=[
        seg(
            "CRC16/MODBUS",
            r'''
import cv2
import json
import os
import struct
import numpy as np

def crc16_modbus(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

check = crc16_modbus(b"123456789")
print("CRC 标准校验值:", hex(check))
metric("CRC 校验值", hex(check))
''',
            "CRC 初值 0xFFFF，逐字节异或后做 8 次右移；最低位为 1 时异或多项式 0xA001（0x8005 的反转）。标准测试串 `123456789` 的结果应是 `0x4B37`，用它验证实现是否正确。",
            "多项式、初值、是否反转、最终异或，这四个参数不同就是不同的 CRC；对接时必须和对方一致。",
        ),
        seg(
            "编码一帧",
            r'''
HEADER = b"\xAA\x55"

def encode_frame(cmd, payload=b""):
    if len(payload) > 255:
        raise ValueError("payload 太长")
    body = bytes([len(payload), cmd]) + payload
    crc = crc16_modbus(body)
    return HEADER + body + struct.pack("<H", crc)

frame1 = encode_frame(0x01, bytes([0x01, 0x02]))
frame2 = encode_frame(0x02, struct.pack("<f", 36.5))
print("frame1:", frame1.hex(" "))
print("frame2:", frame2.hex(" "))
''',
            "长度只统计 payload，不包含帧头/命令/CRC。CRC 覆盖「长度 + 命令 + 数据」，接收方用同样范围重算。`struct.pack(\"<H\", crc)` 按小端写 2 字节；`<f` 按小端写 4 字节浮点。",
            "hex() 输出是给人看的；真正发送要用 bytes。不要用字符串 `\"AA55\"` 直接发。",
        ),
        seg(
            "流式解析器",
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
        length = buffer[2]
        total = 6 + length
        if len(buffer) < total:
            return frames, buffer
        frame = buffer[:total]
        body = frame[2:4 + length]
        crc_recv = struct.unpack("<H", frame[4 + length:6 + length])[0]
        if crc16_modbus(body) == crc_recv:
            frames.append({"cmd": frame[3], "payload": frame[4:4 + length]})
            buffer = buffer[total:]
        else:
            buffer = buffer[1:]
''',
            "解析器循环做四件事：找帧头、等够长度、校验 CRC、成功就消费整帧/失败就丢 1 字节重找。返回 `(已解析帧, 剩余缓冲)`，调用方把剩余缓冲和下次读到的数据拼起来继续解析。",
            "坏帧只丢 1 字节而不是整帧，是为了防止「假帧头」把后面的好帧一起吃掉。",
        ),
        seg(
            "模拟噪声、粘包、分包",
            r'''
stream = b"\x00\xff" + frame1 + b"\x99" + frame2[:3]
frames, rest = parse_stream(stream)
print("第一次解析:", len(frames), [hex(f["cmd"]) for f in frames])
print("剩余字节:", rest.hex(" "))

frames2, rest2 = parse_stream(rest + frame2[3:])
print("补全后解析:", len(frames2), [hex(f["cmd"]) for f in frames2])
print("最终剩余:", rest2)
metric("第一次解析帧数", len(frames))
metric("补全后帧数", len(frames2))
''',
            "`frame2` 被故意切成两段：第一次只给前 3 字节，解析器应该保留；把剩余部分补上后再解析，应该得到完整帧。前面的 `00 ff` 和 `99` 是噪声，会被跳过。",
        ),
        seg(
            "坏 CRC 与帧结构图",
            r'''
bad = frame1[:-1] + b"\x00"
bad_frames, _ = parse_stream(bad)
print("坏 CRC 被丢弃:", len(bad_frames) == 0)

diagram = np.full((260, 1100, 3), 22, np.uint8)
boxes = [
    (30, "AA 55", "帧头 2B", (80, 160, 255)),
    (220, "LEN", "长度 1B", (120, 220, 160)),
    (370, "CMD", "命令 1B", (255, 200, 100)),
    (520, "PAYLOAD", "数据 LEN B", (200, 160, 255)),
    (820, "CRC16", "校验 2B", (255, 120, 140)),
]
for x, title, sub, color in boxes:
    cv2.rectangle(diagram, (x, 80), (x + 150, 170), color, 2)
    cv2.putText(diagram, title, (x + 10, 125), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, color, 2, cv2.LINE_AA)
    cv2.putText(diagram, sub, (x + 10, 152), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (210, 210, 210), 1, cv2.LINE_AA)
cv2.putText(diagram, "UART frame: header + length + command + payload + crc",
            (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), 2, cv2.LINE_AA)
result = diagram
''',
            "坏 CRC 的帧必须被丢弃，不能把错误数据交给控制环。最后把帧结构画出来，方便和嵌入式同事对接字段。",
        ),
    ],
    tests=[
        test("CRC 标准值正确", "crc16_modbus(b'123456789') == 0x4B37"),
        test("编码后能解码", "parse_stream(frame1)[0][0]['cmd'] == 0x01"),
        test("分包后能补齐", "len(frames2) == 1 and frames2[0]['cmd'] == 0x02"),
        test("坏 CRC 被丢弃", "len(bad_frames) == 0"),
    ],
    tasks=[
        task("dev", "加一个回包命令", "定义 0x81 为 ACK、0x82 为 NACK；收到命令后回一帧 ACK。"),
        task("dev", "解析浮点", "把 frame2 的 payload 用 `struct.unpack(\"<f\", ...)` 解出 36.5 并打印。"),
        task("observe", "删掉一个字节", "从 frame1 中间删一个字节，观察解析器是否能重新同步、会丢掉什么。"),
    ],
    quiz_items=[
        quiz("长度字段通常统计什么？", ["整帧", "payload", "帧头", "CRC"], 1,
             "本协议只统计 payload，收发双方约定一致即可。"),
        quiz("坏 CRC 时为什么只丢 1 字节？", ["更快", "防止假帧头吞掉后面的好帧", "省内存", "CRC 要求"], 1,
             "从下一字节重新找帧头，才有可能重新同步。"),
        quiz("`struct.pack(\"<H\", x)` 的 `<` 表示？", ["大端", "小端", "无符号", "浮点"], 1,
             "`<` 是小端，`>` 是大端。"),
    ],
    industry="STM32/Arduino 与工控机、ROS2 与底盘、PLC 与视觉传感器之间大量使用串口/CAN/Modbus。协议设计、CRC、超时重传、分包处理是机器人软件工程师的日常。",
    career="开发型岗位要写稳定的协议库和单元测试；调控型岗位要会用串口助手抓包，判断是丢包、CRC 错、波特率不对还是接线问题。",
    next_step="下一课把多个动作组织成状态机，并处理超时与故障恢复。",
)

L2 = lesson(
    "ctrl-state",
    "状态机：分拣站的节拍、超时与故障恢复",
    "显式状态迁移、事件、超时、JSONL 日志、甘特图",
    chapter="engineer",
    difficulty=4,
    minutes=50,
    tags=["状态机", "日志", "故障"],
    objectives=[
        "用「状态 + 事件 → 下一状态」的表格描述分拣流程",
        "实现拒绝非法迁移、超时进入 ERROR、reset 恢复",
        "把迁移写成 JSONL，并画出每个场景的时间线",
    ],
    concept=[
        P("分拣站不是一个长脚本，而是一组状态：待机、检测、抓取、放置、回零。每个状态只关心「收到什么事件、下一步去哪」。把迁移写成显式表格，才能测试、才能在上位机画出流程、才能在故障时知道停在哪。"),
        TABLE(
            ["当前状态", "事件", "下一状态", "动作"],
            [
                ["IDLE", "start", "DETECT", "开相机/开灯"],
                ["DETECT", "found", "PICK", "锁定目标"],
                ["PICK", "picked", "PLACE", "关吸盘/抬升"],
                ["PLACE", "placed", "HOME", "松开/回零"],
                ["HOME", "homed", "IDLE", "等下一件"],
                ["DETECT/PICK/PLACE", "timeout/fault", "ERROR", "停线/报警"],
                ["ERROR", "reset", "IDLE", "清故障"],
            ],
        ),
        H("为什么要显式拒绝非法事件"),
        P("如果任何事件都能从任何状态触发，程序会在异常时跳到不可能的组合（比如 IDLE 直接 PLACE）。状态机应该记录「这个事件在当前状态不合法」，而不是静默忽略——现场排障时这条日志非常值钱。"),
        NOTE("超时是状态机的一部分", "检测 2 秒没结果、抓取 3 秒没到位，都要从「等待」变成「故障」。没有超时的状态机，会在现场无限等下去。", "warn"),
    ],
    walkthrough=[
        seg(
            "定义状态与迁移表",
            r'''
import cv2
import json
import os
import time
import numpy as np

STATES = ["IDLE", "DETECT", "PICK", "PLACE", "HOME", "ERROR"]
TRANSITIONS = {
    ("IDLE", "start"): "DETECT",
    ("DETECT", "found"): "PICK",
    ("DETECT", "timeout"): "ERROR",
    ("PICK", "picked"): "PLACE",
    ("PICK", "fault"): "ERROR",
    ("PLACE", "placed"): "HOME",
    ("PLACE", "timeout"): "ERROR",
    ("HOME", "homed"): "IDLE",
    ("ERROR", "reset"): "IDLE",
}
print("状态数:", len(STATES), "迁移数:", len(TRANSITIONS))
''',
            "用字典把迁移表写成数据，而不是写成一堆 if/elif。状态和事件都是字符串，键是 `(state, event)`，值是下一状态。新增动作只需要改表。",
        ),
        seg(
            "状态机类",
            r'''
class Cell:
    def __init__(self):
        self.state = "IDLE"
        self.t = 0
        self.errors = 0
        self.log = []

    def step(self, event, detail=""):
        key = (self.state, event)
        if key not in TRANSITIONS:
            self.log.append({"t": self.t, "state": self.state, "event": event,
                             "next": self.state, "ok": False, "detail": detail})
            return False
        nxt = TRANSITIONS[key]
        if nxt == "ERROR":
            self.errors += 1
        self.log.append({"t": self.t, "state": self.state, "event": event,
                         "next": nxt, "ok": True, "detail": detail})
        self.state = nxt
        self.t += 1
        return True
''',
            "`step` 只做三件事：查表、记录、迁移。非法事件记录 `ok=False` 但不改变状态。`errors` 统计进入 ERROR 的次数，`t` 是逻辑时钟（每一步 +1，真实系统用毫秒时间戳）。",
        ),
        seg(
            "跑三个场景",
            r'''
def run(events):
    cell = Cell()
    for event, detail in events:
        cell.step(event, detail)
    return cell

normal = run([("start", "cycle 1"), ("found", "red @ 220,180"),
              ("picked", "vacuum on"), ("placed", "bin A"),
              ("homed", "cycle done")])
timeout = run([("start", "cycle 2"), ("timeout", "no object in 2s"),
               ("reset", "operator")])
fault = run([("start", "cycle 3"), ("found", "blue @ 610,250"),
             ("fault", "vacuum lost"), ("reset", "operator")])

print("normal:", normal.state, "errors:", normal.errors)
print("timeout:", timeout.state, "errors:", timeout.errors)
print("fault:", fault.state, "errors:", fault.errors)
metric("正常节拍", normal.t)
metric("正常错误数", normal.errors)
metric("超时错误数", timeout.errors)
''',
            "正常场景走完 IDLE→DETECT→PICK→PLACE→HOME→IDLE；超时场景在 DETECT 进入 ERROR，reset 回 IDLE；故障场景在 PICK 进入 ERROR。三个场景都从 IDLE 开始，互不影响。",
        ),
        seg(
            "写 JSONL 日志",
            r'''
log_path = os.path.join(work_dir, "cell_events.jsonl")
with open(log_path, "w", encoding="utf-8") as f:
    for row in normal.log:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("日志行数:", sum(1 for _ in open(log_path, encoding="utf-8")))
metric("日志行数", len(normal.log))
''',
            "一行一个 JSON 对象，追加方便、按行读取也方便。真实系统会加 `timestamp`、`robot_id`、`cycle_id`、`operator`，并用日志采集工具集中存储。",
            "不要把所有日志拼成一个巨大 JSON 数组；崩溃时整个文件可能损坏。JSONL 更适合流式写入。",
        ),
        seg(
            "画状态时间线",
            r'''
timeline = np.full((380, 1080, 3), 20, np.uint8)
rows = [("normal", normal), ("timeout", timeout), ("fault", fault)]
colors = {"IDLE": (120, 120, 120), "DETECT": (90, 190, 255),
          "PICK": (120, 220, 140), "PLACE": (255, 200, 90),
          "HOME": (200, 160, 255), "ERROR": (90, 90, 240)}
for r, (name, cell) in enumerate(rows):
    y = 80 + r * 90
    cv2.putText(timeline, name, (20, y + 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (235, 235, 235), 2, cv2.LINE_AA)
    x = 170
    for row in cell.log:
        color = colors.get(row["state"], (200, 200, 200))
        cv2.rectangle(timeline, (x, y), (x + 80, y + 42), color, -1)
        cv2.putText(timeline, row["state"], (x + 6, y + 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (20, 20, 20), 1, cv2.LINE_AA)
        x += 90
cv2.putText(timeline, "state timeline (one block per transition)",
            (170, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), 2, cv2.LINE_AA)
result = timeline
''',
            "每一行是一个场景，每一块是一次状态。正常场景能看到完整的五步；超时和故障场景会在 ERROR 处出现红色块。现场复盘时，这张图比几百行日志更快定位问题。",
        ),
    ],
    tests=[
        test("正常流程回到 IDLE", "normal.state == 'IDLE'"),
        test("正常流程没有错误", "normal.errors == 0"),
        test("超时进入过 ERROR", "timeout.errors == 1"),
        test("reset 后恢复 IDLE", "timeout.state == 'IDLE' and fault.state == 'IDLE'"),
        test("日志已落盘", "os.path.isfile(log_path)"),
    ],
    tasks=[
        task("dev", "增加暂停/继续", "新增 PAUSED 状态，任何状态收到 pause 进入 PAUSED，resume 回到之前状态。"),
        task("dev", "记录时间戳", "把 `t` 改成 `time.time()`，并在日志里加 `elapsed_ms`。"),
        task("observe", "发一个非法事件", "在 IDLE 状态发 `placed`，观察 `ok=False` 的日志和状态不变。"),
    ],
    quiz_items=[
        quiz("状态机迁移表最适合用什么结构？", ["列表", "字典", "字符串", "类"], 1,
             "(state, event) 到 next state 的映射，字典最直接。"),
        quiz("非法事件应该？", ["静默忽略", "跳到任意状态", "记录并拒绝", "重启程序"], 2,
             "记录拒绝原因，状态不变，便于排障。"),
        quiz("为什么超时要进入 ERROR？", ["让界面好看", "避免无限等待", "加快节拍", "省电"], 1,
             "没有超时会在现场永久卡住。"),
    ],
    industry="PLC 的顺控、ROS2 的 lifecycle node、行为树、抓取流水线都用状态机思想。真正难的是异常分支：相机掉线、抓取失败、料框满、急停、人工复位。",
    career="开发型岗位设计状态与迁移、保证可测试；调控型岗位根据状态日志判断卡在哪一步、是超时、传感器还是执行器。",
    next_step="下一课做工程化闭环：构造数据集、算 precision/recall、剖析耗时、写单元测试。",
)

L3 = lesson(
    "eng-debug",
    "调试与评估：误检率 3% 该怎么查",
    "合成数据集、precision/recall/F1、阈值扫描、耗时剖析、配置与断言",
    chapter="engineer",
    difficulty=5,
    minutes=55,
    tags=["评估", "调试", "单元测试"],
    objectives=[
        "构造带标签的缺陷数据集，区分「看起来准」和「指标准」",
        "扫描阈值，计算 precision/recall/F1，选择工作点",
        "用 perf_counter 剖析耗时，把参数写进配置并用断言锁住行为",
    ],
    concept=[
        P("「误检率 3%」不是一句感觉，而是一个可以拆开的指标。先定义：缺陷为正类。precision = 检出的里有多少是真的；recall = 真缺陷里检出了多少。两条曲线此消彼长，选哪个工作点取决于漏检和误检的成本。"),
        FORMULA("P = TP/(TP+FP)，R = TP/(TP+FN)，F1 = 2PR/(P+R)", "分类指标"),
        H("为什么先做数据集"),
        P("没有标签就无法判断改动是变好还是变坏。工业上会收集正常品、各类缺陷、边界样本，做成固定回归集；每次改参数/换模型都跑一遍，记录 P/R 和耗时。"),
        NOTE("先剖析，再优化", "用 `time.perf_counter()` 包住每个阶段，确认瓶颈在模糊、阈值还是 I/O。不要凭感觉把整段代码重写。", "tip"),
    ],
    walkthrough=[
        seg(
            "构造 16 张带标签的 patch",
            r'''
import cv2
import json
import os
import time
import numpy as np

def make_patch(kind, index):
    rng = np.random.default_rng(500 + index)
    yy, xx = np.mgrid[0:128, 0:128]
    img = 150 + 12 * np.sin(xx / 4.0) + 8 * np.sin(yy / 6.0)
    img = img + rng.normal(0, 4, (128, 128))
    img = np.clip(img, 0, 255).astype(np.uint8)
    if kind == "clean" and index >= 6:
        cv2.line(img, (30, 100), (95, 95), 205, 3, cv2.LINE_AA)
    if kind == "defect":
        contrast = 70 if index < 6 else 28
        width = 2 if index < 6 else 1
        x0 = int(rng.integers(20, 70))
        y0 = int(rng.integers(20, 70))
        cv2.line(img, (x0, y0),
                 (x0 + int(rng.integers(25, 45)), y0 + int(rng.integers(-25, 25))),
                 int(150 - contrast), width, cv2.LINE_AA)
    return img

dataset = []
for i in range(8):
    dataset.append((make_patch("clean", i), 0))
for i in range(8):
    dataset.append((make_patch("defect", i), 1))
print("样本数:", len(dataset), "正样本:", sum(y for _, y in dataset))
metric("样本数", len(dataset))
''',
            "8 张正常 + 8 张缺陷。正常样本里有两张带「折痕」（index>=6），缺陷样本里有两张很淡（index>=6），用来制造误检和漏检。数据量很小，只用于演示评估流程。",
        ),
        seg(
            "缺陷评分与阈值扫描",
            r'''
def defect_score(patch, blur_size=9, hp_threshold=25):
    blur = cv2.GaussianBlur(patch, (blur_size, blur_size), 0)
    high_pass = cv2.absdiff(patch, blur)
    return float((high_pass > hp_threshold).mean())

scores = [(defect_score(p), y) for p, y in dataset]
rows = []
for threshold in [0.0005, 0.0008, 0.001, 0.0015, 0.002, 0.003]:
    tp = sum(1 for s, y in scores if y == 1 and s >= threshold)
    fp = sum(1 for s, y in scores if y == 0 and s >= threshold)
    fn = sum(1 for s, y in scores if y == 1 and s < threshold)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    rows.append({"threshold": threshold, "tp": tp, "fp": fp, "fn": fn,
                 "precision": precision, "recall": recall, "f1": f1})
best = max(rows, key=lambda r: r["f1"])
print("最佳阈值:", best["threshold"], "P/R/F1:",
      round(best["precision"], 2), round(best["recall"], 2), round(best["f1"], 2))
metric("precision", round(best["precision"], 3))
metric("recall", round(best["recall"], 3))
metric("f1", round(best["f1"], 3))
''',
            "缺陷是细线，高频成分强；正常织纹的高频弱。`absdiff(patch, blur)` 是高通滤波，统计超过阈值的像素比例作为分数。扫描不同决策阈值，选 F1 最高的工作点。",
            "F1 只是单一工作点的概括；真实项目要看 PR 曲线和业务成本，漏检往往比误检更贵。",
        ),
        seg(
            "耗时剖析",
            r'''
start = time.perf_counter()
for _ in range(30):
    for patch, _label in dataset:
        defect_score(patch)
elapsed = (time.perf_counter() - start) * 1000
avg_ms = elapsed / (30 * len(dataset))
print("单张平均耗时: %.3f ms" % avg_ms)
metric("avg_ms", round(avg_ms, 3))
''',
            "30 轮 × 16 张，取平均。`perf_counter` 是高精度单调时钟，适合测短间隔。真实产线还要测端到端（采集、预处理、推理、通信），而不只是评分函数。",
        ),
        seg(
            "写配置与断言",
            r'''
config = {"blur_size": 9, "hp_threshold": 25,
          "decision_threshold": best["threshold"], "version": 1}
config_path = os.path.join(work_dir, "defect_config.json")
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# 最小单元测试：正常折痕不能全部误报，明显缺陷必须检出
assert defect_score(dataset[0][0]) < config["decision_threshold"]
assert defect_score(dataset[8][0]) >= config["decision_threshold"]
print("配置已写入:", config_path)
''',
            "参数写进 JSON，版本化，方便回滚和对比。底部两条断言是最小回归测试：一条正常样本不能报警，一条明显缺陷必须报警。真实项目会用 pytest 管理几十条这样的用例。",
            "断言不要只覆盖「容易的样本」；边界样本（折痕、淡划痕）才是回归时最容易坏的地方。",
        ),
        seg(
            "可视化样本与 PR 曲线",
            r'''
grid = np.full((4 * 150 + 20, 4 * 150 + 20, 3), 24, np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX
for i, (patch, label) in enumerate(dataset):
    row, col = divmod(i, 4)
    x, y = 10 + col * 150, 10 + row * 150
    tile = cv2.cvtColor(patch, cv2.COLOR_GRAY2BGR)
    grid[y:y + 128, x:x + 128] = tile
    s = defect_score(patch)
    color = (90, 220, 120) if (s >= best["threshold"]) == bool(label) else (80, 80, 240)
    cv2.putText(grid, "%s %.4f" % ("D" if label else "N", s),
                (x, y + 145), font, 0.42, color, 1, cv2.LINE_AA)
capture("样本与分数", grid)

plot = np.full((360, 560, 3), 22, np.uint8)
pts = []
for r in rows:
    px = 60 + int(r["recall"] * 460)
    py = 300 - int(r["precision"] * 240)
    pts.append((px, py))
cv2.polylines(plot, [np.array(pts, np.int32)], False, (90, 220, 160), 2)
for i, r in enumerate(rows):
    cv2.circle(plot, pts[i], 4, (255, 200, 90), -1)
cv2.putText(plot, "PR curve", (60, 35), font, 0.8, (235, 235, 235), 2, cv2.LINE_AA)
cv2.putText(plot, "recall ->", (420, 340), font, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
cv2.putText(plot, "precision", (10, 60), font, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
capture("PR 曲线", plot)
result = np.hstack([grid, cv2.resize(plot, (560, 620))])
''',
            "左边是 16 张样本和分数，绿色表示判断正确、红色表示判断错误；右边是 PR 曲线。把失败样本放在眼前，比只看一个 F1 数字更容易发现问题。",
        ),
    ],
    tests=[
        test("最佳 F1 达标", "best['f1'] >= 0.75"),
        test("precision 达标", "best['precision'] >= 0.8"),
        test("recall 达标", "best['recall'] >= 0.7"),
        test("单张耗时低于 50ms", "avg_ms < 50"),
        test("配置文件已生成", "os.path.isfile(config_path)"),
    ],
    params=[
        param("blur_size", "高通模糊核", 9, 3, 21, 2),
        param("hp_threshold", "高通阈值", 25, 10, 60, 1),
    ],
    tasks=[
        task("dev", "增加 F2 指标", "给 F2（更看重 recall）写一个计算，并选 F2 最高的工作点。"),
        task("dev", "加一张边界样本", "构造一张「折痕 + 淡划痕」的样本，观察它被分到哪一类，并解释。"),
        task("observe", "把模糊核调小", "把 blur_size 改成 3，重新跑扫描，观察正常样本分数是否升高。"),
    ],
    quiz_items=[
        quiz("precision 的分母是？", ["TP+FN", "TP+FP", "TN+FP", "全部样本"], 1,
             "precision = TP/(TP+FP)，检出的里有多少是真的。"),
        quiz("漏检增加会导致？", ["precision 下降", "recall 下降", "F1 上升", "耗时下降"], 1,
             "FN 增加，recall = TP/(TP+FN) 下降。"),
        quiz("调参前应该先做什么？", ["重写算法", "固定数据集并测基线", "换相机", "加更多线程"], 1,
             "没有基线就无法判断改动是否有效。"),
    ],
    industry="工业视觉的 AOI、表面缺陷检测、异常检测都靠这套评估闭环。真实项目会分正常/缺陷/边界三类，记录 P/R、过杀率、漏检率、节拍和稳定性，并做长期漂移监控。",
    career="开发型岗位搭建评估与回归测试；调控型岗位用指标和失败样本定位是阈值、光照、材料还是算法假设的问题。",
    next_step="最后一课把视觉、标定、状态机、串口串成一个完整的智能分拣站。",
)

CHAPTER = chapter(
    "engineer", "04", "控制与工程化",
    "会写算法只是开始：还要让协议可靠、状态可恢复、指标可验证。",
    [L1, L2, L3],
    color="#c084fc", icon="04",
)
