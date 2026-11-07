# -*- coding: utf-8 -*-
"""第二章：图像与 OpenCV 核心。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, seg, param, test, task, quiz, target, lesson, chapter,
)

NP = lesson(
    "np-array",
    "NumPy 速成：图像之前，先认识数组",
    "shape、dtype、索引切片、布尔掩膜、向量化",
    chapter="opencv",
    difficulty=2,
    minutes=30,
    tags=["NumPy", "数组", "向量化"],
    objectives=[
        "创建数组并读懂 shape、dtype、axis",
        "用切片和布尔掩膜批量取数，而不是写 for 循环",
        "理解「图像就是一个三维 uint8 数组」",
    ],
    concept=[
        P("OpenCV 的每一张图都是 NumPy 数组；深度学习框架的张量、点云坐标、机械臂位姿矩阵，底层也都是数组。先把数组用熟，后面看到 `image[y, x]` 才不会发怵。"),
        H("数组和列表的差别"),
        UL(
            "**形状固定**：`shape` 一眼看出几行几列；列表没有维度概念。",
            "**类型统一**：一个数组里所有元素同 dtype，内存连续，运算快。",
            "**向量化**：`a * 2 + 1` 对整个数组一次算完，不用写循环。",
        ),
        FORMULA("image.shape = (H, W, 3)   image[y, x, c]", "图像与数组的对应"),
        NOTE("axis 的方向", "`axis=0` 沿行方向（对每一列求值），`axis=1` 沿列方向（对每一行求值）。记不住就先建一个 2×3 的小数组试一下。", "warn"),
    ],
    walkthrough=[
        seg(
            "创建数组",
            r'''
import time
import cv2
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
print("shape:", a.shape, "dtype:", a.dtype)
print("全零:\n", np.zeros((2, 3), dtype=np.uint8))
print("全 7:\n", np.full((2, 2), 7))
print("序列:", np.arange(0, 10, 2))
''',
            "`np.array` 把嵌套列表变成二维数组；`shape=(2,3)` 表示 2 行 3 列。`zeros/full/arange` 是三个最常用的构造器。dtype 决定每个元素占几个字节、能表示什么范围。",
            "图像用 `uint8`（0–255）；坐标变换用 `float32`；计数用 `int`。类型用错会出现截断或溢出。",
        ),
        seg(
            "索引、切片、转置",
            r'''
print("a[0,1] =", a[0, 1])
print("第二列:", a[:, 1])
print("右下 2x2:\n", a[0:2, 1:3])
print("转置:\n", a.T)
''',
            "二维索引用 `[行, 列]`；`:` 表示整行/整列；切片不含右边界。`a.T` 行列互换。图像的 `image[y1:y2, x1:x2]` 就是同一套切片。",
        ),
        seg(
            "向量化运算与布尔掩膜",
            r'''
print("a*2+1:\n", a * 2 + 1)
print("每列均值:", a.mean(axis=0))
print("裁剪:", np.clip(a * 10, 0, 20))
selected = a[a > 3]
print("大于 3 的值:", selected)
''',
            "`a*2+1` 对每个元素同时生效，没有 Python 循环。`mean(axis=0)` 沿行方向压缩，得到每列均值。`a > 3` 生成同形状的布尔数组，`a[a>3]` 取出所有为 True 的元素——这就是颜色掩膜、阈值分割的底层机制。",
            "布尔索引返回一维数组，不是原形状；需要保持形状时用 `np.where`。",
        ),
        seg(
            "用数组生成一张图",
            r'''
yy, xx = np.mgrid[0:240, 0:320]
gradient = (xx / 320.0 * 255).astype(np.uint8)
mask = gradient > 128
print("gradient shape:", gradient.shape, "dtype:", gradient.dtype)
print("亮部比例:", round(float(mask.mean()), 3))

color = np.zeros((240, 320, 3), np.uint8)
color[mask] = (80, 220, 160)
color[~mask] = (30, 40, 50)
result = color
capture("生成的渐变图", gradient)
capture("布尔掩膜上色", color)
metric("亮部比例", round(float(mask.mean()), 3))
''',
            "`mgrid` 生成每个像素的 x/y 坐标，用 x 坐标做渐变。`astype(np.uint8)` 把浮点转成 0–255。`color[mask]` 把掩膜为 True 的像素染成绿色，`~mask` 是取反。整张图没有任何 for 循环。",
        ),
        seg(
            "循环 vs 向量化：为什么要学 NumPy",
            r'''
size = 1_000_000
data = np.random.default_rng(0).random(size)
start = time.perf_counter()
loop_sum = 0.0
for value in data:
    loop_sum += value
loop_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
vec_sum = float(data.sum())
vec_ms = (time.perf_counter() - start) * 1000
print("循环: %.1f ms" % loop_ms)
print("向量化: %.2f ms" % vec_ms)
print("结果差:", abs(vec_sum - loop_sum))
metric("循环耗时(ms)", round(loop_ms, 1))
metric("向量化耗时(ms)", round(vec_ms, 2))
''',
            "同样是一百万个数求和，Python 循环要逐个解释执行，NumPy 的 `sum()` 在 C 层一次跑完，通常快几十倍。视觉程序每帧要处理几十万个像素，这个差距直接决定能不能跑到 30 FPS。",
            "向量化不是「代码短」，而是「把循环交给底层」；能向量化就不要写逐像素 for。",
        ),
    ],
    tests=[
        test("数组形状正确", "a.shape == (2, 3)"),
        test("数组求和正确", "int(a.sum()) == 21"),
        test("布尔筛选正确", "len(selected) == 3"),
        test("渐变图尺寸正确", "gradient.shape == (240, 320) and gradient.dtype == np.uint8"),
        test("彩色结果正确", "result.shape == (240, 320, 3)"),
        test("两种求和一致", "abs(float(data.sum()) - loop_sum) < 1e-6"),
    ],
    tasks=[
        task("dev", "生成单位矩阵", "用 `np.eye(3)` 生成 3×3 单位矩阵，并打印。"),
        task("tune", "改阈值", "把 `gradient > 128` 改成 64 / 192，观察亮部比例和上色结果。"),
        task("observe", "比较 axis", "对 `a` 分别求 `mean(axis=0)` 和 `mean(axis=1)`，解释两个结果的形状和含义。"),
    ],
    quiz_items=[
        quiz("`np.zeros((2,3))` 的 shape 是？", ["(3,2)", "(2,3)", "(6,)", "(2,3,1)"], 1,
             "参数就是 shape，先 2 行再 3 列。"),
        quiz("`a[a > 3]` 返回什么？", ["同形状数组", "一维数组", "布尔值", "报错"], 1,
             "布尔索引把为 True 的元素抽出来，结果是一维的。"),
        quiz("`mean(axis=0)` 对 2×3 数组的结果形状是？", ["(2,)", "(3,)", "(2,3)", "标量"], 1,
             "axis=0 沿行压缩，留下 3 列，所以是 (3,)。"),
    ],
    industry="OpenCV、PyTorch、NumPy、PCL 的数据都以数组/张量形式流动。会向量化的人写出的预处理能快几倍，直接决定产线节拍；不会的人常在一个逐像素 for 循环上卡住整帧。",
    career="开发型岗位要把预处理写成向量化、可测试的函数；调控型岗位要能从 shape/dtype 报错快速判断是通道、类型还是维度问题。",
    next_step="下一课把数组真正当成图像：拆通道、裁 ROI、缩放、画框。",
)

L1 = lesson(
    "cv-image-array",
    "图像就是数组：第一次拆开一张图",
    "shape、dtype、BGR、像素索引、ROI、缩放与绘图",
    chapter="opencv",
    mode="vision",
    sample="studio.jpg",
    difficulty=2,
    minutes=30,
    tags=["ndarray", "BGR", "ROI"],
    objectives=[
        "说清一张 BGR 图的 shape、dtype 和内存含义",
        "用 `image[y, x]` 取像素，用切片取 ROI",
        "在图上画框、画点、写字，并保存中间结果",
    ],
    concept=[
        P("OpenCV 读进来的彩色图，本质是一个 `numpy.ndarray`，形状是 `(高, 宽, 3)`，类型是 `uint8`，每个通道取值 0–255。理解这一点，后面所有操作都只是数组运算。"),
        FORMULA("image.shape = (H, W, 3)   →   image[y, x, c]", "彩色图索引"),
        P("为什么是 BGR 而不是 RGB？这是 OpenCV 早期沿用摄像头采集顺序留下的历史包袱。显示、保存、`cv2.imwrite` 都按 BGR 工作；只有和 matplotlib、PIL、网页 Canvas 交互时才需要转成 RGB。"),
        H("ROI 是最实用的操作"),
        P("ROI（Region of Interest）就是数组切片：`image[y1:y2, x1:x2]`。注意先 y 后 x，且切片不含右边界。工业视觉里先裁 ROI 再处理，能把计算量降一个数量级，也能排除无关区域。"),
        NOTE("坐标顺序", "OpenCV 画图函数的点坐标是 `(x, y)`，而数组索引是 `[y, x]`。这两个顺序相反，是新手最常见的 bug 来源。", "warn"),
    ],
    walkthrough=[
        seg(
            "读取图像的元信息",
            r'''
import cv2
import numpy as np

print("shape:", image.shape)       # (高, 宽, 通道)
print("dtype:", image.dtype)       # uint8
print("height x width:", image.shape[0], "x", image.shape[1])
print("像素总数:", image.size)
''',
            "`shape` 的三个数分别是高、宽、通道数。`dtype=uint8` 表示每个通道用 8 位无符号整数存储，范围 0–255。`size` 是全部元素个数（高 × 宽 × 3）。",
            "不要用 `image.shape[1]` 当高度；OpenCV 的宽是 shape[1]。",
        ),
        seg(
            "BGR 通道与像素",
            r'''
b, g, r = cv2.split(image)
print("左上角像素 BGR:", image[0, 0])
print("中心像素 BGR:", image[image.shape[0] // 2, image.shape[1] // 2])
print("通道数:", image.shape[2])
''',
            "`cv2.split` 把三通道拆成三张单通道图，分别是蓝、绿、红。`image[y, x]` 返回一个长度为 3 的数组，顺序是 B、G、R。中心像素落在白色便签上，所以三个值都接近 255。",
            "`b, g, r = cv2.split(image)` 的顺序是 BGR；如果你按 RGB 理解，红色和蓝色会互换。",
        ),
        seg(
            "ROI 裁剪",
            r'''
h, w = image.shape[:2]
roi = image[120:650, 300:820]
print("ROI shape:", roi.shape)
print("ROI 左上角像素:", roi[0, 0])
''',
            "`image[120:650, 300:820]` 取 y 从 120 到 649、x 从 300 到 819 的区域。ROI 是原数组的视图（view），修改 ROI 会影响原图；需要独立副本时用 `.copy()`。",
        ),
        seg(
            "缩放与插值",
            r'''
small = cv2.resize(roi, (320, 240), interpolation=cv2.INTER_AREA)
print("缩小后:", small.shape)
capture("ROI 缩略图", small)
''',
            "`resize` 的目标尺寸是 `(宽, 高)`，不是 `(高, 宽)`。缩小用 `INTER_AREA`（区域平均，抗摩尔纹），放大用 `INTER_LINEAR` 或 `INTER_CUBIC`。视觉模型预处理里的缩放方式会影响精度。",
            "`cv2.resize(roi, (320, 240))` 得到的是宽 320、高 240，和 shape 的顺序相反。",
        ),
        seg(
            "在图上画框和点",
            r'''
result = image.copy()
cv2.rectangle(result, (300, 120), (820, 650), (80, 220, 120), 4)
cx, cy = w // 2, h // 2
cv2.circle(result, (cx, cy), 12, (0, 200, 255), -1)
cv2.putText(result, "ROI", (310, 110), cv2.FONT_HERSHEY_SIMPLEX,
            1.0, (80, 220, 120), 2, cv2.LINE_AA)
metric("ROI 宽高", "%dx%d" % (roi.shape[1], roi.shape[0]))
''',
            "`rectangle` 接收左上角和右下角 `(x, y)`；`circle` 的最后一个参数为 -1 表示实心；`putText` 的字号、颜色、线宽、抗锯齿都要显式给。先 `copy()` 再画，避免污染原图。",
        ),
        seg(
            "灰度图与通道统计",
            r'''
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print("gray shape:", gray.shape)
print("灰度最小/最大:", int(gray.min()), int(gray.max()))
print("平均亮度:", round(float(gray.mean()), 1))
capture("灰度图", gray)
''',
            "灰度图只有两个维度 `(H, W)`。`min/max/mean` 是最快的图像统计，用来判断曝光是否正常。很多算法（阈值、边缘、轮廓）都在灰度图上做，因为计算量只有彩色图的 1/3。",
            "`cv2.cvtColor` 的转换码是 `COLOR_BGR2GRAY`，不是 `RGB2GRAY`。",
        ),
    ],
    tests=[
        test("图像是三通道", "image.ndim == 3 and image.shape[2] == 3"),
        test("ROI 非空", "roi.shape[0] > 0 and roi.shape[1] > 0"),
        test("缩略图尺寸正确", "small.shape[:2] == (240, 320)"),
        test("结果图尺寸不变", "result.shape == image.shape"),
        test("灰度图是二维", "gray.ndim == 2"),
    ],
    tasks=[
        task("dev", "换一个 ROI", "把 ROI 改成右上角的黄色卡片区域，重新运行，观察裁剪结果。"),
        task("dev", "画一条对角线", "用 `cv2.line(result, (0,0), (w,h), (0,0,255), 3)` 画一条红色对角线。"),
        task("observe", "观察视图与副本", "把 `result = image.copy()` 改成 `result = image`，再运行，看看原图 `image` 是否被画上了框。"),
    ],
    quiz_items=[
        quiz("一张 800×600 的 BGR 图，shape 是？", ["(800, 600)", "(600, 800, 3)", "(800, 600, 3)", "(3, 600, 800)"], 1,
             "shape 的顺序是高、宽、通道。"),
        quiz("`image[100, 200]` 表示？", ["x=100, y=200", "y=100, x=200", "第 100 个通道", "第 100 行第 200 列的颜色"], 1,
             "数组索引是先 y 后 x。"),
        quiz("缩小图像时优先用哪种插值？", ["INTER_NEAREST", "INTER_LINEAR", "INTER_AREA", "INTER_CUBIC"], 2,
             "INTER_AREA 相当于区域平均，缩小最稳。"),
    ],
    industry="所有视觉流水线的第一步都是「拿到图、裁 ROI、看尺寸」。工业相机分辨率、ROI 位置、缩放比例会直接影响节拍和精度；把 ROI 设对，往往比换算法更能提速。",
    career="开发型岗位要处理不同分辨率、不同通道顺序的输入；调控型岗位要会用 ROI 排除干扰区域，快速定位画面问题。",
    next_step="下一课按颜色把目标从背景里分离出来：BGR 不够稳，改用 HSV。",
)

L2 = lesson(
    "cv-color-hsv",
    "颜色分割：在 HSV 里抓住红色物块",
    "BGR→HSV、双区间掩膜、形态学去噪、质心定位",
    chapter="opencv",
    mode="vision",
    sample="parts.jpg",
    difficulty=2,
    minutes=35,
    tags=["HSV", "inRange", "颜色分割"],
    objectives=[
        "解释 H/S/V 三个通道分别代表什么，以及 OpenCV 的 H 为什么是 0–180",
        "用两段 hue 区间处理红色在色环两端的环绕问题",
        "从掩膜求出最大色块的质心、面积，并叠加到原图",
    ],
    concept=[
        P("在 BGR 里做颜色阈值很痛苦：光照一变，三个通道一起变。HSV 把颜色拆成色相 H、饱和度 S、明度 V，光照主要影响 V，色相基本稳定，所以按颜色找目标通常用 HSV。"),
        TABLE(
            ["通道", "范围（OpenCV）", "含义", "调参直觉"],
            [
                ["H 色相", "0–180", "是什么颜色", "红色在 0 和 180 两端"],
                ["S 饱和度", "0–255", "颜色有多浓", "灰/白/黑 S 很低"],
                ["V 明度", "0–255", "有多亮", "阴影、反光主要改 V"],
            ],
        ),
        FORMULA("H_open = H_degree / 2", "OpenCV 把 0–360° 压到 0–180"),
        H("红色的环绕问题"),
        P("红色横跨 0° 和 360°，在 OpenCV 里就是 H∈[0,10] 和 H∈[170,180] 两段。只取一段会漏掉一半红色像素，所以要用两个 `inRange` 再做按位或。"),
        NOTE("形态学不是万能", "掩膜上的小噪点用开运算去掉，小洞用闭运算补上。但核太大也会把相邻目标粘在一起，先小核、再逐步加大。", "tip"),
    ],
    walkthrough=[
        seg(
            "转到 HSV 并看一个红色像素",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
print("红色块中心 BGR:", image[95, 785])
print("红色块中心 HSV:", hsv[95, 785])
''',
            "同一个像素在两套颜色空间里的坐标完全不同。BGR 的三个数都会随光照变化；HSV 里 H 接近 0，S 很高，V 也高。调阈值时先打印目标像素的 HSV，比盲猜快得多。",
        ),
        seg(
            "两段 hue 区间做红色掩膜",
            r'''
lower1 = np.array([0, p["sat_min"], p["val_min"]])
upper1 = np.array([p["hue_max"], 255, 255])
lower2 = np.array([170, p["sat_min"], p["val_min"]])
upper2 = np.array([180, 255, 255])

mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
raw_pixels = int(mask.sum() // 255)
print("红色像素:", raw_pixels)
metric("红色像素（去噪前）", raw_pixels)
''',
            "`inRange` 对每个像素判断是否落在闭区间内，返回 0/255 的单通道掩膜。两段结果用 `|` 按位或合并。`mask.sum()//255` 是统计白色像素个数的常用技巧。",
            "下界和上界的数组顺序必须是 H、S、V；少写一个分量会得到奇怪的形状错误。",
        ),
        seg(
            "形态学去噪",
            r'''
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
capture("红色掩膜", mask)
''',
            "开运算先腐蚀后膨胀，去掉孤立的白色噪点；闭运算先膨胀后腐蚀，补上目标内部的小黑洞（高光、反光）。顺序通常是先开后闭。",
        ),
        seg(
            "找最大连通区域并求质心",
            r'''
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
big = max(contours, key=cv2.contourArea)
M = cv2.moments(big)
cx = int(M["m10"] / M["m00"])
cy = int(M["m01"] / M["m00"])
area = int(cv2.contourArea(big))
print("最大红块面积:", area, "质心:", cx, cy)
metric("最大红块面积", area)
metric("质心", "%d, %d" % (cx, cy))
''',
            "`findContours` 拿到所有外轮廓；`max(..., key=cv2.contourArea)` 选面积最大的。`moments` 的 `m10/m00` 是 x 方向一阶矩除以面积，得到质心 x；y 同理。质心是抓取、跟踪最常用的目标中心。",
            "如果 `m00 == 0`（轮廓退化成线），除法会崩；工业代码要先判断面积。",
        ),
        seg(
            "叠加显示",
            r'''
result = image.copy()
red = np.array([0, 0, 255], dtype=np.float32)
result[mask > 0] = (0.35 * result[mask > 0] + 0.65 * red).astype(np.uint8)
cv2.drawContours(result, [big], -1, (0, 255, 255), 3)
cv2.circle(result, (cx, cy), 9, (255, 255, 255), -1)
cv2.putText(result, "red @ %d,%d" % (cx, cy), (max(10, cx - 110), max(30, cy - 18)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
''',
            "布尔索引 `result[mask > 0]` 只改掩膜内的像素。把原图和纯红按 35%/65% 混合，既有高亮又不完全遮住纹理。最后画轮廓、质心和文字。",
        ),
    ],
    tests=[
        test("掩膜尺寸与图像一致", "mask.shape == image.shape[:2]"),
        test("找到了红色区域", "raw_pixels > 1000"),
        test("质心在画面内", "0 <= cx < image.shape[1] and 0 <= cy < image.shape[0]"),
        test("结果图尺寸不变", "result.shape == image.shape"),
    ],
    params=[
        param("sat_min", "饱和度下限 S", 120, 40, 255, 5, hint="太低会把灰白背景也算进来"),
        param("val_min", "明度下限 V", 80, 20, 255, 5, hint="阴影里的目标 V 会变低"),
        param("hue_max", "红色 H 上限", 10, 2, 30, 1, hint="红色在 0 附近，上限越大越宽松"),
    ],
    tasks=[
        task("dev", "识别绿色", "复制这段逻辑，把 HSV 区间改成绿色（H≈35–85），统计绿块数量。"),
        task("tune", "只数不叠色", "把叠加显示去掉，改成输出每种颜色的数量表格。"),
        task("tune", "让掩膜更干净", "把形态学核从 5 改成 3 或 7，观察噪点和边缘的变化。"),
    ],
    quiz_items=[
        quiz("OpenCV 的 H 通道范围是？", ["0–255", "0–360", "0–180", "-180–180"], 2,
             "OpenCV 把 0–360° 压到 0–180。"),
        quiz("为什么红色要用两段区间？", ["红色饱和度低", "红色在色环两端", "红色亮度高", "OpenCV 的 bug"], 1,
             "0° 和 360° 是同一个红色，压到 0–180 后落在 0 和 180 两端。"),
        quiz("开运算的主要作用是？", ["补洞", "去掉小噪点", "放大目标", "改变颜色"], 1,
             "先腐蚀后膨胀，去掉孤立小亮块。"),
    ],
    industry="颜色分拣是最常见的入门产线任务：零件按颜色进不同料框。真实的难点不是 `inRange`，而是光照、反光、色差和相机白平衡；现场要拿标准色卡反复标定 HSV 区间。",
    career="调控型岗位最常改的就是 HSV 上下界和形态学核；开发型岗位则要把这些参数做成配置，并记录每次改动的效果。",
    next_step="颜色之外，下一课用灰度阈值和边缘把结构提取出来。",
)

L3 = lesson(
    "cv-threshold-edge",
    "阈值与边缘：把图像变成结构",
    "Otsu、自适应阈值、Sobel、Canny 的适用边界",
    chapter="opencv",
    mode="vision",
    sample="document.jpg",
    difficulty=3,
    minutes=40,
    tags=["Otsu", "自适应", "Canny"],
    objectives=[
        "说清全局阈值、Otsu、自适应阈值各自适合什么光照条件",
        "用 GaussianBlur 预处理，理解 Canny 的双阈值",
        "把原图、阈值、边缘拼成对照面板，做参数对比",
    ],
    concept=[
        P("阈值把灰度图变成黑白：大于阈值变白，小于变黑。难点从来不是 `cv2.threshold` 这一行，而是「阈值取多少」以及「光照不均匀时一个阈值够不够」。"),
        TABLE(
            ["方法", "原理", "适合", "失效场景"],
            [
                ["固定阈值", "人工给一个数", "光照稳定的工位", "换灯、换背景就崩"],
                ["Otsu", "最大化类间方差，自动找双峰切点", "前景/背景双峰明显", "单峰、渐变阴影"],
                ["自适应", "每个像素用邻域均值/高斯加权", "文档、表面不均", "大面积纯色、噪声高"],
            ],
        ),
        H("Canny 的四步"),
        UL(
            "高斯平滑：压掉高频噪声。",
            "Sobel 求梯度：得到每个像素的边缘强度和方向。",
            "非极大值抑制：只保留梯度方向上的脊。",
            "双阈值连接：强边缘保留，弱边缘只有在连着强边缘时才保留。",
        ),
        FORMULA("低阈值 : 高阈值 ≈ 1 : 2 ~ 1 : 3", "常用起点，再按漏检/误检调"),
        NOTE("参数不是越敏感越好", "Canny 低阈值降得太低，背景纹理全变成边缘；后续轮廓、直线检测会被淹没。先保证「主要结构连续」，再谈细节。", "warn"),
    ],
    walkthrough=[
        seg(
            "灰度与高斯平滑",
            r'''
import cv2
import numpy as np

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
print("灰度范围:", int(gray.min()), int(gray.max()))
''',
            "高斯核 `(5, 5)` 表示 5×5 邻域，`sigma=0` 让 OpenCV 按核大小自动算标准差。平滑会降低噪声，也会让边缘稍微变钝；核越大越明显。",
        ),
        seg(
            "Otsu 自动阈值",
            r'''
otsu_value, otsu = cv2.threshold(
    blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print("Otsu 自动阈值:", otsu_value)
metric("Otsu 阈值", round(float(otsu_value), 1))
''',
            "传 `0` 作为阈值只是占位，`THRESH_OTSU` 会自己算。它遍历 0–255，找让前景/背景类间方差最大的切点。双峰越明显，结果越稳。",
            "Otsu 返回两个值：实际阈值和结果图。别只接一个变量。",
        ),
        seg(
            "自适应阈值",
            r'''
block = int(p["block_size"])
if block % 2 == 0:
    block += 1
adaptive = cv2.adaptiveThreshold(
    blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, block, 10)
''',
            "自适应阈值对每个像素只看 `block × block` 的邻域，用高斯加权均值减去常数 10 作为局部阈值。阴影里的文字也能被切出来。`blockSize` 必须是大于 1 的奇数。",
            "blockSize 要大于笔画宽度、小于光照变化的尺度；太小会把笔画内部切成黑白相间。",
        ),
        seg(
            "Sobel 梯度",
            r'''
gx = cv2.Sobel(blur, cv2.CV_32F, 1, 0, ksize=3)
gy = cv2.Sobel(blur, cv2.CV_32F, 0, 1, ksize=3)
magnitude = cv2.magnitude(gx, gy)
magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
magnitude = magnitude.astype(np.uint8)
''',
            "`Sobel(dx=1, dy=0)` 求水平方向导数，对竖直边缘敏感；`dy=1` 对水平边缘敏感。`magnitude` 合成梯度强度。归一化到 0–255 才能显示。",
            "Sobel 输出有正负，必须用 `CV_32F` 或 `CV_64F`；用 uint8 会截断负值。",
        ),
        seg(
            "Canny 双阈值",
            r'''
low = int(p["canny_low"])
high = max(low + 1, int(p["canny_high"]))
edges = cv2.Canny(blur, low, high)
ratio = float(edges.mean() / 255.0)
print("边缘像素占比: %.3f%%" % (ratio * 100))
metric("边缘像素占比", round(ratio, 4))
''',
            "Canny 的 low/high 是滞后阈值：高于 high 的一定是边缘，低于 low 的一定不是，介于两者之间的只有连着强边缘才保留。占比是很好的量化指标：太低可能漏检，太高可能噪声过多。",
        ),
        seg(
            "拼成对照面板",
            r'''
def tile(img, text):
    if img.ndim == 2:
        out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        out = img.copy()
    out = cv2.resize(out, (480, 300))
    cv2.rectangle(out, (0, 0), (480, 34), (20, 20, 20), -1)
    cv2.putText(out, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2, cv2.LINE_AA)
    return out

top = np.hstack([tile(blur, "blur"), tile(otsu, "Otsu"), tile(adaptive, "adaptive")])
bottom = np.hstack([tile(edges, "Canny"), tile(magnitude, "Sobel"), tile(gray, "gray")])
result = np.vstack([top, bottom])
''',
            "把六张图缩放到同一尺寸再拼接，是实验对比的标准做法。`hstack` 要求高度一致，`vstack` 要求宽度一致；先 resize 再拼就不会报错。",
        ),
    ],
    tests=[
        test("Otsu 是二值图", "int(otsu.max()) == 255 and int(otsu.min()) == 0"),
        test("边缘图尺寸正确", "edges.shape == gray.shape"),
        test("面板是彩色图", "result.ndim == 3 and result.shape[2] == 3"),
        test("Otsu 阈值合理", "0 < otsu_value < 255"),
    ],
    params=[
        param("block_size", "自适应邻域 blockSize", 31, 11, 61, 2, hint="必须是奇数，越大越看全局"),
        param("canny_low", "Canny 低阈值", 60, 10, 150, 5),
        param("canny_high", "Canny 高阈值", 160, 40, 320, 5),
    ],
    tasks=[
        task("dev", "只保留文字", "调整 blockSize 和常数，让便签上的手写线保留、背景网格消失。"),
        task("tune", "让边缘更连续", "把 Canny 低阈值降到 25，高阈值降到 80，观察边缘是变连续还是变脏。"),
        task("observe", "去掉高斯", "把 `blur` 改成 `gray` 再跑 Canny，比较噪点数量。"),
    ],
    quiz_items=[
        quiz("Otsu 最适合什么图？", ["单峰直方图", "双峰明显的图", "纯色图", "彩色图"], 1,
             "Otsu 假设前景和背景各成一个峰。"),
        quiz("Canny 的高阈值作用？", ["决定弱边缘", "强边缘门槛", "高斯核大小", "图像尺寸"], 1,
             "高于高阈值的一定保留；低阈值决定弱边缘是否能接上。"),
        quiz("自适应阈值的 blockSize 必须？", ["偶数", "奇数且 >1", "等于图像宽度", "是 2 的幂"], 1,
             "OpenCV 要求大于 1 的奇数。"),
    ],
    industry="文档扫描、表面缺陷、车道线、PCB 焊盘定位都会先做阈值/边缘。现场最常见的问题是光照不均，这时全局 Otsu 会整片失效，需要自适应阈值或分区处理。",
    career="调控型岗位要能在「漏检」和「误检」之间找平衡；开发型岗位则要把阈值做成可配置、可回归的模块。",
    next_step="边缘只是像素；下一课把连通区域变成可计数的轮廓，并量出面积、位置和形状。",
)

L4 = lesson(
    "cv-contour-shape",
    "轮廓与形状：数清、量准、定位",
    "形态学、findContours、面积/外接矩形/质心/圆度",
    chapter="opencv",
    mode="vision",
    sample="coins.jpg",
    difficulty=3,
    minutes=45,
    tags=["contours", "形态学", "测量"],
    objectives=[
        "用 Otsu + 形态学得到干净的连通区域",
        "按面积过滤轮廓，计算外接矩形、质心和圆度",
        "理解「19 枚硬币只数出 18 个」的粘连问题",
    ],
    concept=[
        P("阈值得到的是像素，轮廓得到的是「目标」。`findContours` 把相邻的白色像素串成边界点集，之后就能算面积、周长、外接矩形、质心、凸包、圆度——这些才是分拣、计数、测量能用的量。"),
        FORMULA("circularity = 4πA / P²", "圆度：越接近 1 越像圆"),
        H("为什么先做形态学"),
        UL(
            "**开运算**去掉毛刺和孤立噪点，避免一个目标被数成多个。",
            "**闭运算**补掉目标内部的高光/反光小洞，避免一个目标被拆成多个。",
            "核越大，粘连风险越高；先小核，再按需要加。",
        ),
        NOTE("粘连是经典难题", "两枚硬币挨在一起，外轮廓会合成一个。只靠腐蚀分开会改变面积；工业上常用距离变换 + 分水岭，或直接用实例分割模型。这一课先学会识别「数少了」并解释原因。", "warn"),
    ],
    walkthrough=[
        seg(
            "灰度、平滑、Otsu 反相",
            r'''
import cv2
import numpy as np

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
_, mask = cv2.threshold(
    blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
print("Otsu 反相后白色像素:", int(mask.sum() // 255))
''',
            "硬币比背景暗，所以用 `THRESH_BINARY_INV` 把暗目标变成白色、背景变成黑色。`findContours` 默认找白色目标，方向反了会数到背景。",
            "如果目标比背景亮，就用 `THRESH_BINARY`；先确认极性再谈参数。",
        ),
        seg(
            "形态学清理",
            r'''
size = int(p["morph_size"])
if size % 2 == 0:
    size += 1
kernel = np.ones((size, size), np.uint8)
clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel)
capture("清理后的掩膜", clean)
''',
            "开运算去掉小噪点，闭运算补内部空洞。结构元尺寸必须是正奇数。可以分别 capture 开运算和闭运算的结果，对比各自去掉了什么。",
        ),
        seg(
            "找轮廓并按面积过滤",
            r'''
contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
min_area = float(p["min_area"])
objects = []
for c in contours:
    area = float(cv2.contourArea(c))
    if area < min_area:
        continue
    x, y, bw, bh = cv2.boundingRect(c)
    M = cv2.moments(c)
    if M["m00"] == 0:
        continue
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    perimeter = float(cv2.arcLength(c, True))
    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter else 0
    objects.append({
        "area": area, "bbox": (x, y, bw, bh), "center": (cx, cy),
        "circularity": float(circularity),
    })
print("连通区域数:", len(objects))
metric("连通区域数", len(objects))
''',
            "`RETR_EXTERNAL` 只取最外层轮廓，适合计数；`CHAIN_APPROX_SIMPLE` 压缩直线段，省内存。面积过滤掉噪声；`m00` 为 0 的退化轮廓直接跳过，避免除零。圆度用面积和周长的组合，越接近 1 越圆。",
            "`contourArea` 返回浮点；用 `int` 截断会让小目标变成 0。",
        ),
        seg(
            "按面积排序并画出来",
            r'''
objects.sort(key=lambda o: o["area"], reverse=True)
result = image.copy()
for index, obj in enumerate(objects):
    x, y, bw, bh = obj["bbox"]
    cx, cy = obj["center"]
    cv2.rectangle(result, (x, y), (x + bw, y + bh), (80, 220, 120), 2)
    cv2.circle(result, (int(cx), int(cy)), 5, (0, 220, 255), -1)
    cv2.putText(result, str(index + 1), (x, max(18, y - 6)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
''',
            "按面积从大到小排序，编号更稳定。外接矩形给出 x/y/宽/高，质心给出抓取点。工业上还会加最小外接矩形，得到旋转角度，供夹爪对齐。",
        ),
        seg(
            "统计与解释",
            r'''
areas = [o["area"] for o in objects]
print("最大面积:", round(max(areas), 1))
print("最小面积:", round(min(areas), 1))
print("平均面积:", round(sum(areas) / len(areas), 1))
round_objects = [o for o in objects if o["circularity"] > 0.8]
print("圆度 > 0.8 的目标:", len(round_objects))
metric("平均面积", round(sum(areas) / len(areas), 1))
''',
            "面积分布能看出目标是否同一规格；圆度能区分圆孔、方块和长条形。注意：粘连会让面积翻倍、圆度下降，这两个指标同时异常时，先怀疑粘连而不是镜头。",
        ),
    ],
    tests=[
        test("至少找到 12 个目标", "len(objects) >= 12"),
        test("面积都超过下限", "all(o['area'] >= float(p['min_area']) for o in objects)"),
        test("结果图尺寸不变", "result.shape == image.shape"),
        test("圆度在合理范围", "all(0 <= o['circularity'] <= 1.2 for o in objects)"),
    ],
    params=[
        param("min_area", "最小面积（像素）", 2000, 200, 6000, 100),
        param("morph_size", "形态学核尺寸", 5, 3, 15, 2, hint="奇数；越大越容易粘连"),
    ],
    tasks=[
        task("dev", "只保留圆形", "用圆度 > 0.85 过滤，只给圆形目标画框，输出剩余数量。"),
        task("dev", "加最小外接矩形", "对每个目标用 `cv2.minAreaRect`，把旋转角度也打印出来。"),
        task("observe", "制造粘连", "把形态学核改成 15×15，观察连通区域数是否减少，并解释原因。"),
    ],
    quiz_items=[
        quiz("`RETR_EXTERNAL` 的含义？", ["所有轮廓", "只取最外层", "只取内孔", "按面积排序"], 1,
             "只返回最外层轮廓，适合计数。"),
        quiz("圆度公式 4πA/P² 中，P 是？", ["像素总数", "轮廓周长", "外接矩形周长", "面积"], 1,
             "P 是轮廓周长，圆度越接近 1 越像圆。"),
        quiz("两枚硬币粘连时，最直接的表现是？", ["面积变小", "数量偏少、面积偏大", "颜色改变", "轮廓变成圆"], 1,
             "外轮廓合并，数量减少，合并后的面积接近两枚之和。"),
    ],
    industry="药片计数、螺丝分选、零件尺寸测量、PCB 焊盘定位都靠轮廓统计。真实产线还会用最小外接矩形算角度、用凸包算缺陷、用匹配算形状相似度。",
    career="开发型岗位要把轮廓特征封装成稳定的检测函数；调控型岗位要能从「数量不对」快速判断是阈值、形态学还是粘连问题。",
    next_step="下一课做几何变换：把倾斜拍摄的纸面拉正，这是文档扫描和工位标定的基础。",
)

L5 = lesson(
    "cv-perspective",
    "透视校正：把斜着拍的纸拉正",
    "找纸、四点排序、getPerspectiveTransform、warpPerspective",
    chapter="opencv",
    mode="vision",
    sample="document.jpg",
    difficulty=3,
    minutes=45,
    tags=["透视", "单应性", "文档扫描"],
    objectives=[
        "用低饱和+高亮度掩膜找到纸面，而不是依赖 Canny",
        "把四个角点排成左上/右上/右下/左下，构造单应变换",
        "用 warpPerspective 得到正视扫描件，并做自适应二值化",
    ],
    concept=[
        P("相机斜着看一个平面，近大远小。透视变换（单应性）用一个 3×3 矩阵把四个点映射到四个点，把梯形拉成矩形。它保证直线仍是直线，但不保证平行线仍平行——这正是「透视」和「仿射」的区别。"),
        FORMULA("[x', y', w']ᵀ = H · [x, y, 1]ᵀ，最终 (x'/w', y'/w')", "单应变换"),
        H("四步流水线"),
        UL(
            "**找纸**：低饱和度 + 高亮度，比 Canny 在「白纸 + 绿桌」上更稳。",
            "**补角**：纸边被物体压住时轮廓会缺角，先 convexHull 再 approxPolyDP。",
            "**排序**：按 x+y 和 x−y 找左上、右下、右上、左下，顺序错了会得到镜像/旋转结果。",
            "**拉正**：目标矩形的宽高按实际长宽比（A4 是 210:297），再二值化。",
        ),
        NOTE("顺序比公式更容易错", "四个点如果顺序错，warpPerspective 会把纸扭成蝴蝶结。先在原图上把四个点按 TL、TR、BR、BL 画出来确认，再做变换。", "warn"),
    ],
    walkthrough=[
        seg(
            "用 HSV 找纸面",
            r'''
import cv2
import numpy as np

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(
    hsv,
    np.array([0, 0, int(p["val_min"])]),
    np.array([180, int(p["sat_max"]), 255]),
)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
capture("纸面掩膜", mask)
''',
            "纸是低饱和、高亮度的；桌面是绿色，饱和度高，会被 `sat_max` 排除。先闭运算把纸上的黑圈/文字造成的小洞补上，再开运算去掉噪点。",
            "`sat_max` 太大，绿色桌面会混进来；太小，纸上的阴影会被切掉。",
        ),
        seg(
            "最大轮廓 + 凸包 + 多边形近似",
            r'''
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
big = max(contours, key=cv2.contourArea)
hull = cv2.convexHull(big)
peri = cv2.arcLength(hull, True)
approx = cv2.approxPolyDP(hull, float(p["eps_ratio"]) * peri, True)
print("近似后的角点数:", len(approx))
metric("角点数", len(approx))
''',
            "纸边上压了黑色圆环，原始轮廓会缺角；`convexHull` 先把凹进去的地方包起来，再用 `approxPolyDP` 把密集点简化成 4 个角。`eps_ratio` 是近似精度，太大角会丢，太小会保留很多点。",
            "如果 approx 不是 4 个点，不要硬做透视变换；先记录「失败」并回退到原图。",
        ),
        seg(
            "四个角排序",
            r'''
found = len(approx) == 4
warped = None
if found:
    pts = approx.reshape(4, 2).astype(np.float32)
    s = pts.sum(axis=1)
    d = pts.dot(np.array([1.0, -1.0], dtype=np.float32))
    rect = np.zeros((4, 2), dtype=np.float32)
    rect[0] = pts[np.argmin(s)]   # 左上：x+y 最小
    rect[2] = pts[np.argmax(s)]   # 右下：x+y 最大
    rect[1] = pts[np.argmax(d)]   # 右上：x-y 最大
    rect[3] = pts[np.argmin(d)]   # 左下：x-y 最小
    print("排序后:", rect.astype(int).tolist())
''',
            "`x+y` 最小的是左上，最大的是右下；`x−y` 最大的是右上，最小的是左下。这个技巧对旋转、轻微透视都成立。先把 rect 画到原图上检查顺序，再做后面的事。",
        ),
        seg(
            "构造目标矩形并做透视变换",
            r'''
if found:
    tl, tr, br, bl = rect
    width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
    height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))
    dst = np.array([
        [0, 0], [width - 1, 0],
        [width - 1, height - 1], [0, height - 1],
    ], dtype=np.float32)
    H = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, H, (int(width), int(height)))
    print("拉正后尺寸:", warped.shape)
    capture("拉正后的彩色图", warped)
''',
            "目标矩形的宽高取对边的最大长度，避免拉正后缺一条边。`getPerspectiveTransform` 需要 4 对点，返回 3×3 的 H；`warpPerspective` 按 H 重采样。",
            "宽高用 `int()` 转成整数；OpenCV 的 size 参数必须是整数。",
        ),
        seg(
            "二值化并输出",
            r'''
if found:
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    scan = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 12)
    result = scan
    metric("文档尺寸", "%dx%d" % (warped.shape[1], warped.shape[0]))
    metric("找到纸张", "是")
else:
    result = image.copy()
    cv2.putText(result, "paper not found", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
    metric("找到纸张", "否")
''',
            "拉正后用自适应阈值去掉阴影，得到接近扫描件的黑白图。真实扫描 App 还会做去噪、锐化、裁剪白边；这里先掌握核心四步。",
        ),
    ],
    tests=[
        test("成功找到纸张", "found is True"),
        test("四个角点", "len(approx) == 4"),
        test("透视结果非空", "warped is not None and warped.shape[1] > 300"),
        test("结果非空", "result is not None and result.size > 0"),
    ],
    params=[
        param("sat_max", "饱和度上限", 60, 30, 120, 5),
        param("val_min", "亮度下限", 140, 100, 210, 5),
        param("eps_ratio", "多边形近似比例", 0.08, 0.02, 0.15, 0.01),
    ],
    tasks=[
        task("dev", "按 A4 比例输出", "把目标宽高固定成 210:297 的比例，输出 1240×1754 的扫描件。"),
        task("dev", "画角点", "在 result 上用不同颜色标出 TL/TR/BR/BL 四个点，确认排序正确。"),
        task("tune", "换一张纸", "上传自己的文档照片，调 sat_max / val_min / eps_ratio 直到稳定找到四个角。"),
    ],
    quiz_items=[
        quiz("透视变换需要几对点？", ["2", "3", "4", "8"], 2,
             "单应矩阵 8 个自由度，需要 4 对点。"),
        quiz("四个角排序中，左上角通常满足？", ["x+y 最大", "x+y 最小", "x−y 最大", "x−y 最小"], 1,
             "左上角 x、y 都小，x+y 最小。"),
        quiz("为什么先 convexHull？", ["加速", "补回被遮挡的凹角", "改变颜色", "去噪"], 1,
             "纸边被压住时轮廓会凹进去，凸包先把外轮廓包回来。"),
    ],
    industry="手机扫描 App、票据录入、护照识别、PCB 对位都先做透视校正。校正后 OCR 识别率通常能明显提升；工业上还会用标定好的四角做像素→毫米映射。",
    career="开发型岗位要处理角点检测失败、顺序错、比例不对；调控型岗位要能根据现场照片快速调掩膜和近似参数。",
    next_step="下一课做定位：模板匹配与 ORB 特征，看看旋转、缩放时谁更稳。",
)

L6 = lesson(
    "cv-template-orb",
    "模板匹配与 ORB：旋转后还能找到吗",
    "matchTemplate 的局限、ORB 关键点、比值筛选、RANSAC 单应性",
    chapter="opencv",
    mode="vision",
    sample="pcb.jpg",
    template="pcb_template.png",
    difficulty=4,
    minutes=50,
    tags=["模板匹配", "ORB", "RANSAC"],
    objectives=[
        "用 matchTemplate 找到目标并解释分数含义",
        "用 ORB + BFMatcher + 比值筛选建立特征对应",
        "用 findHomography + RANSAC 在旋转场景中定位目标框",
    ],
    concept=[
        P("模板匹配把模板在图上逐像素滑动，算每个位置的相似度，取最大值。它快、简单，但对旋转、缩放、光照变化很敏感。ORB 则先找关键点、再算二进制描述子，通过匹配描述子建立对应，最后由单应性把模板框投影过去。"),
        TABLE(
            ["方法", "优点", "局限", "典型场景"],
            [
                ["matchTemplate", "实现简单、速度稳定", "旋转/缩放/遮挡易失败", "固定工位、固定姿态"],
                ["ORB + 单应性", "支持旋转、尺度、部分遮挡", "弱纹理目标特征少", "零件定位、AR、拼接"],
            ],
        ),
        FORMULA("good match: d1 < ratio · d2", "最近邻距离明显小于次近邻"),
        NOTE("先看数据再选方法", "这一课的 PCB 被旋转了 15°，模板匹配分数只有 0.25，但 ORB 仍有 200 多个好匹配。不是 ORB 更「高级」，而是它假设更少。", "tip"),
    ],
    walkthrough=[
        seg(
            "模板匹配",
            r'''
import cv2
import numpy as np

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
score_map = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
_, max_score, _, max_loc = cv2.minMaxLoc(score_map)
h, w = template_gray.shape
result = image.copy()
cv2.rectangle(result, max_loc, (max_loc[0] + w, max_loc[1] + h),
              (80, 220, 120), 3)
print("模板匹配最高分:", round(float(max_score), 3))
metric("模板匹配最高分", round(float(max_score), 3))
''',
            "`TM_CCOEFF_NORMED` 把相似度归一化到 -1–1，1 表示完全一致。`minMaxLoc` 同时给出最小/最大值及位置。旋转 15° 后分数只有 0.25，说明这个结果不可信。",
            "模板必须比原图小；模板尺寸变了，匹配结果也会变。",
        ),
        seg(
            "ORB 关键点与描述子",
            r'''
orb = cv2.ORB_create(nfeatures=2500)
kp_template, des_template = orb.detectAndCompute(template_gray, None)
kp_scene, des_scene = orb.detectAndCompute(gray, None)
print("模板关键点:", len(kp_template), "场景关键点:", len(kp_scene))
''',
            "ORB 先检测角点（FAST），再为每个关键点算一个 256 位的二进制描述子。`detectAndCompute` 一次完成两步。纹理越丰富（文字、走线、焊盘），关键点越多。",
            "如果 `des_template is None`，说明模板几乎没有纹理，ORB 不适合，应回到模板匹配或换目标。",
        ),
        seg(
            "匹配与比值筛选",
            r'''
matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
knn = matcher.knnMatch(des_template, des_scene, k=2)
ratio = float(p["ratio"])
good = [m for m, n in knn if m.distance < ratio * n.distance]
print("好匹配数量:", len(good))
metric("ORB 好匹配", len(good))
''',
            "对模板的每个描述子，在场景里找最近和次近的两个。如果最近的距离明显更小，说明这个对应是独特的；否则可能是重复纹理造成的歧义。`NORM_HAMMING` 是 ORB 二进制描述子的距离度量。",
        ),
        seg(
            "RANSAC 求单应性",
            r'''
H = None
if len(good) >= 8:
    src = np.float32([kp_template[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp_scene[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, inlier_mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    print("单应矩阵:", H is not None, "内点:", int(inlier_mask.sum()) if inlier_mask is not None else 0)
metric("单应矩阵", "成功" if H is not None else "失败")
''',
            "`findHomography` 用 RANSAC 随机抽 4 对点拟合，反复找内点最多的一组。`5.0` 是重投影误差阈值（像素）。好匹配里允许有错配，RANSAC 会把它们当外点丢掉。",
        ),
        seg(
            "把模板框投影到场景",
            r'''
if H is not None:
    th, tw = template_gray.shape
    corners = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(corners, H).astype(np.int32)
    cv2.polylines(result, [projected], True, (0, 220, 255), 4)
    cv2.putText(result, "ORB", (projected[0, 0, 0], max(30, projected[0, 0, 1] - 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2, cv2.LINE_AA)
''',
            "把模板的四个角用 H 变换到场景坐标，就得到旋转后的目标框。`perspectiveTransform` 一次变换多个点，比手动乘矩阵方便。",
            "投影后的坐标要转成 int32 才能给 `polylines`；越界点会被裁掉，不会崩。",
        ),
        seg(
            "可视化匹配",
            r'''
if len(good) > 0:
    vis = cv2.drawMatches(template, kp_template, image, kp_scene,
                          good[:40], None, flags=2)
    vis = cv2.resize(vis, (1200, int(vis.shape[0] * 1200 / vis.shape[1])))
    capture("ORB 匹配连线", vis)
''',
            "`drawMatches` 把两张图并排，画出匹配连线。只看内点会更干净；这里展示前 40 个，方便观察错配。",
        ),
    ],
    tests=[
        test("模板有足够关键点", "len(kp_template) > 100"),
        test("好匹配至少 8 对", "len(good) >= 8"),
        test("单应矩阵成功", "H is not None"),
        test("结果图尺寸不变", "result.shape == image.shape"),
    ],
    params=[
        param("ratio", "比值筛选阈值", 0.75, 0.55, 0.95, 0.01),
        param("match_threshold", "模板匹配可信阈值", 0.55, 0.3, 0.95, 0.05),
    ],
    tasks=[
        task("dev", "只画内点", "用 `inlier_mask` 过滤 good，只画 RANSAC 认可的内点连线。"),
        task("dev", "输出目标中心", "把 projected 的四个角求平均，得到目标中心像素坐标并打印。"),
        task("observe", "把图转正", "把 pcb.jpg 旋转回 0°，再比较模板匹配分数和 ORB 好匹配数量。"),
    ],
    quiz_items=[
        quiz("matchTemplate 的 TM_CCOEFF_NORMED 最大值代表？", ["位置", "相似度", "尺寸", "颜色"], 1,
             "归一化相关系数，1 表示最相似。"),
        quiz("ORB 描述子的距离用什么？", ["欧氏距离", "汉明距离", "余弦距离", "曼哈顿距离"], 1,
             "ORB 是二进制描述子，用汉明距离统计不同位的个数。"),
        quiz("RANSAC 的作用？", ["加速匹配", "剔除错配并拟合模型", "改变颜色", "放大图像"], 1,
             "随机采样一致性地拟合，外点不参与最终模型。"),
    ],
    industry="固定工位的零件定位常用模板匹配；机器人抓取、AR 标记、图像拼接更常用 ORB/SIFT + 单应性。近年深度学习特征（SuperPoint、LoFTR）在弱纹理和光照变化下更强，但 ORB 仍是轻量基线。",
    career="开发型岗位要能根据目标纹理、旋转、实时性选方法；调控型岗位要会看匹配连线，判断是特征太少还是比值阈值太严。",
    next_step="基础视觉到这里。下一章进入机器人任务：循迹、分拣、对接、标定和光流。",
)

CHAPTER = chapter(
    "opencv", "02", "OpenCV 视觉核心",
    "图像是数组，颜色是掩膜，结构是轮廓；每一课都围绕一个真实工位任务。",
    [NP, L1, L2, L3, L4, L5, L6],
    color="#5eead4", icon="02",
)
