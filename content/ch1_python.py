# -*- coding: utf-8 -*-
"""第一章：Python 零基础。"""

from common import (
    P, H, UL, NOTE, TABLE, seg, param, test, task, quiz, target, lesson, chapter,
)

L1 = lesson(
    "py-first-run",
    "第一次运行：让机器人开口",
    "print、变量、注释，以及怎么读懂第一条报错",
    chapter="python",
    difficulty=1,
    minutes=20,
    tags=["print", "变量", "报错"],
    objectives=[
        "独立运行第一段 Python 代码，看懂控制台输出",
        "用变量保存机器人名称、电量，并用比较运算做判断",
        "遇到 NameError 时知道先检查变量名和引号",
    ],
    concept=[
        P("这一页右侧的编辑器不是玩具：它就是一段真实的 Python 程序。点「运行」时，本机会启动一个 Python 进程执行它，再把文字和图片送回浏览器。你以后在 VS Code、PyCharm 里写代码，运行方式本质上一样。"),
        H("程序由三种最小的积木组成"),
        UL(
            "**输出**：`print(...)` 把括号里的内容显示出来，用来观察程序状态。",
            "**变量**：给一个值起名字，例如 `battery = 87.5`，后面就能反复使用。",
            "**注释**：以 `#` 开头，给人看的说明，Python 会跳过。",
        ),
        NOTE("学习建议", "先原样运行一次，再改一个值运行一次。编程是「改一点、跑一下、看结果」的循环，不是背语法。", "tip"),
        P("机器人工程里，变量名要能让别人一眼看懂。`battery` 比 `b` 好，`is_ready` 比 `flag` 好。现场调试时，同事读你的日志，第一眼看到的就是这些名字。"),
    ],
    walkthrough=[
        seg(
            "让程序说第一句话",
            r'''
# 以 # 开头的是注释，Python 不会执行它
print("你好，机器人工程师！")
''',
            "`print()` 是 Python 最常用的观察工具。括号里的字符串会被原样输出到控制台。中文、英文、标点都可以。",
            "字符串必须用引号包起来；中文引号“”不是 Python 语法。",
        ),
        seg(
            "用变量保存状态",
            r'''
robot_name = "R-01"       # 字符串 str
battery = 87.5            # 浮点数 float
is_ready = battery > 20   # 布尔值 bool：比较的结果
''',
            "`=` 不是数学里的等于，而是「把右边的值装进左边的名字」。`battery > 20` 会先算出一个 `True` 或 `False`，再存进 `is_ready`。",
            "变量名区分大小写，`Battery` 和 `battery` 是两个变量。",
        ),
        seg(
            "把状态打印出来",
            r'''
print("机器人:", robot_name)
print("电量:", battery, "%")
print("可以出发:", is_ready)
''',
            "`print()` 可以一次接收多个值，用逗号隔开，输出时自动加空格。这样拼接字符串比用 `+` 更省事，也不会因为类型不同而报错。",
        ),
        seg(
            "改变状态，再判断一次",
            r'''
battery = 15
is_ready = battery > 20
print("低电量时 is_ready =", is_ready)
''',
            "变量可以被重新赋值。注意：`is_ready` 不会自动跟着 `battery` 变化，必须重新计算一次。这是新手最常见的逻辑错误之一：改了输入，却忘了更新派生状态。",
            "在真实机器人里，电量、位姿、故障标志都应在每一步重新计算，而不是只算一次。",
        ),
        seg(
            "认识第一条报错",
            r'''
# 把下面这行前面的 # 去掉，再运行，看看会发生什么
# print("电压:", voltage)
print("程序结束")
''',
            "如果去掉注释，会得到 `NameError: name 'voltage' is not defined`。意思是：你使用了一个还没赋值的名字。看到报错不要慌，先看最后一行，再看它指出的行号。",
            "常见原因：变量名拼错、变量定义在另一个分支里、忘了先赋值。",
        ),
    ],
    tests=[
        test("机器人名字是字符串", 'robot_name == "R-01"'),
        test("电量是数字", "isinstance(battery, (int, float))"),
        test("is_ready 与电量一致", "is_ready == (battery > 20)"),
    ],
    tasks=[
        task("dev", "加一条任务状态", "新增变量 `mission = \"巡检 A 区\"`，用一行 print 输出「R-01 正在执行：巡检 A 区」。"),
        task("observe", "制造一次低电量", "把 battery 改成 15，重新运行，解释 is_ready 为什么变了。再把 15 改成 150，观察结果。"),
    ],
    quiz_items=[
        quiz("`print(\"A\", 1)` 的输出是什么？", ["A1", "A 1", "(\"A\", 1)", "报错"], 1,
             "print 用逗号分隔多个值时，默认用空格连接。"),
        quiz("`battery > 20` 的结果类型是？", ["int", "str", "bool", "float"], 2,
             "比较运算的结果永远是布尔值 True 或 False。"),
        quiz("出现 NameError，最不可能的原因是？", ["变量名拼写错误", "变量还没赋值", "字符串少了引号", "变量在另一个分支里定义"], 2,
             "少引号通常是 SyntaxError；NameError 关注「名字有没有被定义」。"),
    ],
    industry="任何机器人项目的第一天，几乎都是从一条 Python 脚本开始的：读传感器日志、画一条曲线、验证一个公式。大厂的算法工程师也要能写这种小脚本快速验证想法。",
    career="开发型岗位会把它写进自动化脚本；调控型岗位更多是用脚本批量分析现场日志。两种岗位都要求你能独立定位「为什么这个名字没定义」。",
    next_step="下一课把「值」分清楚：整数、浮点、字符串、布尔，以及 f-string 格式化。",
)

