# -*- coding: utf-8 -*-
"""第九章：OpenCV + ROS2 视觉节点。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "ros2-vision-node",
    "OpenCV 视觉节点：把检测结果发到 ROS2 话题",
    "HSV 检测、Detection 消息、发布者、参数化阈值与可视化",
    chapter="ros2-vision",
    mode="vision",
    sample="parts.jpg",
    difficulty=4,
    minutes=50,
    tags=["ROS2", "OpenCV", "vision_node"],
    objectives=[
        "把 OpenCV 检测封装成一个“节点”函数",
        "把检测框转成 Detection 消息并发布",
        "用参数控制阈值/最小面积，输出可视化",
    ],
    concept=[
        P("视觉节点的最小闭环是：订阅图像 → OpenCV 处理 → 发布检测结果。图像可以用 `sensor_msgs/Image` 或 `cv_bridge` 转成 numpy；检测结果用自定义 `Detection` 消息。"),
        CODE(
            """# rclpy 视觉节点骨架
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from vision_interfaces.msg import Detection

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.declare_parameter('min_area', 700)
        self.pub = self.create_publisher(Detection, 'detections', 10)
        self.sub = self.create_subscription(Image, 'image', self.on_image, 10)
        self.bridge = CvBridge()

    def on_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        # ... OpenCV 检测 ...
        det = Detection()
        det.label = 'red'
        det.score = 0.9
        self.pub.publish(det)""",
            "python",
        ),
        NOTE("消息不要塞大图", "图像走 `sensor_msgs/Image`/压缩话题，检测结果只发框、类别、分数、位姿。把整张图塞进自定义消息会拖垮带宽和实时性。", "warn"),
    ],
    walkthrough=[
        seg(
            "HSV 检测红色目标",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([0, 80, 40]), np.array([180, 255, 255]))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
detections = []
for c in contours:
    area = float(cv2.contourArea(c))
    if area < float(p["min_area"]):
        continue
    M = cv2.moments(c)
    if M["m00"] == 0:
        continue
    detections.append({"label": "part",
                       "x": M["m10"] / M["m00"],
                       "y": M["m01"] / M["m00"],
                       "area": area,
                       "score": min(1.0, area / 5000.0)})
print("彩色目标:", len(detections))
metric("检测数", len(detections))
''',
            "HSV 的红色横跨 0° 和 180°，所以两段掩膜要合并。面积阈值用参数而不是写死，现场换镜头/换工位才能调。",
        ),
        seg(
            "模拟发布者",
            r'''
class MiniPublisher:
    def __init__(self, topic):
        self.topic = topic
        self.sent = []
    def publish(self, msg):
        self.sent.append(dict(msg))

pub = MiniPublisher("/robot1/detections")
for d in detections:
    pub.publish(d)
print("published:", len(pub.sent), "to", pub.topic)
metric("发布数", len(pub.sent))
''',
            "真实节点里 `pub.publish(det)` 会走 DDS；这里用列表模拟，方便验证字段和数量。消息字段要跟接口包完全一致，否则运行时会报类型错误。",
        ),
        seg(
            "画检测结果",
            r'''
result = image.copy()
for d in detections:
    x, y = int(d["x"]), int(d["y"])
    cv2.circle(result, (x, y), 16, (0, 255, 255), 2)
    cv2.putText(result, "%.2f" % d["score"], (x + 18, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
''',
            "可视化是视觉节点的“日志”。把框、分数、序号画出来，现场能快速判断是漏检、误检还是坐标变换错。",
        ),
        seg(
            "参数化",
            r'''
print("min_area =", p["min_area"])
print("真实节点用 declare_parameter / get_parameter 读取")
''',
            "参数从 launch/YAML 传入，节点不重新编译就能调。阈值、最小面积、相机 ID、置信度都适合做参数。",
        ),
        seg(
            "接进 launch",
            r'''
print("Node(package='vision_node', executable='vision_node',")
print("     parameters=[{'min_area': 700}],")
print("     remappings=[('image', '/camera/image_raw')])")
''',
            "launch 里配参数和重映射，节点代码保持通用。`/camera/image_raw` 是绝对名，换相机只需改 launch。",
        ),
    ],
    tests=[
        test("至少 5 个目标", "len(detections) >= 5"),
        test("检测字段完整", "all({'label', 'x', 'y', 'score'} <= set(d) for d in detections)"),
        test("发布数量一致", "len(pub.sent) == len(detections)"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    params=[
        param("min_area", "最小面积（px²）", 700, 100, 5000, 50),
    ],
    tasks=[
        task("dev", "加蓝色", "同时检测蓝色目标，给消息加 color 字段。"),
        task("dev", "加坐标变换", "把像素坐标映射到工作台毫米，再发布。"),
        task("tune", "改代码", "把 `min_area` 从参数改成写死 1000，跑一次；再改回参数，说明为什么现场要参数化。"),
        task("observe", "调 min_area", "把阈值调到 3000，观察检测数和误检。"),
    ],
    quiz_items=[
        quiz("检测结果应该发什么？", ["整张原图", "框/类别/分数/位姿", "视频文件", "相机内参"], 1,
             "图像走图像话题，检测结果走轻量消息。"),
        quiz("红色 HSV 为什么要两段？", ["红色最亮", "红色横跨 0/180", "红色饱和度低", "相机问题"], 1,
             "H 在 0 和 180 附近都可能是红色。"),
        quiz("参数化阈值的好处？", ["不用重编译", "提高分辨率", "自动标定", "减少内存"], 0,
             "现场可调，不用改代码重编。"),
    ],
    industry="ROS2 视觉节点是感知层的基本单元：相机驱动 → 检测/分割 → 位姿 → 规划/控制。工程上要关注带宽、延迟、时间戳和坐标系。",
    career="视觉应用开发要能把 OpenCV 算法包成 ROS2 节点；调控岗位要会看话题频率、延迟、检测框和参数。",
    next_step="ROS2 主线到这里闭环。最后用 GitHub 项目练一次真实复刻。",
)

CHAPTER = chapter(
    "ros2-vision", "09", "ROS2 视觉集成",
    "把 OpenCV 检测包成 ROS2 节点：消息、发布、参数、launch 与可视化。",
    [L1],
    color="#34d399", icon="09",
)
