# -*- coding: utf-8 -*-
"""第七章：电机与运动控制（FOC / EtherCAT / 驱控一体）。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "foc-basics",
    "FOC 入门：三相电流如何变成 dq 两个数",
    "Clarke/Park 变换、逆变换、SVPWM/SPWM 占空比与三相波形",
    chapter="motor",
    difficulty=3,
    minutes=45,
    tags=["FOC", "Clarke", "Park"],
    objectives=[
        "把三相电流变成 αβ，再变成旋转坐标 dq",
        "验证 id≈0、iq≈指令值，理解“转矩只跟 iq 有关”",
        "从 vd/vq 反算三相占空比，画出电流与 PWM 波形",
    ],
    concept=[
        P("FOC（磁场定向控制）的核心是把三相正弦电流投影到跟着转子旋转的 dq 坐标：d 轴管磁链，q 轴管转矩。控制器只需控制 id、iq 两个直流量，而不是三条相位差 120° 的交流量。"),
        FORMULA("iα = 2/3(ia − ib/2 − ic/2)，iβ = (ib − ic)/sqrt(3)", "Clarke 变换"),
        FORMULA("id = iαcosθ + iβsinθ，iq = −iαsinθ + iβcosθ", "Park 变换"),
        TABLE(
            ["量", "含义", "控制目标"],
            [
                ["id", "励磁电流", "通常设为 0（表贴式电机）"],
                ["iq", "转矩电流", "与目标转矩成正比"],
                ["θe", "转子电角度", "来自编码器/霍尔/无感观测器"],
                ["duty", "三相占空比", "经 SVPWM/SPWM 给逆变器"],
            ],
        ),
        NOTE("坐标变换不是“调参”", "Clarke/Park 是线性变换，系数取决于你采用等幅值还是等功率约定。本课用等幅值约定；换库/换芯片时要确认系数，否则电流幅值会差 √(3/2)。", "warn"),
    ],
    walkthrough=[
        seg(
            "设定电机参数与运行点",
            r'''
import cv2
import numpy as np

R = 0.5          # 相电阻 Ω
L = 0.001        # 相电感 H
FLUX = 0.01      # 永磁磁链 Wb
POLES = 7        # 极对数
VDC = 48.0       # 母线电压 V
speed_rpm = 1200.0
iq_ref = 10.0
id_ref = 0.0

omega_m = speed_rpm * 2 * np.pi / 60.0
omega_e = omega_m * POLES
theta = np.linspace(0, 2 * np.pi, 720, endpoint=False)
print("电角速度: %.1f rad/s" % omega_e)
''',
            "先固定一个运行点：转速、母线电压、iq 指令。真实 FOC 里 θe 来自编码器，随时间是变化的；这里取一个电周期做稳态分析，便于看清波形。",
        ),
        seg(
            "逆 Park + 逆 Clarke 生成三相电流",
            r'''
i_alpha = -iq_ref * np.sin(theta) + id_ref * np.cos(theta)
i_beta = iq_ref * np.cos(theta) + id_ref * np.sin(theta)
ia = i_alpha
ib = -0.5 * i_alpha + np.sqrt(3) / 2 * i_beta
ic = -0.5 * i_alpha - np.sqrt(3) / 2 * i_beta
print("三相电流幅值:", round(float(np.max(np.abs(ia))), 1))
''',
            "已知 id/iq，反变换回三相，得到三条相位差 120° 的正弦。`ia+ib+ic≈0` 是三相三线制的约束，也是检查变换有没有写错的第一条断言。",
        ),
        seg(
            "正向变换验证",
            r'''
alpha = (2 / 3) * (ia - 0.5 * ib - 0.5 * ic)
beta = (2 / 3) * (np.sqrt(3) / 2 * ib - np.sqrt(3) / 2 * ic)
id_now = alpha * np.cos(theta) + beta * np.sin(theta)
iq_now = -alpha * np.sin(theta) + beta * np.cos(theta)
print("id 均值: %.4f" % float(np.mean(id_now)))
print("iq 均值: %.4f" % float(np.mean(iq_now)))
metric("id 均值", round(float(np.mean(id_now)), 4))
metric("iq 均值", round(float(np.mean(iq_now)), 4))
''',
            "把生成的三相电流再变回 dq，应该几乎回到设定值。这一步是“变换闭环”测试：先相信数学，再相信硬件采样。",
        ),
        seg(
            "从 vd/vq 算三相占空比",
            r'''
vd = R * id_ref - omega_e * L * iq_ref
vq = R * iq_ref + omega_e * (L * id_ref + FLUX)
v_alpha = vd * np.cos(theta) - vq * np.sin(theta)
v_beta = vd * np.sin(theta) + vq * np.cos(theta)
va = v_alpha
vb = -0.5 * v_alpha + np.sqrt(3) / 2 * v_beta
vc = -0.5 * v_alpha - np.sqrt(3) / 2 * v_beta
duty = 0.5 + np.vstack([va, vb, vc]) / VDC
duty = np.clip(duty, 0.0, 1.0)
print("占空比范围: %.2f ~ %.2f" % (duty.min(), duty.max()))
metric("最大占空比", round(float(duty.max()), 3))
''',
            "稳态电压方程里包含电阻压降、电感压降和反电动势。`0.5 + v/Vdc` 是 SPWM 的近似；实际产品常用 SVPWM，母线利用率高约 15%，但坐标变换和电流环思想相同。",
            "如果占空比接近 0 或 1，说明电压指令超出母线能力，需要弱磁、限幅或提高 Vdc。",
        ),
        seg(
            "画三相电流、dq 电流和占空比",
            r'''
canvas = np.full((760, 1080, 3), 18, np.uint8)

def curve(ax, values, color, label, y0, h, lo, hi):
    pts = []
    for i, v in enumerate(values):
        px = 70 + int(i * 940 / (len(values) - 1))
        py = y0 + h - int((v - lo) / (hi - lo) * h)
        pts.append((px, py))
    cv2.polylines(canvas, [np.array(pts, np.int32)], False, color, 2)
    cv2.putText(canvas, label, (70, y0 - 8), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 1, cv2.LINE_AA)

curve(canvas, ia, (80, 200, 255), "ia", 50, 170, -12, 12)
curve(canvas, ib, (120, 240, 140), "ib", 270, 170, -12, 12)
curve(canvas, ic, (255, 180, 120), "ic", 490, 170, -12, 12)
curve(canvas, iq_now, (80, 220, 255), "iq (should be 10)", 50, 170, -12, 12)
result = canvas
''',
            "把三相波形和 iq 画在一起，能直观看到“交流量 → 直流量”的效果。真实调试时还会看电流环给定/反馈、编码器角度和 PWM 占空比。",
        ),
    ],
    tests=[
        test("三相电流和为零", "abs(float(np.max(np.abs(ia + ib + ic)))) < 1e-9"),
        test("id 接近 0", "abs(float(np.mean(id_now))) < 0.01"),
        test("iq 接近指令", "abs(float(np.mean(iq_now)) - iq_ref) < 0.01"),
        test("占空比在 0~1", "float(duty.min()) >= 0 and float(duty.max()) <= 1"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    params=[
        param("iq_ref", "iq 指令（A）", 10, 2, 20, 1),
        param("speed_rpm", "转速（rpm）", 1200, 100, 3000, 50),
    ],
    tasks=[
        task("dev", "改成 id=2", "把 id_ref 改成 2 A，重新验证 id/iq，并解释 d 轴电流的作用。"),
        task("dev", "加 SVPWM", "查 SVPWM 的扇区判断和七段式占空比，替换 SPWM 的 0.5+v/Vdc。"),
        task("observe", "提高转速", "把 speed_rpm 提到 3000，观察反电动势和占空比是否接近饱和。"),
    ],
    quiz_items=[
        quiz("FOC 里控制转矩的是？", ["id", "iq", "ia", "Vdc"], 1,
             "表贴式电机 id=0，转矩与 iq 成正比。"),
        quiz("Park 变换的作用？", ["把三相变两相", "把静止 αβ 变到旋转 dq", "把交流变直流电压", "滤波"], 1,
             "Park 用转子角把 αβ 投影到随转子旋转的 dq。"),
        quiz("占空比接近 1 说明？", ["电压不够", "电压指令接近母线上限", "电流为零", "编码器坏了"], 1,
             "占空比饱和，需要限幅/弱磁/提高母线电压。"),
    ],
    industry="FOC 是伺服、云台、无人机电调、电动车驱动的基础。真正产品还要处理电流采样、死区、母线电压波动、编码器对齐、弱磁和故障保护。",
    career="运动控制开发要能把 FOC 数学、功率电路和嵌入式代码对上；调控岗位要会看相电流、iq 响应、占空比饱和和温升。",
    next_step="下一课把 FOC 接到电流环 PI，观察阶跃响应和整定。",
)

L2 = lesson(
    "foc-loop",
    "FOC 电流环：PI、限幅与阶跃响应",
    "一阶电机模型、PI 电流环、积分限幅、上升/超调/调节时间",
    chapter="motor",
    difficulty=4,
    minutes=45,
    tags=["FOC", "PI", "电流环"],
    objectives=[
        "用离散模型模拟 dq 电流环",
        "理解 Kp/Ki、母线限幅、积分抗饱和对响应的影响",
        "从阶跃响应读出上升时间、超调和稳态误差",
    ],
    concept=[
        P("电流环是 FOC 最内层、最快的环。它把 iq 指令变成电压指令，让实际电流在几百微秒到几毫秒内跟上。外层的速度环、位置环都建立在它之上。"),
        FORMULA("L·di/dt = v − R·i − Ke·ω", "简化 d 轴/q 轴模型（这里把 q 轴单独拿出来）"),
        FORMULA("v = Kp·e + Ki·∫e dt", "PI 控制器；输出再限幅到 ±Vdc/2"),
        NOTE("积分抗饱和", "电压被母线限幅时，积分项如果继续累加，退饱和会严重超调。代码里必须对积分限幅，或做 back-calculation。", "warn"),
    ],
    walkthrough=[
        seg(
            "电机与控制器参数",
            r'''
import cv2
import numpy as np

R, L, Ke = 0.5, 0.001, 0.05
VDC = 48.0
DT = 1e-4
STEPS = 4000
speed_rpm = 1000.0
omega = speed_rpm * 2 * np.pi / 60.0
i_ref = 10.0
kp_i, ki_i = float(p["kp_i"]), float(p["ki_i"])
print("电流环周期: %.2f ms" % (DT * 1000))
''',
            "真实电流环通常在 10–20 kHz（50–100 µs）。这里用 100 µs 离散步长，既能看清动态，又不会让仿真太慢。",
        ),
        seg(
            "离散 PI + 电机模型",
            r'''
i = 0.0
integral = 0.0
history = []
for step in range(STEPS):
    error = i_ref - i
    integral = max(-50.0, min(50.0, integral + error * DT))
    v = kp_i * error + ki_i * integral
    v = max(-VDC / 2, min(VDC / 2, v))
    di = (v - R * i - Ke * omega) / L
    i += di * DT
    history.append((i, v, error))
print("最终电流: %.4f A" % history[-1][0])
''',
            "每个周期：算误差 → 积分（限幅）→ PI 输出 → 母线限幅 → 电机方程积分。`Ke*omega` 是反电动势，PI 会把它当成扰动自动补掉。",
        ),
        seg(
            "读指标",
            r'''
currents = np.array([h[0] for h in history])
final_error = abs(i_ref - currents[-1])
overshoot = max(0.0, (float(currents.max()) - i_ref) / i_ref * 100.0)
settle = len(currents)
for k in range(len(currents)):
    if np.all(np.abs(currents[k:] - i_ref) < 0.1):
        settle = k
        break
print("稳态误差: %.4f A" % final_error)
print("超调: %.1f %%" % overshoot)
print("调节步数: %d (%.1f ms)" % (settle, settle * DT * 1000))
metric("稳态误差(A)", round(float(final_error), 4))
metric("超调(%)", round(float(overshoot), 1))
metric("调节(ms)", round(float(settle * DT * 1000), 1))
''',
            "三个指标分别看“准不准、冲不冲、快不快”。电流环通常要求无稳态误差、超调小、调节时间在毫秒级；具体指标由机械和工艺决定。",
        ),
        seg(
            "画阶跃响应",
            r'''
canvas = np.full((420, 1000, 3), 18, np.uint8)
def draw(vals, color, lo, hi, y0=40, h=280, label=""):
    pts = []
    for i, v in enumerate(vals):
        x = 60 + int(i * 880 / (len(vals) - 1))
        y = y0 + h - int((v - lo) / (hi - lo) * h)
        pts.append((x, y))
    cv2.polylines(canvas, [np.array(pts, np.int32)], False, color, 2)
    cv2.putText(canvas, label, (60, y0 - 8), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 1, cv2.LINE_AA)

draw(currents, (80, 220, 255), 0, 13, label="iq step response")
cv2.line(canvas, (60, 320), (940, 320), (60, 60, 60), 1)
result = canvas
''',
            "把阶跃响应画出来，比只看一个数字更容易发现震荡、饱和和积分饱和。真实调试会用示波器/伺服上位机看同样的曲线。",
        ),
        seg(
            "换一组参数看变化",
            r'''
for kp, ki in ((1.0, 500.0), (2.0, 1000.0), (1.0, 2000.0)):
    i2, integ2 = 0.0, 0.0
    peak = 0.0
    for _ in range(STEPS):
        e = i_ref - i2
        integ2 = max(-50.0, min(50.0, integ2 + e * DT))
        v2 = max(-VDC / 2, min(VDC / 2, kp * e + ki * integ2))
        i2 += (v2 - R * i2 - Ke * omega) / L * DT
        peak = max(peak, i2)
    print("Kp=%.0f Ki=%.0f -> peak=%.2f A" % (kp, ki, peak))
''',
            "同样的电机，Kp 影响“冲多快”，Ki 影响“多久消掉误差”。Ki 太大容易超调，Kp 太小会慢。先保证不饱和、不震荡，再谈快。",
        ),
    ],
    tests=[
        test("稳态误差小于 0.05A", "final_error < 0.05"),
        test("超调小于 5%", "overshoot < 5.0"),
        test("调节时间小于 20ms", "settle * DT * 1000 < 20"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    params=[
        param("kp_i", "电流环 Kp", 2.0, 0.2, 6.0, 0.1),
        param("ki_i", "电流环 Ki", 1000, 100, 3000, 50),
    ],
    tasks=[
        task("dev", "加抗饱和回算", "电压饱和时把积分项回退，比较超调变化。"),
        task("dev", "加速度环", "外环 PI 输出 iq 指令，内环仍是电流环，模拟负载扰动。"),
        task("observe", "把 Ki 调到 3000", "观察超调和调节时间，解释为什么不是越大越好。"),
    ],
    quiz_items=[
        quiz("电流环最内层通常多快？", ["1 Hz", "10–20 kHz", "50 Hz", "1 kHz"], 1,
             "电流环周期常见 50–100 µs，即 10–20 kHz。"),
        quiz("积分限幅主要防什么？", ["噪声", "积分饱和导致退饱和超调", "过压", "编码器丢步"], 1,
             "输出饱和时积分继续累积，退饱和会冲过头。"),
        quiz("反电动势在电流环里算什么？", ["噪声", "可被 PI 补偿的扰动", "故障", "编码器信号"], 1,
             "PI 的积分项会消掉常值扰动。"),
    ],
    industry="伺服驱动器、无人机电调、云台、机器人关节都用电流环。真正难点是采样噪声、死区、母线波动和参数随温度变化。",
    career="运动控制开发要能写离散 PI、限幅、抗饱和和故障保护；调控岗位要会看阶跃响应、判断震荡来自电流环还是机械。",
    next_step="下一课看工业现场的总线：EtherCAT 帧、PDO 和 CiA402 状态机。",
)

L3 = lesson(
    "ethercat-basics",
    "EtherCAT 入门：帧、PDO 与 CiA402",
    "EtherType、datagram、PDO 映射、状态字/控制字与使能序列",
    chapter="motor",
    difficulty=4,
    minutes=50,
    tags=["EtherCAT", "PDO", "CiA402"],
    objectives=[
        "看懂 EtherCAT 帧头和 datagram 的基本字段",
        "打包/解析一个 PDO，理解过程数据如何映射",
        "走一遍 CiA402 的使能状态机，知道每个控制字的作用",
    ],
    concept=[
        P("EtherCAT 是工业运动控制最常用的实时以太网之一。主站发一帧，从站边转发边读写，整条链路在一个帧里完成；PDO 传周期过程数据，SDO 传参数。"),
        TABLE(
            ["概念", "作用", "典型内容"],
            [
                ["EtherType 0x88A4", "标识 EtherCAT 帧", "以太网头之后"],
                ["Datagram", "一次读写命令", "APRD/APWR/FPRD/FPWR + 地址 + 数据"],
                ["PDO", "周期过程数据", "控制字、目标位置、状态字、实际位置"],
                ["SDO", "参数/对象字典", "增益、限位、编码器分辨率"],
                ["CiA402", "伺服状态机", "Shutdown/Switch on/Enable operation"],
            ],
        ),
        FORMULA("Ethernet | EtherCAT header | Datagram 1 | Datagram 2 | ...", "一帧可带多个 datagram"),
        NOTE("实时性不只靠协议", "EtherCAT 的实时性依赖主站调度、分布式时钟、从站实现和 NIC。用普通 Python 做硬实时不现实；本课只做帧/状态机的离线仿真。", "warn"),
    ],
    walkthrough=[
        seg(
            "构造一个 EtherCAT 帧",
            r'''
import struct
import cv2
import numpy as np

def build_frame(payload, cmd=0x0C, index=1, address=0x1000):
    eth = b"\xff" * 6 + bytes.fromhex("001122334455") + b"\x88\xa4"
    datagram = struct.pack("<BB4sHHH", cmd, index,
                           address.to_bytes(4, "little"),
                           len(payload), 0, 0)
    datagram += payload + struct.pack("<H", 0)
    ecat_header = struct.pack("<H", len(datagram) & 0x7FF)
    return eth + ecat_header + datagram

pdo = struct.pack("<Hih", 0x000F, 12345, 8)  # controlword, target, mode
frame = build_frame(pdo)
print("frame bytes:", len(frame))
print("EtherType:", frame[12:14].hex())
''',
            "Ethernet 头 14 字节，EtherCAT 头 2 字节，然后是 datagram。`0x88A4` 是 EtherCAT 的 EtherType；`0x000F` 是 CiA402 的 Enable operation 控制字。",
        ),
        seg(
            "解析帧",
            r'''
length = struct.unpack_from("<H", frame, 14)[0] & 0x7FF
offset = 16
cmd, index, addr, plen, flags, irq = struct.unpack_from("<BB4sHHH", frame, offset)
payload = frame[offset + 12:offset + 12 + plen]
wkc = struct.unpack_from("<H", frame, offset + 12 + plen)[0]
parsed = {
    "type": frame[12:14].hex(),
    "ecat_len": length,
    "cmd": cmd, "index": index,
    "address": int.from_bytes(addr, "little"),
    "payload": payload, "wkc": wkc,
}
print(parsed)
metric("PDO 字节数", plen)
''',
            "datagram 头 12 字节：命令、索引、4 字节地址、长度、标志、中断；后面是数据，最后 2 字节是工作计数器 WKC。真实解析还要处理多个 datagram 和字节对齐。",
        ),
        seg(
            "PDO 解包",
            r'''
cw, target, mode = struct.unpack("<Hih", payload)
print("controlword: 0x%04X" % cw)
print("target_position:", target)
print("mode:", mode, "(8 = CSP)")
metric("目标位置", target)
''',
            "PDO 是“约定好的字节布局”。主站和从站必须使用同一个 ESI/对象字典映射，否则同样的字节会被解释成不同的变量。CSP=8、CSV=9、CST=10 是 CiA402 的周期同步模式。",
        ),
        seg(
            "走一遍 CiA402 使能状态机",
            r'''
sequence = [
    ("DISABLE_VOLTAGE", 0x0000, "NOT_READY"),
    ("SHUTDOWN", 0x0006, "READY_TO_SWITCH_ON"),
    ("SWITCH_ON", 0x0007, "SWITCHED_ON"),
    ("ENABLE_OPERATION", 0x000F, "OPERATION_ENABLED"),
]
state = "NOT_READY"
states = []
for name, command, expected in sequence:
    if command == 0x0000:
        state = "NOT_READY"
    else:
        state = expected
    states.append((name, command, state))
    print("%-18s cw=0x%04X -> %s" % (name, command, state))
metric("最终状态", state)
''',
            "真实状态机还要处理 Quick stop、Fault、Fault reset、Disabled operation 等分支。使能顺序错了，驱动器会拒绝或报警；现场先看状态字，再看控制字。",
        ),
        seg(
            "画帧结构与状态时间线",
            r'''
canvas = np.full((520, 1080, 3), 18, np.uint8)
blocks = [("Ethernet", 60, 150), ("ECAT", 220, 110), ("Datagram", 340, 260),
          ("PDO", 610, 260), ("WKC", 880, 100)]
for name, x, w in blocks:
    cv2.rectangle(canvas, (x, 70), (x + w, 150), (80, 220, 160), 2)
    cv2.putText(canvas, name, (x + 10, 118), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (230, 230, 230), 1, cv2.LINE_AA)
for i, (name, cw, st) in enumerate(states):
    y = 230 + i * 60
    cv2.rectangle(canvas, (60, y), (300, y + 36), (70, 70, 70), -1)
    cv2.putText(canvas, name, (70, y + 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(canvas, "-> " + st, (320, y + 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (120, 230, 180), 1, cv2.LINE_AA)
result = canvas
''',
            "把帧布局和状态迁移画出来，方便和 EtherCAT 主站/驱动器同事对齐。真实项目还要抓包看 WKC、DC 偏差和丢帧。",
        ),
    ],
    tests=[
        test("EtherType 正确", "frame[12:14] == b'\\x88\\xa4'"),
        test("PDO 可解析", "parsed['payload'] == pdo and parsed['wkc'] == 0"),
        test("状态机使能", "state == 'OPERATION_ENABLED'"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    tasks=[
        task("dev", "加一个 datagram", "在同一帧里拼两个 datagram，写一个循环解析。"),
        task("dev", "解析状态字", "查 CiA402 状态字位定义，写 `is_enabled(statusword)`。"),
        task("observe", "改模式", "把 mode 改成 9/10，解释 CSV/CST 与 CSP 的区别。"),
    ],
    quiz_items=[
        quiz("EtherCAT 的 EtherType 是？", ["0x0800", "0x88A4", "0x0806", "0x8100"], 1,
             "0x88A4 标识 EtherCAT。"),
        quiz("PDO 通常传什么？", ["参数", "周期过程数据", "固件", "IP 地址"], 1,
             "PDO 传控制字/目标位置/状态字/实际位置等周期数据。"),
        quiz("CSP 的含义？", ["周期同步位置", "周期同步速度", "周期同步转矩", "回零"], 0,
             "CSP=Cyclic Synchronous Position，周期同步位置。"),
    ],
    industry="EtherCAT 广泛用于伺服、机器人关节、CNC、锂电和半导体设备。主站栈（TwinCAT、SOEM、IgH）和从站 ESI 文件是工程落地的核心。",
    career="运动控制开发要能读 ESI、配 PDO、写状态机；调控岗位要会看 WKC、DC 偏差、OP 状态和驱动器报警。",
    next_step="下一课把 CSP/CSV/CST 和跟随误差放进一个驱控一体仿真。",
)

L4 = lesson(
    "servo-cst",
    "驱控一体：CSP/CSV/CST 与跟随误差",
    "梯形速度规划、位置/速度前馈、跟随误差、伺服整定",
    chapter="motor",
    difficulty=4,
    minutes=50,
    tags=["伺服", "CSP", "跟随误差"],
    objectives=[
        "生成梯形速度/位置曲线",
        "模拟位置环 + 速度前馈，计算跟随误差",
        "理解 CSP、CSV、CST 三种周期同步模式的差别",
    ],
    concept=[
        P("驱控一体把伺服控制、编码器、EtherCAT 从站和功率级装进一个驱动器。上位机只下发周期同步指令，驱动器内部跑电流环、速度环、位置环。"),
        TABLE(
            ["模式", "主站下发", "驱动器内部", "典型场景"],
            [
                ["CSP", "目标位置", "位置环 + 速度环 + 电流环", "点位、插补"],
                ["CSV", "目标速度", "速度环 + 电流环", "连续轨迹、传送带"],
                ["CST", "目标转矩/电流", "电流环", "力控、张力控制"],
            ],
        ),
        FORMULA("e_follow = x_cmd − x_actual", "跟随误差；不是编码器误差"),
        NOTE("跟随误差与稳态误差", "加减速时跟随误差会变大，匀速时应该很小。调参不是把 Kp 无限加大，否则会震荡、发热、甚至触发过流。", "warn"),
    ],
    walkthrough=[
        seg(
            "梯形速度规划",
            r'''
import math
import cv2
import numpy as np

def trapezoid(distance, vmax, accel, dt=0.001):
    ta = vmax / accel
    da = 0.5 * accel * ta * ta
    if 2 * da > distance:
        ta = math.sqrt(distance / accel)
        vmax = accel * ta
        da = 0.5 * accel * ta * ta
    tc = (distance - 2 * da) / vmax
    total = 2 * ta + tc
    steps = int(total / dt) + 200
    pos, vel = [], []
    p = 0.0
    for i in range(steps):
        t = i * dt
        if t < ta:
            v = accel * t
        elif t < ta + tc:
            v = vmax
        elif t < total:
            v = max(0.0, vmax - accel * (t - ta - tc))
        else:
            v = 0.0
        p += v * dt
        pos.append(p)
        vel.append(v)
    return np.array(pos), np.array(vel)

pos, vel = trapezoid(800.0, float(p["vmax"]), float(p["accel"]))
print("规划点数:", len(pos), "终点:", round(float(pos[-1]), 2))
''',
            "梯形规划分加速、匀速、减速三段；距离太短时自动变成三角形。真实控制器还会用 S 曲线限制加加速度，减少冲击。",
        ),
        seg(
            "二阶级伺服模型 + 位置前馈",
            r'''
dt = 0.001
kp = float(p["kp"])
tau = 0.02
amax = 20000.0
p, v = 0.0, 0.0
history = []
for i in range(len(pos)):
    err = pos[i] - p
    v_ref = vel[i] + kp * err
    acc = max(-amax, min(amax, (v_ref - v) / tau))
    v += acc * dt
    p += v * dt
    history.append((pos[i] - p, p, v))
max_follow = max(abs(h[0]) for h in history)
final_err = abs(pos[-1] - p)
print("最大跟随误差: %.3f mm" % max_follow)
print("终点误差: %.3f mm" % final_err)
metric("最大跟随误差(mm)", round(float(max_follow), 3))
metric("终点误差(mm)", round(float(final_err), 3))
''',
            "`vel[i]` 是速度前馈，`kp*err` 是位置修正。没有前馈时，位置环要靠误差“追”速度，跟随误差会明显变大；前馈让误差不用很大就能跟上。",
        ),
        seg(
            "对比无前馈",
            r'''
p2, v2 = 0.0, 0.0
follow2 = []
for i in range(len(pos)):
    err = pos[i] - p2
    v_ref = kp * err
    acc = max(-amax, min(amax, (v_ref - v2) / tau))
    v2 += acc * dt
    p2 += v2 * dt
    follow2.append(abs(pos[i] - p2))
print("无前馈最大跟随误差: %.3f mm" % max(follow2))
metric("无前馈跟随(mm)", round(float(max(follow2)), 3))
''',
            "前馈把“已知的规划速度”直接加到速度指令，反馈只负责修残差。工业伺服通常同时有速度前馈、加速度前馈和摩擦补偿。",
        ),
        seg(
            "画位置/速度/误差",
            r'''
canvas = np.full((560, 1080, 3), 18, np.uint8)
def plot(vals, color, lo, hi, y0, h, label):
    pts = []
    for i, val in enumerate(vals):
        x = 70 + int(i * 920 / (len(vals) - 1))
        y = y0 + h - int((val - lo) / (hi - lo) * h)
        pts.append((x, y))
    cv2.polylines(canvas, [np.array(pts, np.int32)], False, color, 2)
    cv2.putText(canvas, label, (70, y0 - 8), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 1, cv2.LINE_AA)

plot(pos, (80, 220, 255), 0, 850, 50, 150, "position command")
plot([h[1] for h in history], (120, 240, 140), 0, 850, 50, 150, "position actual")
plot(vel, (120, 240, 140), 0, 650, 260, 120, "velocity")
plot([h[0] for h in history], (255, 180, 120), -4, 4, 440, 90, "following error")
result = canvas
''',
            "跟随误差曲线在加速/减速段最大、匀速段最小。如果匀速段误差也很大，先查前馈、摩擦、编码器方向和 PID。",
        ),
        seg(
            "三种模式怎么选",
            r'''
print("CSP: 下发位置，适合点位/插补，轨迹由驱动器插值")
print("CSV: 下发速度，适合连续轨迹/传送带跟随")
print("CST: 下发转矩/电流，适合力控/张力")
print("本仿真对应 CSP + 速度前馈")
''',
            "模式选择取决于谁负责轨迹规划：主站负责轨迹就用 CSP/CSV；需要力控就用 CST。别在 CSP 模式下频繁变速下发，容易造成冲击。",
        ),
    ],
    tests=[
        test("最大跟随误差小于 5mm", "max_follow < 5.0"),
        test("终点误差小于 0.5mm", "final_err < 0.5"),
        test("前馈优于无前馈", "max_follow < max(follow2)"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    params=[
        param("kp", "位置环 Kp", 20, 5, 60, 1),
        param("vmax", "最大速度（mm/s）", 600, 200, 1500, 50),
        param("accel", "加速度（mm/s²）", 3000, 1000, 10000, 500),
    ],
    tasks=[
        task("dev", "加 S 曲线", "把梯形速度改成七段 S 曲线，比较最大跟随误差。"),
        task("dev", "加摩擦", "在速度环加一个常数摩擦项，观察匀速段误差。"),
        task("observe", "降低 Kp", "把 Kp 调到 5，观察跟随误差和震荡。"),
    ],
    quiz_items=[
        quiz("CSP 下发什么？", ["位置", "速度", "转矩", "电流"], 0,
             "CSP=Cyclic Synchronous Position。"),
        quiz("跟随误差的定义？", ["编码器分辨率", "指令位置−实际位置", "电流误差", "速度误差"], 1,
             "跟随误差是位置指令与实际位置的差。"),
        quiz("速度前馈的作用？", ["替代反馈", "让系统不用靠大误差追上速度", "增加摩擦", "降低母线电压"], 1,
             "前馈提供主要速度指令，反馈只修残差。"),
    ],
    industry="伺服压机、机器人关节、CNC 进给、锂电卷绕都依赖 CSP/CSV/CST 和跟随误差控制。调参要结合机械刚度、负载惯量和工艺公差。",
    career="运动控制开发要能配 PDO、写模式切换和回零；调控岗位要会看跟随误差、整定增益、判断机械共振和编码器问题。",
    next_step="下一章用 3 个月计划把这些串起来，并复刻一个 GitHub 机器人视觉项目。",
)

CHAPTER = chapter(
    "motor", "07", "电机与运动控制",
    "从 FOC 的坐标变换、电流环，到 EtherCAT PDO/CiA402，再到驱控一体的 CSP/CSV/CST。",
    [L1, L2, L3, L4],
    color="#f472b6", icon="07",
)