L2 = lesson(
    "py-types",
    "数据与类型：机器人世界的数字和文字",
    "int / float / str / bool、f-string 格式化与类型转换",
    chapter="python",
    difficulty=1,
    minutes=25,
    tags=["类型", "f-string", "转换"],
    objectives=[
        "分清 int、float、str、bool，并知道什么时候需要转换",
        "用 f-string 把传感器读数格式化成可读的日志",
        "避开 `bool(\"False\")`、`int(\"3.5\")` 这类经典坑",
    ],
    concept=[
        P("机器人程序处理的每一件事，最后都落到几种基本类型上：编码器计数是整数，电压是浮点数，串口收到的是字符串，急停按钮是布尔值。类型决定了你能对它做什么运算。"),
        TABLE(
            ["类型", "例子", "典型用途"],
            [
                ["int", "`12`、`-3`", "计数、编号、像素坐标"],
                ["float", "`1.25`、`87.5`", "距离、电压、速度"],
                ["str", "`\"AGV-07\"`", "设备号、日志、串口文本"],
                ["bool", "`True` / `False`", "是否到位、是否报警"],
            ],
        ),
        H("为什么要用 f-string"),
        P("把数字和文字拼在一起，最直观的写法是 `\"距离: \" + str(distance)`，但要手动转换类型，格式也不可控。f-string 把表达式直接嵌进字符串，还能指定小数位、补零、对齐，是现在 Python 日志与界面的标准写法。"),
        NOTE("现场经验", "日志里 `1.2500000000000002` 这种数字很常见。用 `:.2f` 固定两位小数，既好读，也方便和阈值比较。", "tip"),
    ],
    walkthrough=[
        seg(
            "四种基本类型",
            r'''
sensor_id = "ultrasonic-01"   # str
distance_m = 1.25             # float
sample_count = 12             # int
is_blocked = False            # bool

print(type(sensor_id), type(distance_m), type(sample_count), type(is_blocked))
''',
            "`type()` 返回一个值的类型。四个变量分别对应字符串、浮点数、整数、布尔值。不要靠「看起来像」猜类型，用 `type()` 或 `isinstance()` 确认。",
        ),
        seg(
            "单位换算与取整",
            r'''
distance_mm = distance_m * 1000
print("距离（毫米）:", distance_mm)
print("int 取整:", int(distance_mm))
print("round 四舍五入:", round(distance_mm))
''',
            "`1.25 * 1000` 得到的是浮点数 `1250.0`。`int()` 直接截断小数部分，`round()` 才做四舍五入。做阈值判断时通常保留浮点，不要急着取整。",
            "`int()` 不是四舍五入：`int(2.9)` 是 2。",
        ),
        seg(
            "算术运算",
            r'''
next_count = sample_count + 1
ratio = sample_count / 5
remainder = sample_count % 5
print("下一编号:", next_count)
print("比例:", ratio, "余数:", remainder)
''',
            "`/` 的结果一定是浮点数；`//` 是整除；`%` 取余数。机器人的轮询计数、分包序号、循环缓冲区下标，都经常用 `%`。",
        ),
        seg(
            "f-string：把读数变成日志",
            r'''
label = f"{sensor_id}: {distance_mm:.0f} mm"
print(label)
print(f"电量 {87.5:.1f}%")
print(f"编号 {7:03d}")
''',
            "大括号里可以放变量，也可以放格式说明。`:.0f` 表示不保留小数，`:.1f` 保留一位，`:03d` 表示至少三位、不足补零。日志的可读性和可检索性，往往就靠这些格式。",
            "f-string 前面必须有 `f`，否则大括号会被当成普通字符。",
        ),
        seg(
            "布尔值与类型转换",
            r'''
is_blocked = distance_mm < 300
print("是否挡住:", is_blocked)
print("字符串转整数:", int("42") + 1)
print("bool(0) =", bool(0), " bool('0') =", bool("0"))
''',
            "比较运算得到布尔值。`int(\"42\")` 可以把数字字符串转成整数，但 `int(\"3.5\")` 会报错。注意 `bool(\"0\")` 是 `True`，因为非空字符串都算真——这是串口解析里非常危险的坑。",
            "从串口读到的 `\"0\"` / `\"False\"` 必须先显式判断，不能直接 `bool()`。",
        ),
        seg(
            "字符串清洗与拆分",
            r'''
raw = "  AGV-07,OK  "
print(raw.strip().lower())
parts = raw.strip().split(",")
print(parts)
print("设备号:", parts[0], "状态:", parts[1])
''',
            "串口和文件里的文本经常带空格、换行。`strip()` 去掉首尾空白，`lower()` 统一小写，`split(\",\")` 按逗号切成列表。解析协议的第一步永远是清洗。",
        ),
    ],
    tests=[
        test("毫米换算正确", "distance_mm == 1250.0"),
        test("日志格式正确", 'label == "ultrasonic-01: 1250 mm"'),
        test("拆分结果正确", 'parts == ["AGV-07", "OK"]'),
        test("障碍判断正确", "is_blocked is False"),
    ],
    tasks=[
        task("dev", "改成危险距离", "把 distance_m 改成 0.28，重新运行，确认 is_blocked 变成 True。"),
        task("tune", "格式化三位编号", "用 f-string 把设备号 7 输出成 `007`，再输出一个保留两位小数的电压 `12.3456`。"),
    ],
    quiz_items=[
        quiz("`int(\"3.5\")` 的结果是？", ["3", "4", "3.5", "报错"], 3,
             "int() 只能解析整数字符串；要转小数应使用 float(\"3.5\")。"),
        quiz("`bool(\"False\")` 的值是？", ["False", "True", "0", "报错"], 1,
             "非空字符串都是 True。必须显式比较 `text == \"False\"` 或解析成布尔。"),
        quiz("哪个写法保留两位小数？", ["f\"{v:.2f}\"", "f\"{v:2f}\"", "f\"{v:.2}\"", "f\"{v:02d}\""], 0,
             "`.2f` 是两位小数的定点格式。"),
    ],
    industry="视觉系统输出的坐标、置信度、时间戳，最终都要格式化成日志或 JSON。坐标精度写错一位，机械臂就可能抓空；日志格式不统一，现场排障就会多花几小时。",
    career="调控型岗位每天看大量日志，格式敏感度是基本功；开发型岗位则要把这些字段设计成稳定的数据契约。",
    next_step="下一课把很多个读数放进列表和字典，用循环批量处理。",
)

