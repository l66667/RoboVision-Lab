# -*- coding: utf-8 -*-
"""第八章：ROS2 工程层（package.xml、CMake、rosidl、colcon）。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "ros2-package-cmake",
    "package.xml + CMakeLists：一个 ROS2 C++ 包怎么搭",
    "ament_cmake 模板、依赖类型、可执行文件、OpenCV/Eigen 链接、install/export",
    chapter="ros2-build",
    difficulty=4,
    minutes=55,
    tags=["ROS2", "ament_cmake", "package.xml"],
    objectives=[
        "分清 buildtool_depend、build_depend、exec_depend",
        "写出一个能编译 OpenCV/Eigen 节点的 CMakeLists",
        "理解 install(TARGETS) 和 ament_export_dependencies 的作用",
    ],
    concept=[
        P("ROS2 的 C++ 包由 `package.xml`（元数据/依赖）和 `CMakeLists.txt`（构建规则）组成。`colcon` 读取 package.xml 决定依赖顺序，CMake/ament 负责真正编译。"),
        TABLE(
            ["依赖标签", "什么时候用", "例子"],
            [
                ["buildtool_depend", "构建工具", "ament_cmake"],
                ["build_depend", "编译期头文件/库", "rclcpp、OpenCV"],
                ["exec_depend", "运行期库/插件", "rclcpp、image_transport"],
                ["test_depend", "测试", "ament_lint_auto"],
            ],
        ),
        CODE(
            """<package format="3">
  <name>vision_node</name>
  <version>0.1.0</version>
  <description>OpenCV detector</description>
  <maintainer email="you@example.com">you</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <build_depend>rclcpp</build_depend>
  <build_depend>opencv2</build_depend>
  <exec_depend>rclcpp</exec_depend>
  <exec_depend>opencv2</exec_depend>

  <export><build_type>ament_cmake</build_type></export>
</package>""",
            "xml",
        ),
        CODE(
            """cmake_minimum_required(VERSION 3.8)
project(vision_node)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)

add_executable(detector src/detector.cpp)
target_link_libraries(detector ${OpenCV_LIBS} Eigen3::Eigen)
ament_target_dependencies(detector rclcpp)

install(TARGETS detector DESTINATION lib/${PROJECT_NAME})
ament_export_dependencies(rclcpp)
ament_package()""",
            "cmake",
        ),
        P("如果节点做成可组合组件，还要注册：`rclcpp_components_register_node(detector COMPONENT detector_node EXECUTABLE detector)`；普通 `add_executable` 方式则不需要。"),
    ],
    walkthrough=[
        seg(
            "生成 package.xml",
            r'''
import xml.etree.ElementTree as ET
from pathlib import Path

package_xml = """<?xml version="1.0"?>
<package format="3">
  <name>vision_node</name>
  <version>0.1.0</version>
  <description>OpenCV detector</description>
  <maintainer email="you@example.com">you</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <build_depend>rclcpp</build_depend>
  <build_depend>opencv2</build_depend>
  <exec_depend>rclcpp</exec_depend>
  <exec_depend>opencv2</exec_depend>
  <export><build_type>ament_cmake</build_type></export>
