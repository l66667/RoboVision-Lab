# -*- coding: utf-8 -*-
"""第六章：ROS2 基础（发布订阅、接口、命名空间）。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "ros2-pubsub",
    "ROS2 发布订阅：节点、话题与回调",
    "Node / Topic / Publisher / Subscriber、QoS、spin 与最小可运行模型",
    chapter="ros2",
    difficulty=2,
    minutes=35,
    tags=["ROS2", "Pub/Sub", "rclpy"],
    objectives=[
        "说清节点、话题、发布者、订阅者、回调的关系",
        "读懂一个 rclpy 发布/订阅节点和对应的 C++ 版本",
        "用纯 Python 模拟消息投递，理解 spin 在做什么",
    ],
    concept=[
        P("ROS2 的通信骨架是“节点 + 话题”：发布者往话题写消息，订阅者从话题读消息，中间由 DDS 负责发现和传输。节点不需要知道对方是谁，只认话题名和消息类型。"),
        TABLE(
            ["概念", "作用", "代码里对应"],
            [
                ["Node", "一个进程/模块", "`rclpy.init` + `Node`"],
                ["Topic", "带类型的消息通道", "`create_publisher` / `create_subscription`"],
                ["QoS", "可靠性/队列/寿命", "`QoSProfile`"],
                ["spin", "让节点处理回调", "`rclpy.spin(node)`"],
                ["Executor", "调度回调的线程/队列", "`SingleThreadedExecutor`"],
            ],
        ),
        CODE(
            """# Python: 最小发布者
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(0.5, self.tick)
    def tick(self):
        msg = String()
        msg.data = 'hello'
        self.pub.publish(msg)

rclpy.init()
rclpy.spin(Talker())""",
            "python",
        ),
        CODE(
            """// C++: 同一个发布者
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Talker : public rclcpp::Node {
public:
  Talker() : Node("talker") {
    pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(500),
      [this]() {
        std_msgs::msg::String msg;
        msg.data = "hello";
        pub_->publish(msg);
      });
  }