L3 = lesson(
    "py-list-dict",
    "列表与字典：批量处理传感器数据",
    "索引、切片、append、for 循环、字典取值",
    chapter="python",
    difficulty=2,
    minutes=30,
    tags=["list", "dict", "循环"],
    objectives=[
        "用列表保存一组距离读数，完成索引、切片、追加",
        "用 for + if 过滤出安全距离，并统计数量",
        "用字典描述一台机器人的多个属性，遍历键值对",
    ],
    concept=[
        P("机器人不会一次只给你一个数。激光雷达一帧几百个点，视觉一帧几十个检测框，日志一次几千行。列表（list）负责「一串同类东西」，字典（dict）负责「一个物体的多个字段」。"),
        H("列表的两件事"),
        UL(
            "**按下标取**：`data[0]` 是第一个，`data[-1]` 是最后一个。下标从 0 开始。",
            "**切片**：`data[1:4]` 取下标 1、2、3，不含 4；`data[:3]` 取前三个。",
        ),
        H("字典的两件事"),
        UL(
            "**按键取**：`robot[\"battery\"]`；不确定键是否存在时用 `robot.get(\"speed\", 0)`。",
            "**遍历**：`for key, value in robot.items()` 同时拿到键和值。",
        ),
        NOTE("常见坑", "列表的切片和 `append` 会修改原列表；把列表赋给另一个变量不会复制，两个名字指向同一份数据。需要副本时用 `data.copy()` 或 `list(data)`。", "warn"),
    ],
    walkthrough=[
        seg(
            "创建列表并访问",
            r'''
distances = [820, 415, 96, 1200, 55]
print("数量:", len(distances))
print("第一个:", distances[0], "最后一个:", distances[-1])
print("前三个:", distances[:3])
''',
            "方括号里用逗号分隔元素。`len()` 返回元素个数；负下标从末尾数；切片 `[:3]` 取前三个。机器人里的关节角、路径点、检测框列表都用这种结构。",
        ),
        seg(
            "追加与修改",
            r'''
distances.append(640)
distances[2] = 90
print(distances)
''',
            "`append()` 在末尾追加一个元素；`distances[2] = 90` 直接改第三个元素。列表是可变的（mutable），这两行都会改变原列表。",
            "不要在遍历列表的同时删除元素，容易漏项；需要过滤时新建一个列表。",
        ),
        seg(
            "用循环过滤",
            r'''
safe = []
for d in distances:
    if d >= 300:
        safe.append(d)

print("安全距离:", safe)
print("安全数量:", len(safe))
''',
            "`for d in distances` 依次把每个元素赋给 `d`。只有满足 `d >= 300` 才追加到 `safe`。这就是视觉里「按面积过滤轮廓」的同一套逻辑。",
        ),
        seg(
            "带下标的循环",
            r'''
for i, d in enumerate(distances):
    status = "障碍" if d < 300 else "通行"
    print(f"#{i}: {d} mm -> {status}")
''',
            "`enumerate()` 同时给出下标和值，比手动维护计数器更不容易错。`A if 条件 else B` 是条件表达式，适合这种二选一的短判断。",
        ),
        seg(
            "字典：一台机器人的档案",
            r'''
robot = {"id": "AGV-07", "battery": 76, "pose": (1.2, 0.8, 0.0)}
print(robot["id"], robot["battery"])
print(robot.get("speed", "未设置"))

robot["speed"] = 0.4
for key, value in robot.items():
    print(key, "=", value)
''',
            "字典用键而不是下标。`get()` 在键不存在时返回默认值，避免 KeyError。`pose` 的值是一个元组 `(x, y, theta)`，元组不可修改，适合表示一个整体状态。",
            "JSON、配置文件、API 返回值，在 Python 里几乎都映射成字典。",
        ),
        seg(
            "列表套字典：一帧检测结果",
            r'''
detections = [
    {"color": "red", "x": 320, "y": 180},
    {"color": "blue", "x": 640, "y": 220},
]
for det in detections:
    print(det["color"], det["x"], det["y"])
''',
            "视觉检测的自然结构就是「列表套字典」：列表表示一帧里有多个目标，字典表示每个目标的颜色、坐标、置信度。后面的课程会反复用到这个结构。",
        ),
    ],
    tests=[
        test("列表长度正确", "len(distances) == 6"),
        test("安全距离过滤正确", "safe == [820, 415, 1200, 640]"),
        test("字典写入成功", 'robot["speed"] == 0.4'),
        test("检测框结构正确", 'detections[1]["color"] == "blue"'),
    ],
    tasks=[
        task("dev", "统计安全距离", "不用 len，写一个循环累加 safe 里的距离，输出总长度和平均值。"),
        task("dev", "增加一个检测", "往 detections 里追加一个绿色目标，坐标 (500, 300)，再遍历打印。"),
        task("observe", "观察浅拷贝", "把 `a = distances`、`b = distances.copy()` 分别改一个元素，看原列表是否变化。"),
    ],
    quiz_items=[
        quiz("`data[-1]` 表示？", ["第一个元素", "最后一个元素", "倒数第二个", "报错"], 1,
             "负下标从末尾开始，-1 是最后一个。"),
        quiz("`data[1:4]` 包含几个元素？", ["2", "3", "4", "5"], 1,
             "包含下标 1、2、3，共 3 个，不含 4。"),
        quiz("读取可能不存在的键，最稳妥的写法是？", ["robot[\"speed\"]", "robot.get(\"speed\", 0)", "robot.speed", "robot[\"speed\", 0]"], 1,
             "get() 提供默认值，不会抛 KeyError。"),
    ],
    industry="一帧视觉结果通常是 `list[dict]`，一个机器人状态是 `dict`。把这两层结构设计清楚，后面的跟踪、分拣、日志都好写。",
    career="开发型岗位要设计稳定的数据结构；调控型岗位要能从 JSON 日志里快速筛出异常帧。",
    next_step="下一课把重复逻辑封装成函数，让代码可以复用、可以测试。",
)