</package>"""

root = ET.fromstring(package_xml)
name = root.findtext("name")
deps = [e.text for e in root.findall("build_depend")]
print("package:", name, "build deps:", deps)
metric("包名", name)
''',
            "`package.xml` 是包的身份证：名字、版本、许可证、依赖。`colcon` 用这些依赖做拓扑排序；少写一个 `exec_depend`，本机编译能过，换机器运行就可能找不到库。",
        ),
        seg(
            "生成 CMakeLists",
            r'''
cmake = """cmake_minimum_required(VERSION 3.8)
project(vision_node)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
add_executable(detector src/detector.cpp)
target_link_libraries(detector ${OpenCV_LIBS} Eigen3::Eigen)
ament_target_dependencies(detector rclcpp)
install(TARGETS detector DESTINATION lib/${PROJECT_NAME})
ament_export_dependencies(rclcpp)
ament_package()
"""
print(cmake)
''',
            "`add_executable` 生成节点；`ament_target_dependencies` 把 rclcpp 的头文件/库/宏传给目标；`target_link_libraries` 链接 OpenCV；`install` 决定 `ros2 run` 能不能找到可执行文件。",
        ),
        seg(
            "写入工作空间并检查",
            r'''
work = Path("work")
work.mkdir(exist_ok=True)
(work / "package.xml").write_text(package_xml, encoding="utf-8")
(work / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
print("files:", sorted(p.name for p in work.iterdir()))
metric("文件数", len(list(work.iterdir())))
''',
            "真实包还要有 `src/detector.cpp`、`include/`、`launch/`。先保证两个构建文件正确，再往里填代码；顺序反了会被编译错误淹没。",
        ),
        seg(
            "检查依赖与安装规则",
            r'''
assert root.findtext("name") == "vision_node"
assert root.find("buildtool_depend").text == "ament_cmake"
assert "rclcpp" in deps and "opencv2" in deps
assert "find_package(OpenCV REQUIRED)" in cmake
assert "find_package(Eigen3 REQUIRED)" in cmake
assert "Eigen3::Eigen" in cmake
assert "install(TARGETS detector" in cmake
assert "ament_package()" in cmake
print("package/CMake checks passed")
''',
            "检查清单：包名、构建工具、依赖、`find_package`、`add_executable`、`install`、`ament_package()`。任何一项缺失都可能出现“编译过了但 `ros2 run` 找不到”。",
        ),
    ],
    tests=[
        test("包名正确", "root.findtext('name') == 'vision_node'"),
        test("构建工具正确", "root.find('buildtool_depend').text == 'ament_cmake'"),
        test("编译/运行依赖齐全", "'rclcpp' in deps and 'opencv2' in deps"),
        test("CMake 链接 OpenCV/Eigen", "'find_package(OpenCV REQUIRED)' in cmake and 'Eigen3::Eigen' in cmake"),
        test("安装规则存在", "'install(TARGETS detector' in cmake"),
        test("文件已写入", "(work / 'package.xml').exists() and (work / 'CMakeLists.txt').exists()"),
    ],
    tasks=[
        task("dev", "加 Eigen", "在 package.xml 和 CMakeLists 里加 Eigen3，链接到 detector。"),
        task("dev", "加第二个节点", "增加 `tracker` 可执行文件，并安装到 lib/${PROJECT_NAME}。"),
        task("observe", "删 exec_depend", "删掉 opencv2 的 exec_depend，重新 build/run，观察运行期错误。"),
    ],
    quiz_items=[
        quiz("构建工具依赖用？", ["build_depend", "buildtool_depend", "exec_depend", "test_depend"], 1,
             "ament_cmake 是构建工具，用 buildtool_depend。"),
        quiz("install(TARGETS) 的作用？", ["编译", "安装可执行文件到 install 目录", "链接 OpenCV", "生成消息"], 1,
             "让 ros2 run 能找到节点。"),
        quiz("运行期缺库，先查？", ["build_depend", "exec_depend", "test_depend", "license"], 1,
             "运行期依赖缺失常见于 exec_depend 漏写。"),
    ],
    industry="ROS2 C++ 包的构建问题占现场时间很大：依赖找不到、链接失败、install 漏了、接口顺序错。会读这两个文件，排错效率会高一个量级。",
    career="开发型岗位要能独立搭包；调控岗位要能看编译日志定位是依赖、链接还是安装问题。",
    next_step="下一课把 msg/srv/action 接口接进 CMake 和 package.xml。",
)

L2 = lesson(
    "ros2-rosidl",
    "自定义接口工程化：msg/srv/action 与 rosidl",
    "接口包结构、rosidl_generate_interfaces、生成依赖、头文件/模块引入",
    chapter="ros2-build",
    difficulty=4,
    minutes=45,
    tags=["ROS2", "rosidl", "msg", "srv"],
    objectives=[
        "设计一个接口包（msg/srv/action）",
        "写对 rosidl 的 CMake/package.xml 配置",
        "理解接口生成顺序与头文件引入问题",
    ],
    concept=[
        P("接口包只放 `.msg/.srv/.action`，不放业务代码。它先被 `rosidl` 生成 C++/Python 代码，其他包再依赖它。接口包编译失败，后面所有依赖包都会失败。"),
        CODE(
            """# CMakeLists.txt（接口包）
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Detection.msg"
  "srv/Detect.srv"
  "action/Pick.action"
)
ament_export_dependencies(rosidl_default_runtime)
ament_package()""",
            "cmake",
        ),
        CODE(
            """<!-- package.xml（接口包） -->