private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};""",
            "cpp",
        ),
        NOTE("话题名不是随便起的", "`chatter` 是相对名，会受命名空间影响；`/chatter` 是绝对名。多机器人系统里通常用 `/robot1/chatter` 这样的命名空间隔离。", "tip"),
    ],
    walkthrough=[
        seg(
            "用纯 Python 模拟节点与话题",
            r'''
from dataclasses import dataclass

@dataclass
class String:
    data: str

class MiniPublisher:
    def __init__(self, node, topic):
        self.node = node
        self.topic = topic
    def publish(self, msg):
        self.node.publish(self.topic, msg)

class MiniNode:
    def __init__(self, name):
        self.name = name
        self.subscribers = {}

    def create_publisher(self, topic):
        self.subscribers.setdefault(topic, [])
        return MiniPublisher(self, topic)

    def create_subscription(self, topic, callback):
        self.subscribers.setdefault(topic, []).append(callback)

    def publish(self, topic, msg):
        for callback in self.subscribers.get(topic, []):
            callback(msg)

    def spin_once(self):
        return None

print("node ready")
''',
            "这个 `MiniNode` 把 DDS 的发现和传输省掉，只保留“话题名 → 回调列表”的核心。理解了这个映射，再看 `rclpy` 就不神秘了。",
        ),
        seg(
            "订阅并接收消息",
            r'''
received = []
def on_message(msg):
    received.append(msg.data)

node = MiniNode("listener")
node.create_subscription("/chatter", on_message)
publisher = node.create_publisher("/chatter")

for i in range(3):
    publisher.publish(String("hello %d" % i))
node.spin_once()
print(received)
metric("收到消息数", len(received))
''',
            "发布者调用 `publish` 时，`MiniNode` 直接遍历该话题的回调；真实 ROS2 里这一步由 executor 从 DDS 队列取出消息后调用。`spin` 就是“不断取消息、执行回调”的循环。",
        ),
        seg(
            "QoS 直觉",
            r'''
qos = {"reliability": "reliable", "depth": 10}
print("QoS:", qos)
print("传感器数据常用 best_effort；控制/服务常用 reliable")
''',
            "QoS 不匹配是 ROS2 很常见的“收不到数据”原因：发布者 best_effort、订阅者 reliable 可能不兼容。先 `ros2 topic info -v` 看两端 QoS，再改代码。",
        ),
        seg(
            "节点图",
            r'''
print("talker --[/chatter]--> listener")
print("一个话题可以有多个发布者和多个订阅者")
''',
            "ROS2 允许一个话题多发布/多订阅。设计接口时要明确“谁拥有数据、谁消费数据”，避免多个节点同时写同一个控制话题。",
        ),
    ],
    tests=[
        test("收到 3 条消息", "len(received) == 3"),
        test("消息内容正确", "received[0] == 'hello 0'"),
        test("节点有话题", "len(node.subscribers) >= 1"),
    ],
    tasks=[
        task("dev", "加第二个订阅者", "给 `/chatter` 再加一个回调，观察两个回调都被调用。"),
        task("dev", "加命名空间", "把话题改成 `/robot1/chatter`，模拟多机器人隔离。"),
        task("tune", "读代码找错", "如果先 `publish` 再 `create_subscription`，会收到几条？先预测，再改顺序运行验证。"),
        task("observe", "看 QoS", "在真实 ROS2 环境运行 `ros2 topic info /chatter -v`，对比发布/订阅 QoS。"),
    ],
    quiz_items=[
        quiz("订阅者靠什么找到发布者？", ["IP 地址", "话题名 + 消息类型 + DDS 发现", "端口", "文件路径"], 1,
             "ROS2 通过 DDS 发现同话题、同类型的端点。"),
        quiz("spin 的作用？", ["编译", "处理回调/消息", "标定相机", "启动编译器"], 1,
             "spin 让 executor 持续取消息并调用回调。"),
        quiz("传感器数据常用哪种 QoS？", ["reliable", "best_effort", "transient_local", "durability"], 1,
             "best_effort 允许丢帧，适合高频传感器。"),
    ],
    industry="ROS2 是移动机器人、机械臂、自动驾驶中间件的主流选择。发布订阅是所有上层功能（感知、定位、规划、控制）的骨架。",
    career="机器人软件工程师要能设计话题、QoS、命名空间；调控岗位要会用 `ros2 topic` 工具排查“有没有数据、类型对不对、QoS 兼不兼容”。",
    next_step="下一课定义自己的消息和服务，而不是只用 String。",
)

L2 = lesson(
    "ros2-msg-srv",
    "自定义消息与服务：让接口表达业务",
    "msg/srv 定义、字段类型、rosidl 生成、服务请求/响应",
    chapter="ros2",
    difficulty=3,
    minutes=40,
    tags=["ROS2", "msg", "srv"],
    objectives=[
        "写出一个 Detection.msg 和 Detect.srv",
        "说清 msg 与 srv 的使用场景",
        "理解 rosidl_generate_interfaces 与包依赖",
    ],
    concept=[
        P("`std_msgs/String` 只能传字符串；真实项目要传检测框、位姿、抓取请求。自定义接口把字段、类型、语义固定下来，发布者和订阅者才能独立开发。"),
        CODE(
            """# Detection.msg
string label
float32 x
float32 y
float32 score