L4 = lesson(
    "py-functions",
    "函数：把动作封装成可复用的模块",
    "def、参数、返回值、默认参数、作用域",
    chapter="python",
    difficulty=2,
    minutes=35,
    tags=["函数", "参数", "作用域"],
    objectives=[
        "写出带参数和返回值的函数，并用 print 验证结果",
        "用默认参数和关键字参数让接口更好用",
        "理解局部变量与全局变量的边界，避免「函数改了外面」的意外",
    ],
    concept=[
        P("函数是机器人软件的最小复用单元。限幅、角度归一化、坐标变换、电机混控，这些动作在程序里会出现几十次；写成函数后，改一处、处处生效，也能单独测试。"),
        H("一个函数的三部分"),
        UL(
            "**定义**：`def 名字(参数):`，下面缩进的是函数体。",
            "**返回**：`return 值` 把结果交回调用者；没有 return 就返回 `None`。",
            "**调用**：`名字(实参)`，实参按位置或按名字传给形参。",
        ),
        P("函数应该「只做一件事，并把结果返回」，而不是在函数里偷偷修改全局变量。这样才容易测试、容易在别的项目里复用。"),
        NOTE("调试技巧", "函数结果不对时，先在函数内部 print 中间量，或在调用处 print 返回值。不要一上来就改公式。", "tip"),
    ],
    walkthrough=[
        seg(
            "限幅函数",
            r'''
def clamp(value, low, high):
    """把 value 限制在 [low, high] 之间。"""
    if value < low:
        return low
    if value > high:
        return high
    return value

print(clamp(150, 0, 100))
print(clamp(-5, 0, 100))
print(clamp(42, 0, 100))
''',
            "`clamp` 是机器人里最常用的函数之一：电机指令、PWM 占空比、转向角都必须限幅。三个分支分别处理「低于下限」「高于上限」「正常」。`\"\"\"...\"\"\"` 是文档字符串，写清楚函数做什么。",
            "参数顺序要固定；调用时 `clamp(150, 0, 100)` 比 `clamp(0, 100, 150)` 更不容易错。",
        ),
        seg(
            "距离函数",
            r'''
def distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return (dx * dx + dy * dy) ** 0.5

print(distance(0, 0, 3, 4))
print(distance(1.0, 2.0, 4.0, 6.0))
''',
            "两点距离公式。`** 0.5` 是开平方，比 `math.sqrt` 少一个 import。函数内部临时变量 `dx`、`dy` 只在函数里存在，外面看不到。",
        ),
        seg(
            "默认参数与关键字参数",
            r'''
def motor_command(speed, steer=0.0, enabled=True):
    if not enabled:
        return 0.0, 0.0
    left = speed - steer
    right = speed + steer
    return clamp(left, -1, 1), clamp(right, -1, 1)

print(motor_command(0.6, steer=0.2))
print(motor_command(0.6, enabled=False))
''',
            "`steer=0.0` 和 `enabled=True` 是默认值，调用时可以省略。`steer=0.2` 是关键字参数，读代码的人一眼知道 0.2 代表转向而不是速度。函数返回两个值，本质是一个元组。",
            "默认参数不要用可变对象（如 `[]`、`{}`），否则会在多次调用间共享。",
        ),
        seg(
            "角度归一化",
            r'''
def normalize_angle(deg):
    while deg > 180:
        deg -= 360
    while deg < -180:
        deg += 360
    return deg

for a in (0, 90, 370, -190, 540):
    print(a, "->", normalize_angle(a))
''',
            "机器人朝向常常累加到 370°、-190°，但控制器只接受 (-180, 180]。用 while 而不是 if，因为可能超出整整一圈。这个函数在后面的循迹和对接课里会再次出现。",
        ),
        seg(
            "作用域：函数能看到什么",
            r'''
limit = 100

def apply_limit(v):
    return clamp(v, -limit, limit)

print(apply_limit(250))
print("函数外 limit 仍然是", limit)
''',
            "函数内部可以读外面的 `limit`，但**不要**在函数里直接改它。需要修改时，把值作为参数传进去，或把新值 return 出来。这样数据流向清晰，调试时不会「不知道谁改了它」。",
            "如果函数里出现 `limit = ...`，Python 会把它当成新的局部变量，外面的值不变。",
        ),
    ],
    tests=[
        test("上限限幅", "clamp(150, 0, 100) == 100"),
        test("距离公式", "abs(distance(0, 0, 3, 4) - 5.0) < 1e-9"),
        test("电机混控", "abs(motor_command(0.6, 0.2)[0] - 0.4) < 1e-9 and abs(motor_command(0.6, 0.2)[1] - 0.8) < 1e-9"),
        test("角度归一化", "normalize_angle(370) == 10 and normalize_angle(-190) == 170"),
        test("外部变量未被修改", "limit == 100"),
    ],
    tasks=[
        task("dev", "写一个单位转换", "实现 `to_mm(meters)`，返回毫米；再实现 `to_mps(mm_per_s)`，把毫米每秒转成米每秒。"),
        task("dev", "写一个速度限制", "实现 `limit_speed(v, max_v)`，把速度限制在 ±max_v，要求复用 clamp。"),
        task("observe", "打印与返回", "把 `distance` 里的 return 改成 print，再运行一次，看 `print(distance(...))` 输出什么。"),
    ],
    quiz_items=[
        quiz("函数没有 return 时返回什么？", ["0", "None", "False", "报错"], 1,
             "Python 函数默认返回 None。"),
        quiz("`def f(a, b=2)`，调用 `f(1)` 时 b 是？", ["1", "2", "None", "报错"], 1,
             "b 使用默认值 2。"),
        quiz("函数里对全局变量赋值，外面会变吗？", ["会", "不会，除非用 global", "一定报错", "取决于类型"], 1,
             "函数内赋值会创建局部变量；修改全局变量需要 global，但不推荐。"),
    ],
    industry="视觉流水线里的 `undistort`、`pixel_to_world`、`clamp`、`normalize_angle` 都应该是纯函数：给定输入，返回输出，不依赖隐藏状态。这样才方便单元测试和跨项目复用。",
    career="开发型岗位考的就是「能不能把一段脚本拆成可测试的函数」；调控型岗位则要能快速改参数、验证函数边界。",
    next_step="下一课用类把「状态 + 行为」放在一起，并把日志写成 JSON 文件。",
)