<buildtool_depend>ament_cmake</buildtool_depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>""",
            "xml",
        ),
        NOTE("接口包不要写业务", "接口包只定义数据结构；把节点、OpenCV、控制逻辑放到依赖它的包里。这样接口可以独立版本化，其他包也能复用。", "tip"),
    ],
    walkthrough=[
        seg(
            "定义 msg/srv/action",
            r'''
msg_def = """string label
float32 x
float32 y
float32 yaw
float32 score
"""
srv_def = """string color
---
bool success
Detection detection
"""
action_def = """string target_color
---
bool success
---
float32 progress
"""
print(msg_def)
''',
            "字段类型要用 ROS2 支持的 IDL 类型（string、float32、int32、bool、数组等）。坐标系、单位、score 含义写注释；接口一旦发布很难改。",
        ),
        seg(
            "解析字段",
            r'''
fields = []
for line in msg_def.strip().splitlines():
    typ, name = line.split()
    fields.append((typ, name))
print(fields)
metric("字段数", len(fields))
''',
            "真实 `rosidl` 会生成 `Detection.msg` 对应的 C++ 结构体和 Python 类。这里先解析字段，确认命名和类型没有拼错。",
        ),
        seg(
            "写接口包配置",
            r'''
cmake = """find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Detection.msg"
  "srv/Detect.srv"
  "action/Pick.action"
)
ament_export_dependencies(rosidl_default_runtime)
ament_package()
"""
print(cmake)
''',
            "`rosidl_generate_interfaces` 列出所有接口文件；漏一个，另一个包 include 时就会“找不到头文件”。`ament_export_dependencies` 让下游拿到运行期依赖。",
        ),
        seg(
            "生成顺序与引入",
            r'''
print("1. colcon build --packages-select vision_interfaces")
print("2. source install/setup.bash")
print("3. 下游包 find_package(vision_interfaces REQUIRED)")
print("4. C++: #include \"vision_interfaces/msg/detection.hpp\"")
print("5. Python: from vision_interfaces.msg import Detection")
''',
            "下游包必须在 package.xml 里 `depend` 接口包，CMake 里 `find_package` + `ament_target_dependencies`。只改代码不重新 source，Python 可能导入旧接口。",
        ),
        seg(
            "常见接口错误",
            r'''
errors = [
    "rosidl_generate_interfaces 漏文件",
    "package.xml 漏 rosidl_default_generators",
    "下游没 depend 接口包",
    "接口包没编完就编下游",
    "Python 没 source install/setup.bash",
]
for e in errors:
    print("-", e)
''',
            "接口问题优先看“第一个失败的是不是接口包”。如果接口包成功、下游失败，再查依赖声明和 include 路径。",
        ),
    ],
    tests=[
        test("Detection 字段完整", "fields == [('string', 'label'), ('float32', 'x'), ('float32', 'y'), ('float32', 'yaw'), ('float32', 'score')]"),
        test("srv 有分隔符", "'---' in srv_def"),
        test("action 有 goal/result/feedback", "action_def.count('---') == 2"),
        test("CMake 注册接口", "'rosidl_generate_interfaces' in cmake and 'Detection.msg' in cmake"),
    ],
    tasks=[
        task("dev", "加数组字段", "给 Detection 加 `float32[] polygon`，并说明长度如何约定。"),
        task("dev", "加常量", "在 msg 里加 `uint8 CLASS_RED=1`，观察生成后的常量访问方式。"),
        task("observe", "删生成依赖", "删掉 `rosidl_default_generators`，看 colcon 第一个报错是什么。"),
    ],
    quiz_items=[
        quiz("接口包应该放什么？", ["OpenCV 代码", "msg/srv/action 定义", "launch", "地图"], 1,
             "接口包只放接口定义。"),
        quiz("rosidl_generate_interfaces 的作用？", ["生成 C++/Python 接口代码", "启动节点", "链接 OpenCV", "压缩数据"], 0,
             "它驱动接口代码生成。"),
        quiz("下游 include 不到头文件，先查？", ["相机", "接口包是否编译/依赖是否声明", "显卡", "网络"], 1,
             "先确认接口包和 depend/find_package。"),
    ],
    industry="接口包是 ROS2 多包协作的契约。接口设计清晰，感知/规划/控制可以并行开发；接口混乱，后期改动会牵连所有包。",
    career="开发型岗位要能设计接口包和版本；调控岗位要会 `ros2 interface show`、确认消息类型和字段。",
    next_step="下一课用 colcon 组织多包工作空间，处理依赖顺序和叠加。",
)

L3 = lesson(
    "ros2-colcon-workspace",
    "colcon 工作空间：build、install、overlay 与依赖顺序",
    "src/build/install/log、colcon 常用命令、拓扑排序、环境脚本、常见工程问题",
    chapter="ros2-build",
    difficulty=4,
    minutes=50,
    tags=["ROS2", "colcon", "workspace"],
    objectives=[
        "说清 src/build/install/log 各自作用",
        "用依赖图推出 colcon 的编译顺序",
        "掌握 build/select/test/clean 与 overlay",
    ],
    concept=[
        P("ROS2 工作空间不是“一个文件夹”，而是 `src`（源码）+ `build`（中间产物）+ `install`（安装结果）+ `log`（日志）。`source install/setup.bash` 把当前工作空间叠加到环境里。"),
        TABLE(
            ["目录", "内容", "要不要提交"],
            [
                ["src/", "包源码", "要"],
                ["build/", "CMake 中间文件", "不要"],
                ["install/", "可执行/库/接口", "不要"],
                ["log/", "构建日志", "不要"],
            ],
        ),
        CODE(
            """colcon build
