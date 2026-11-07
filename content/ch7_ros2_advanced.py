# -*- coding: utf-8 -*-
"""第七章：ROS2 进阶（launch、同步、executor、参数、日志）。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "ros2-launch-timer",
    "Python Launch 与定时器：一次启动一组节点",
    "LaunchDescription、Node、TimerAction、定时器回调与启动顺序",
    chapter="ros2",
    difficulty=3,
    minutes=40,
    tags=["ROS2", "launch", "timer"],
    objectives=[
        "读懂 Python launch 文件的结构",
        "用 TimerAction 延迟启动节点",
        "模拟定时器节拍，理解 launch 与 timer 的区别",
    ],
    concept=[
        P("`ros2 run` 一次只启动一个节点；真实系统要同时启动相机、检测、规划、控制。Python launch 用代码描述“启动哪些节点、传什么参数、何时启动”，还能加事件和条件。"),
        CODE(
            """from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction

def generate_launch_description():
    detector = Node(
        package='vision_node',
        executable='detector',
        parameters=[{'confidence': 0.6}],
        remappings=[('image', '/camera/image_raw')],
    )
    return LaunchDescription([
        detector,
        TimerAction(period=2.0, actions=[Node(
            package='vision_node', executable='planner')]),
    ])""",
            "python",
        ),
        NOTE("launch 不是节点", "launch 文件只负责“启动/配置”，本身不处理消息。节点里的 `create_timer` 才是周期回调；两者经常一起出现，但职责不同。", "tip"),
    ],
    walkthrough=[
        seg(
            "描述启动项",
            r'''
from dataclasses import dataclass

@dataclass
class LaunchItem:
    name: str
    delay: float = 0.0
    period: float = 0.0

items = [
    LaunchItem("camera", 0.0, 0.0),
    LaunchItem("detector", 0.5, 0.0),
    LaunchItem("planner", 2.0, 0.0),
    LaunchItem("watchdog", 0.0, 1.0),
]
print(items)
''',
            "每个启动项对应一个 Node；`delay` 是延迟启动，`period` 是节点内定时器的周期。真实 launch 里这些字段会变成 `TimerAction` 和节点参数。",
        ),
        seg(
            "模拟启动与定时器",
            r'''
def simulate(items, duration=5.0):
    events = []
    for item in items:
        events.append((item.delay, "start", item.name))
        if item.period > 0:
            t = item.delay + item.period
            while t <= duration:
                events.append((t, "tick", item.name))
                t += item.period
    return sorted(events, key=lambda e: (e[0], e[1]))

timeline = simulate(items)
for t, kind, name in timeline:
    print("%.1fs %-5s %s" % (t, kind, name))
metric("事件数", len(timeline))
''',
            "定时器从启动后开始计时，按周期重复；`TimerAction` 是延迟“启动节点”，不是节点内的周期回调。排错时先确认是“没启动”还是“启动了但定时器没触发”。",
        ),
        seg(
            "检查启动顺序",
            r'''
starts = [name for t, kind, name in timeline if kind == "start"]
print("启动顺序:", starts)
assert starts == ["camera", "watchdog", "detector", "planner"] or starts[0] == "camera"
''',
            "相机通常先启动，检测依赖图像；规划可以延迟等检测就绪。不要用 `sleep` 硬等，优先用生命周期/事件/参数确认就绪。",
        ),
        seg(
            "常用 launch 命令",
            r'''
print("ros2 launch vision_bringup bringup.launch.py")
print("ros2 launch vision_bringup bringup.launch.py use_sim:=true")
print("ros2 launch --show-args vision_bringup bringup.launch.py")
''',
            "`--show-args` 能看 launch 参数，`use_sim:=true` 是启动参数覆盖。现场先看参数默认值，避免“以为启动了、其实用了另一套配置”。",
        ),
    ],
    tests=[
        test("四个启动项", "len(items) == 4"),
        test("有定时器事件", "sum(1 for e in timeline if e[1] == 'tick') >= 4"),
        test("相机先启动", "starts[0] == 'camera'"),
        test("事件按时间排序", "timeline == sorted(timeline, key=lambda e: (e[0], e[1]))"),
    ],
    tasks=[
        task("dev", "加条件启动", "加一个 `use_sim` 参数，为 True 时启动仿真相机，否则启动真实相机。"),
        task("dev", "改周期", "把 watchdog 周期改成 0.5s，观察事件数。"),
        task("observe", "删掉延迟", "把 planner 的 delay 改成 0，观察启动顺序变化。"),
    ],
    quiz_items=[
        quiz("launch 文件的作用？", ["处理图像", "启动/配置节点", "编译 C++", "标定相机"], 1,
             "launch 负责编排启动，不处理业务消息。"),
        quiz("TimerAction 与 create_timer 的区别？", ["一样", "前者延迟启动，后者节点内周期回调", "后者只用于 C++", "前者只能启动一次"], 1,
             "TimerAction 是 launch 动作；create_timer 是节点内定时器。"),
        quiz("查看 launch 参数用？", ["ros2 topic echo", "--show-args", "colcon test", "ros2 bag"], 1,
             "`ros2 launch --show-args` 列出可传参数。"),
    ],
    industry="真实机器人 bringup 常用 launch 组织相机、底盘、定位、导航、视觉；多机系统还会用 group + namespace 批量启动。",
    career="开发型岗位要写可配置 launch；调控岗位要会用 launch 参数切换真实/仿真、相机型号和工位。",
    next_step="下一课处理多传感器时间同步和 executor/回调组。",
)

L2 = lesson(
    "ros2-sync-executor",
    "时间同步与 Executor：多传感器回调怎么不打架",
    "message_filters 近似同步、回调组、单线程/多线程 executor",
    chapter="ros2",
    difficulty=5,
    minutes=50,
    tags=["ROS2", "message_filters", "executor"],
    objectives=[
        "用时间戳把相机和雷达消息配对",
        "说清 MutuallyExclusive / Reentrant 回调组的区别",
        "知道 MultiThreadedExecutor 的收益和风险",
    ],
    concept=[
        P("相机 30 Hz、雷达 10 Hz，消息不会同时到。`message_filters` 按时间戳做近似同步，只有配对成功才进回调；否则视觉和点云各处理各的，融合结果会错位。"),
        FORMULA("|t_cam − t_lidar| ≤ slop", "ApproximateTime 的配对条件"),
        CODE(
            """import message_filters