L5 = lesson(
    "py-class-json",
    "类与文件：保存一台机器人的状态",
    "dataclass、方法、JSON 读写、异常处理",
    chapter="python",
    difficulty=3,
    minutes=40,
    tags=["class", "JSON", "异常"],
    objectives=[
        "用 dataclass 定义机器人状态，并添加判断方法",
        "把状态转成 JSON 写入文件，再读回来验证",
        "用 try/except 处理文件不存在、内容损坏等异常",
    ],
    concept=[
        P("字典适合「临时打包」数据，但当数据有固定字段、还要带行为时，类更合适。`RobotState` 把 `robot_id / x / y / battery` 绑在一起，还能提供 `is_low_battery()` 这样的方法。"),
        H("为什么用 dataclass"),
        P("普通类要手写 `__init__` 和 `__repr__`；`@dataclass` 自动生成，字段一目了然。`asdict()` 还能直接转成字典，方便写 JSON。"),
        H("JSON 是机器人系统的通用语言"),
        P("配置、日志、HTTP API、ROS 消息的调试输出，几乎都能用 JSON 表达。Python 的 `json.dump` / `json.load` 负责对象与文本之间的转换。注意 `dump` 是写文件，`dumps` 是转字符串。"),
        NOTE("异常不是敌人", "现场最常见的是文件不存在、权限不足、JSON 被截断。用 `try/except` 捕获后记录清楚，比程序直接崩掉好得多。但不要用 `except: pass` 把错误吞掉。", "warn"),
    ],
    walkthrough=[
        seg(
            "定义状态类",
            r'''
import json
import os
from dataclasses import dataclass, asdict

@dataclass
class RobotState:
    robot_id: str
    x: float
    y: float
    battery: float

    def is_low_battery(self):
        return self.battery < 20.0
''',
            "`@dataclass` 装饰器会根据字段自动生成初始化方法。`self` 代表当前对象，方法里通过 `self.battery` 访问字段。类型标注 `str`、`float` 是给人看的，Python 运行时不会强制检查。",
            "`@dataclass` 后面要跟 `class`，字段要写类型标注，否则不会成为字段。",
        ),
        seg(
            "创建对象并调用方法",
            r'''
state = RobotState("AGV-07", 1.2, 0.8, 18.5)
print(state)
print("低电量:", state.is_low_battery())

state.battery = 25.0
print("低电量:", state.is_low_battery())
''',
            "创建对象时按字段顺序传值。`print(state)` 会显示自动生成的可读形式。修改 `state.battery` 后，方法立刻反映新状态——这就是「状态和行为放在一起」的好处。",
        ),
        seg(
            "转成 JSON 文本",
            r'''
payload = asdict(state)
payload["event"] = "battery_check"
text = json.dumps(payload, ensure_ascii=False, indent=2)
print(text)
''',
            "`asdict()` 把 dataclass 转成普通字典，之后就能加字段、序列化。`ensure_ascii=False` 让中文正常显示；`indent=2` 让日志可读。",
            "`json.dumps` 返回字符串；`json.dump` 直接写文件，别混。",
        ),
        seg(
            "写入文件",
            r'''
log_path = os.path.join(work_dir, "robot_log.json")
with open(log_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print("写入:", log_path)
print("文件存在:", os.path.isfile(log_path))
''',
            "`with open(...) as f` 会在代码块结束时自动关闭文件，即使中间出错也不会泄漏句柄。`work_dir` 是本次运行的临时目录，写在这里不会污染项目。",
            "Windows 上写中文一定要指定 `encoding=\"utf-8\"`，否则可能乱码。",
        ),
        seg(
            "读回来并处理异常",
            r'''
try:
    with open(log_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    print("读回:", loaded["robot_id"], loaded["event"])
except (OSError, ValueError) as exc:
    print("读取失败:", exc)
    loaded = {}
''',
            "`OSError` 覆盖文件不存在、权限不足；`ValueError` 覆盖 JSON 格式错误。捕获后给出可读信息，并给 `loaded` 一个兜底值，后面的代码就不会因为变量未定义而二次崩溃。",
        ),
        seg(
            "追加多条事件日志",
            r'''
events = []
for i in range(3):
    events.append({
        "step": i,
        "x": round(state.x + i * 0.1, 2),
        "battery": state.battery,
    })

print(events)
''',
            "真实系统不会只记一条状态，而是按时间追加事件。列表套字典就是最简单的日志结构；再写文件时，可以一行一个 JSON（JSONL），方便流式追加和按行排查。",
        ),
    ],
    tests=[
        test("电量判断正确", "state.is_low_battery() is False"),
        test("JSON 读回成功", 'loaded["robot_id"] == "AGV-07" and loaded["event"] == "battery_check"'),
        test("文件已生成", "os.path.isfile(log_path)"),
        test("事件数量正确", "len(events) == 3"),
    ],
    tasks=[
        task("dev", "增加 to_json 方法", "给 RobotState 增加 `to_json()`，返回 `json.dumps(asdict(self), ensure_ascii=False)`。"),
        task("dev", "写 JSONL 日志", "把 events 逐行写入 `events.jsonl`，每行一个 `json.dumps`，再逐行读回并统计条数。"),
        task("observe", "制造一次坏 JSON", "手动把日志文件内容改成 `{bad`，重新运行，观察 except 分支的输出。"),
    ],
    quiz_items=[
        quiz("`json.dump(obj, f)` 与 `json.dumps(obj)` 的区别？", ["完全一样", "dump 写文件，dumps 返回字符串", "dumps 只能处理列表", "dump 会压缩"], 1,
             "带 s 的 dumps 返回 string；dump 直接写入文件对象。"),
        quiz("`with open(...)` 的主要好处？", ["读写更快", "自动关闭文件", "自动转 JSON", "自动创建目录"], 1,
             "上下文管理器保证退出代码块时关闭文件。"),
        quiz("捕获文件不存在，应该用哪个异常？", ["ValueError", "KeyError", "OSError", "NameError"], 2,
             "OSError 是文件/IO 相关异常的基类。"),
    ],
    industry="现场部署时，配置和日志几乎都是 JSON。视觉工位会把每帧的检测结果、耗时、参数版本写成 JSONL，出问题时按时间回放。会不会设计日志结构，直接决定排障速度。",
    career="开发型岗位负责定义状态模型和日志格式；调控型岗位负责从日志里还原现场、定位异常。",
    next_step="Python 基础到这里够用了。下一章进入图像：先理解「图片就是 NumPy 数组」。",
)

CHAPTER = chapter(
    "python", "01", "Python 零基础",
    "不假设你有编程经验：从 print 到类与 JSON，每条语句都拆开讲。",
    [L1, L2, L3, L4, L5],
    color="#7dd3fc", icon="01",
)