colcon build --packages-select vision_node
colcon build --symlink-install
colcon test
colcon test-result --verbose
colcon clean packages --yes""",
            "bash",
        ),
        NOTE("overlay 的顺序", "先 source 底层（/opt/ros/humble），再 source 你的 install。后 source 的会覆盖前面的同名包；顺序反了会用到系统旧版本。", "warn"),
    ],
    walkthrough=[
        seg(
            "建依赖图",
            r'''
packages = {
    "vision_interfaces": [],
    "vision_node": ["vision_interfaces", "rclcpp", "opencv2"],
    "vision_bringup": ["vision_node"],
    "robot_description": [],
    "robot_bringup": ["robot_description", "vision_bringup"],
}
print("包数:", len(packages))
metric("包数", len(packages))
''',
            "依赖图里既有工作空间内的包，也有系统包（rclcpp/opencv2）。colcon 只排工作空间内的包；系统包由 `find_package` 找。",
        ),
        seg(
            "拓扑排序",
            r'''
def build_order(packages):
    done, order = set(), []
    while len(done) < len(packages):
        ready = [p for p in packages
                 if p not in done and all(d in done or d not in packages for d in packages[p])]
        if not ready:
            raise ValueError("cycle: " + str(set(packages) - done))
        for p in sorted(ready):
            done.add(p)
            order.append(p)
    return order

order = build_order(packages)
print(" -> ".join(order))
''',
            "colcon 先编没有内部依赖的接口包，再编节点，最后编 bringup。出现环（A 依赖 B、B 依赖 A）会直接失败；先拆接口/回调，别用“再包一层”硬绕。",
        ),
        seg(
            "检查顺序",
            r'''
assert order.index("vision_interfaces") < order.index("vision_node")
assert order.index("vision_node") < order.index("vision_bringup")
assert order.index("robot_description") < order.index("robot_bringup")
print("dependency order OK")
''',
            "接口包必须最早；节点依赖接口；bringup 只放 launch/config，最后编。把 launch 放进节点包也能跑，但工程上建议分离。",
        ),
        seg(
            "叠加工作空间",
            r'''
def prefix(package, ws="/home/me/ros2_ws"):
    return ws + "/install/" + package

print(prefix("vision_node"))
print("source /opt/ros/humble/setup.bash")
print("source ~/ros2_ws/install/setup.bash")
''',
            "overlay 让新包覆盖底层同名包；调试时 `ros2 pkg prefix vision_node` 可确认到底加载了哪个 install。加载错版本，改代码怎么都不生效。",
        ),
        seg(
            "常见工程问题",
            r'''
issues = {
    "依赖找不到": "package.xml 漏 depend / 没 source",
    "链接失败": "CMake 漏 find_package 或 target_link_libraries",
    "接口生成顺序": "接口包没先编 / 下游没 depend",
    "头文件引入": "include 路径/命名空间/接口版本",
    "多包顺序": "依赖环 / 只 select 了一个包",
}
for k, v in issues.items():
    print("%-8s %s" % (k, v))
''',
            "排错顺序：先看第一个失败包，再看它的 package.xml/CMakeLists，最后看 install/setup。不要从最后一个报错往上猜。",
        ),
    ],
    tests=[
        test("包数正确", "len(packages) == 5"),
        test("接口在节点前", "order.index('vision_interfaces') < order.index('vision_node')"),
        test("节点在接口后", "order.index('vision_node') > order.index('vision_interfaces')"),
        test("bringup 最后", "order.index('vision_bringup') > order.index('vision_node')"),
        test("无环", "len(order) == len(packages)"),
    ],
    tasks=[
        task("dev", "加一个包", "给 vision_node 加 `vision_msgs` 依赖，重新排序。"),
        task("dev", "造一个环", "让 A 依赖 B、B 依赖 A，观察 build_order 抛错。"),
        task("observe", "只 select", "运行 `colcon build --packages-select vision_node`，如果接口没编会报什么？"),
    ],
    quiz_items=[
        quiz("colcon build 的 install 目录作用？", ["源码", "安装结果/环境", "日志", "缓存"], 1,
             "install 放可执行/库/接口，setup.bash 在这里。"),
        quiz("只编一个包用？", ["--packages-select", "--symlink-install", "test", "clean"], 0,
             "--packages-select 指定包名。"),
        quiz("接口包应该先编吗？", ["不用", "是", "最后", "只在 Python 编"], 1,
             "下游依赖接口生成的头文件/模块。"),
    ],
    industry="多包工作空间是 ROS2 工程的常态：接口包、驱动包、感知包、bringup 包分层。colcon 的顺序、overlay、install 问题是现场高频故障。",
    career="开发型岗位要能搭多包工程和 CMake；调控岗位要会看 colcon 日志、确认加载的是哪个 install。",
    next_step="下一课把 OpenCV 检测做成一个 ROS2 视觉节点。",
)

CHAPTER = chapter(
    "ros2-build", "08", "ROS2 工程层",
    "package.xml、ament_cmake、rosidl 接口、colcon 工作空间、依赖顺序与常见构建问题。",
    [L1, L2, L3],
    color="#fbbf24", icon="08",
)