# Detect.srv
string color
---
bool success
Detection detection""",
            "text",
        ),
        P("`.msg` 用于话题/服务响应里的数据结构；`.srv` 用 `---` 分隔请求和响应。生成接口需要在 `package.xml` 声明 `rosidl_default_generators`，在 CMake 调 `rosidl_generate_interfaces`。"),
        CODE(
            """# CMakeLists.txt（接口包片段）
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Detection.msg"
  "srv/Detect.srv"
)
ament_export_dependencies(rosidl_default_runtime)""",
            "cmake",
        ),
    ],
    walkthrough=[
        seg(
            "用 dataclass 表达消息",
            r'''
from dataclasses import dataclass

@dataclass
class Detection:
    label: str
    x: float
    y: float
    score: float

det = Detection("red", 320.5, 180.0, 0.92)
print(det)
metric("检测标签", det.label)
''',
            "生成后的 ROS2 消息类，字段访问方式和 dataclass 很像。先用 dataclass 把业务字段定清楚，再写 `.msg`，能少改几轮。",
        ),
        seg(
            "服务请求/响应",
            r'''
@dataclass
class DetectRequest:
    color: str

@dataclass
class DetectResponse:
    success: bool
    detection: object

def handle(req):
    if req.color == "red":
        return DetectResponse(True, det)
    return DetectResponse(False, None)

resp = handle(DetectRequest("red"))
print(resp)
''',
            "服务是“请求—响应”，适合“查一次/做一次”的动作；话题是持续流，适合传感器和状态。抓取请求常用 action（带反馈/取消），简单查询用 srv。",
        ),
        seg(
            "字段类型与边界",
            r'''
fields = {"label": "string", "x": "float32", "y": "float32", "score": "float32"}
print(fields)
print("score 约定 0~1；坐标单位在接口注释里写清")
''',
            "接口一旦发布就很难改：字段类型、单位、坐标系、score 含义都要写进注释。团队里最常见的事故是“米/毫米”“像素/毫米”没约定。",
        ),
        seg(
            "生成顺序",
            r'''
print("1. 定义 msg/srv")
print("2. package.xml 声明 rosidl_default_generators / runtime")
print("3. CMakeLists rosidl_generate_interfaces")
print("4. colcon build 生成 Python/C++ 接口")
''',
            "自定义接口包必须先编译，依赖它的包才能找到头文件/模块。多包工作空间里，colcon 会根据依赖自动排序；`--packages-select` 只编一个包时，依赖可能没编，常见报错就在这里。",
        ),
    ],
    tests=[
        test("消息字段正确", "det.label == 'red' and det.score > 0.9"),
        test("服务成功", "resp.success is True"),
        test("服务返回检测", "resp.detection is det"),
        test("字段类型表完整", "set(fields) == {'label', 'x', 'y', 'score'}"),
    ],
    tasks=[
        task("dev", "加 yaw 字段", "给 Detection 加 `float32 yaw`，并更新 dataclass 和字段表。"),
        task("dev", "写 action", "查 ROS2 action 定义，写一个 `Pick.action` 的 goal/result/feedback。"),
        task("observe", "删掉生成依赖", "在真实工作空间注释 `rosidl_default_generators`，看编译报什么错。"),
    ],
    quiz_items=[
        quiz("srv 的请求和响应用什么分隔？", ["---", "===", "###", ";;;"], 0,
             "`.srv` 用三个减号分隔。"),
        quiz("持续传感器数据更适合？", ["srv", "topic/msg", "action", "参数"], 1,
             "话题是持续流；srv 是一次请求响应。"),
        quiz("自定义接口包必须先做什么？", ["先跑视觉", "先编译接口包", "先标定", "先买相机"], 1,
             "依赖包需要先生成接口，其他包才能 include/import。"),
    ],
    industry="机器人项目里，接口设计比算法更容易被低估。统一的 Detection/Pose/Grasp 接口能让感知、规划、控制并行开发。",
    career="开发型岗位要设计稳定接口；调控岗位要会用 `ros2 interface show` 查字段、用 `ros2 topic echo` 看真实数据。",
    next_step="下一课处理命名空间和话题重映射，这是多机器人/多相机的基础。",
)

L3 = lesson(
    "ros2-remap-namespace",
    "命名空间与重映射：让同一套节点跑多台机器人",
    "相对名/绝对名、namespace、remap、launch 配置",
    chapter="ros2",
    difficulty=3,
    minutes=35,
    tags=["ROS2", "namespace", "remap"],
    objectives=[
        "区分相对话题名和绝对话题名",
        "用 namespace 隔离多台机器人",
        "用 remap 在不改代码的情况下换话题",
    ],
    concept=[
        P("同一份视觉节点，装在 robot1 和 robot2 上，如果都发布 `/image` 就会串数据。命名空间把相对名自动加前缀，重映射则把某个话题名换成另一个。"),
        FORMULA("相对名 image + namespace /robot1 → /robot1/image", "命名空间"),
        CODE(
            """# launch 里同时设置 namespace 和 remap