from sensor_msgs.msg import Image, PointCloud2

cam_sub = message_filters.Subscriber(self, Image, 'image')
lidar_sub = message_filters.Subscriber(self, PointCloud2, 'points')
sync = message_filters.ApproximateTimeSynchronizer(
    [cam_sub, lidar_sub], queue_size=10, slop=0.05)
sync.registerCallback(self.on_pair)""",
            "python",
        ),
        NOTE("回调组不是线程池", "`MutuallyExclusiveCallbackGroup` 保证组内回调不并发；`ReentrantCallbackGroup` 允许并发。多线程 executor 只有在回调组允许时才真正并行。", "warn"),
    ],
    walkthrough=[
        seg(
            "按时间戳配对",
            r'''
def sync_pairs(camera, lidar, slop=0.05):
    pairs = []
    used = set()
    for tc, cam in camera:
        best = None
        for i, (tl, lidar_msg) in enumerate(lidar):
            if i in used:
                continue
            dt = abs(tc - tl)
            if dt <= slop and (best is None or dt < best[0]):
                best = (dt, i, lidar_msg)
        if best:
            used.add(best[1])
            pairs.append((cam, best[2], best[0]))
    return pairs

camera = [(0.00, "cam0"), (0.033, "cam1"), (0.066, "cam2")]
lidar = [(0.01, "lidar0"), (0.08, "lidar1")]
pairs = sync_pairs(camera, lidar, 0.05)
print(pairs)
metric("同步对数", len(pairs))
''',
            "这是 ApproximateTime 的简化版：按时间差找最近邻，超过 slop 就丢弃。真实实现会维护队列、处理乱序和丢帧，但核心就是“时间差 + 队列”。",
        ),
        seg(
            "检查配对质量",
            r'''
for cam, lidar_msg, dt in pairs:
    print("%s <-> %s  dt=%.3fs" % (cam, lidar_msg, dt))
print("最大时间差:", max(dt for _, _, dt in pairs))
''',
            "配对数太少，可能是 slop 太小、频率不匹配或时间戳没同步；配错则可能是队列太深/时间基准不一致。先看 `ros2 topic hz` 和 `ros2 topic delay`。",
        ),
        seg(
            "单线程 vs 多线程",
            r'''
callbacks = [("image", 0.02), ("points", 0.05), ("control", 0.01)]
single = sum(t for _, t in callbacks)
multi = max(t for _, t in callbacks)
print("单线程总耗时: %.2fs" % single)
print("多线程理论耗时: %.2fs" % multi)
''',
            "多线程能重叠 I/O/计算，但共享数据要加锁；回调组配置错会出现“看似并行、其实串行”或“数据竞争”。先用单线程跑通，再按瓶颈拆组。",
        ),
        seg(
            "executor 选择",
            r'''
print("SingleThreadedExecutor: 简单、可预测，适合控制")
print("MultiThreadedExecutor: 适合图像/点云并行，但要管并发")
print("回调组: MutuallyExclusive / Reentrant")
''',
            "控制回路通常要确定性，优先单线程或独立线程；感知可以多线程。不要把“多线程”当性能银弹，锁竞争和回调顺序会带来新问题。",
        ),
    ],
    tests=[
        test("配对成功", "len(pairs) >= 2"),
        test("时间差在 slop 内", "all(dt <= 0.05 for _, _, dt in pairs)"),
        test("不重复使用雷达", "len({id(l) for _, l, _ in pairs}) == len(pairs)"),
        test("多线程更快", "multi < single"),
    ],
    tasks=[
        task("dev", "改成最近邻", "当前按相机顺序找；改成全局最近邻，比较配对数。"),
        task("dev", "加队列", "给 sync_pairs 加固定长度队列，模拟丢帧/乱序。"),
        task("observe", "调 slop", "把 slop 改成 0.01/0.1，观察配对数变化。"),
    ],
    quiz_items=[
        quiz("ApproximateTime 的作用？", ["精确对齐", "按时间差近似配对", "压缩图像", "编译"], 1,
             "允许 slop 内的时间差。"),
        quiz("回调组的作用？", ["控制回调并发/互斥", "改话题名", "生成接口", "编译"], 0,
             "决定 executor 能否并发执行组内回调。"),
        quiz("控制回路更适合？", ["尽量多线程", "确定性/单线程或独立线程", "不用 executor", "只跑 launch"], 1,
             "控制要可预测，避免锁和调度抖动。"),
    ],
    industry="多传感器融合（相机+雷达+IMU）、视觉伺服、自动驾驶都绕不开时间同步；时间戳错 50ms，高速场景就会差几厘米到几十厘米。",
    career="开发型岗位要设计同步/并发；调控岗位要会看时间戳、频率、延迟，判断是丢帧还是时间基准问题。",
    next_step="下一课用参数和日志让节点可配置、可排查。",
)

L3 = lesson(
    "ros2-params-logging",
    "参数与日志：让节点可配置、可排查",
    "declare/get/set、YAML 参数、日志级别、throttle、条件日志",
    chapter="ros2",
    difficulty=3,
    minutes=40,
    tags=["ROS2", "parameters", "logging"],
    objectives=[
        "声明/读取/修改参数，拒绝未声明参数",
        "用 YAML 覆盖节点参数",
        "用日志级别和 throttle 控制输出",
    ],
    concept=[
        P("参数是节点的运行时配置：阈值、相机 ID、增益、话题名。日志是节点的可观测性：谁在什么条件下输出了什么。两者都是“现场可调”的基础。"),
        CODE(
            """# Python: 声明与读取