Node(
    package='vision_node',
    executable='detector',
    namespace='robot1',
    remappings=[('image', 'front_camera/image')],
)""",
            "python",
        ),
        NOTE("绝对名不接收命名空间", "`/image` 是绝对名，namespace 不会给它加前缀；`image` 才是相对名。写节点时优先用相对名，部署时再用 namespace 隔离。", "warn"),
    ],
    walkthrough=[
        seg(
            "实现话题名解析",
            r'''
def resolve(name, namespace="", remaps=None):
    remaps = remaps or {}
    if not name.startswith("/"):
        name = (namespace.rstrip("/") + "/" + name) if namespace else "/" + name
    return remaps.get(name, name)

print(resolve("image", "/robot1"))
print(resolve("/image", "/robot1"))
''',
            "先判断绝对/相对，再拼命名空间，最后查重映射表。真实 ROS2 的规则更细（节点名、私有名 `~`），但这条主线足够解释大多数现场问题。",
        ),
        seg(
            "重映射",
            r'''
remaps = {"/robot1/image": "/robot1/front_camera/image"}
print(resolve("image", "/robot1", remaps))
print(resolve("image", "/robot1"))
''',
            "重映射发生在解析之后：代码里仍写 `image`，部署时映射到 `front_camera/image`。这样同一份代码可以适配不同相机安装位置。",
        ),
        seg(
            "多机器人隔离",
            r'''
for robot in ("robot1", "robot2"):
    print(robot, "->", resolve("detections", "/" + robot))
''',
            "每个机器人一个 namespace，话题自然变成 `/robot1/detections`、`/robot2/detections`。跨机器人通信再显式用绝对名或桥接节点。",
        ),
        seg(
            "排查命令",
            r'''
print("ros2 node list")
print("ros2 topic list -t")
print("ros2 topic echo /robot1/detections")
print("ros2 topic info /robot1/image -v")
''',
            "现场先看节点在不在、话题名对不对、类型/QoS 是否匹配。命名空间错一位，`ros2 topic list` 里就会多出一个陌生话题。",
        ),
    ],
    tests=[
        test("相对名加命名空间", "resolve('image', '/robot1') == '/robot1/image'"),
        test("绝对名不变", "resolve('/image', '/robot1') == '/image'"),
        test("重映射生效", "resolve('image', '/robot1', remaps) == '/robot1/front_camera/image'"),
        test("多机器人隔离", "resolve('detections', '/robot2') == '/robot2/detections'"),
    ],
    tasks=[
        task("dev", "支持私有名", "让 `~image` 解析为 `/robot1/node_name/image`（先简化 node_name）。"),
        task("dev", "写 launch", "写一个 launch，把同一个节点启动两次，namespace 分别为 robot1/robot2。"),
        task("observe", "改绝对名", "把代码里的 `image` 改成 `/image`，观察 namespace 是否还生效。"),
    ],
    quiz_items=[
        quiz("`image` 是？", ["绝对名", "相对名", "私有名", "服务名"], 1,
             "不以 `/` 开头是相对名，会受 namespace 影响。"),
        quiz("remap 的作用？", ["改代码", "运行时换话题名", "改消息类型", "编译"], 1,
             "不改代码，把话题名映射到另一个。"),
        quiz("同一节点跑两台机器人，首选？", ["复制代码", "namespace", "改 IP", "重启 DDS"], 1,
             "namespace 隔离最干净。"),
    ],
    industry="多机器人、多相机、多工位系统几乎都会用 namespace/remap。不会这个，部署第二台设备时就会互相串话题。",
    career="开发型岗位要设计可配置的节点；调控岗位要会用 `ros2 topic list` 和 launch 参数快速定位命名空间问题。",
    next_step="下一课用 Python Launch 批量启动节点和定时器。",
)

CHAPTER = chapter(
    "ros2", "06", "ROS2 基础",
    "节点、话题、自定义消息/服务、命名空间与重映射；用纯 Python 模型理解 rclpy。",
    [L1, L2, L3],
    color="#38bdf8", icon="06",
)