self.declare_parameter('confidence', 0.6)
self.declare_parameter('camera_id', 0)
conf = self.get_parameter('confidence').value

# YAML 覆盖
detector:
  ros__parameters:
    confidence: 0.75
    camera_id: 1""",
            "python",
        ),
        CODE(
            """// C++: 日志
RCLCPP_INFO(this->get_logger(), "confidence=%.2f", conf);
RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 2000,
                     "image timeout");""",
            "cpp",
        ),
    ],
    walkthrough=[
        seg(
            "参数存储",
            r'''
class ParamStore:
    def __init__(self):
        self.values = {}
    def declare(self, name, default):
        if name in self.values:
            raise ValueError("already declared: " + name)
        self.values[name] = default
    def get(self, name):
        if name not in self.values:
            raise KeyError("undeclared: " + name)
        return self.values[name]
    def set(self, name, value):
        if name not in self.values:
            raise KeyError("undeclared: " + name)
        self.values[name] = value

params = ParamStore()
params.declare("confidence", 0.6)
params.declare("camera_id", 0)
print(params.get("confidence"))
''',
            "参数必须先声明再使用。未声明就 `get` 在真实 ROS2 会报错；这看起来麻烦，但能避免拼写错误和“改了不生效”。",
        ),
        seg(
            "修改与校验",
            r'''
params.set("confidence", 0.75)
print("new confidence:", params.get("confidence"))
missing_error = False
try:
    params.get("missing")
except KeyError as exc:
    missing_error = True
    print("expected error:", exc)
metric("confidence", params.get("confidence"))
''',
            "参数修改后要触发回调/重建算法，不能只改值不生效。阈值类参数要做范围校验（0–1），否则现场会传出非法值。",
        ),
        seg(
            "日志级别",
            r'''
LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
def log(level, text, current="INFO"):
    if LEVELS[level] >= LEVELS[current]:
        print("[%s] %s" % (level, text))

log("DEBUG", "frame 001", "INFO")
log("INFO", "detector started", "INFO")
log("WARN", "image timeout", "INFO")
''',
            "默认 INFO，现场排查临时开 DEBUG；高频日志用 throttle，避免刷爆磁盘和终端。日志要带节点名、时间、关键数值。",
        ),
        seg(
            "参数/日志排查顺序",
            r'''
print("1. ros2 param list / get")
print("2. ros2 param set / dump")
print("3. ros2 run ... --ros-args --log-level debug")
print("4. 看时间戳/频率，不只看一行日志")
''',
            "先确认参数值，再看日志级别，最后看数据频率和时间戳。不要用 `print` 代替日志，也不要在控制循环里每帧打 INFO。",
        ),
    ],
    tests=[
        test("参数已声明", "params.get('confidence') == 0.75"),
        test("未声明参数报错", "missing_error is True"),
        test("日志过滤正确", "LEVELS['DEBUG'] < LEVELS['INFO']"),
        test("参数表非空", "len(params.values) == 2"),
    ],
    tasks=[
        task("dev", "加范围校验", "set confidence 时限制 0~1，非法值抛 ValueError。"),
        task("dev", "加 throttle", "实现每 2 秒最多打印一次 WARN 的 throttle。"),
        task("observe", "参数覆盖", "在真实 ROS2 用 `--ros-args -p confidence:=0.8` 启动，看节点是否读到。"),
    ],
    quiz_items=[
        quiz("参数必须先？", ["声明", "删除", "重命名", "编译"], 0,
             "先 declare 再 get/set。"),
        quiz("高频日志应该？", ["全打 INFO", "用 throttle/DEBUG", "删掉日志", "改 print"], 1,
             "throttle 限制频率，DEBUG 按需开启。"),
        quiz("参数改了不生效，先查？", ["相机", "param list/get 和回调", "网络", "显卡"], 1,
             "先确认参数值，再确认修改后是否触发重建。"),
    ],
    industry="现场调试大量时间花在“参数不对/日志不够”。好的节点会把关键参数、频率、延迟、失败原因打出来，而不是只报“失败”。",
    career="开发型岗位要设计参数和日志；调控岗位要会 `ros2 param`、`--log-level`、`ros2 topic hz/delay` 三件套。",
    next_step="下一章进入工程层：package.xml、CMakeLists、rosidl、colcon。",
)

CHAPTER = chapter(
    "ros2-advanced", "07", "ROS2 进阶",
    "launch 编排、定时器、多传感器时间同步、executor/回调组、参数与日志。",
    [L1, L2, L3],
    color="#a78bfa", icon="07",
)
