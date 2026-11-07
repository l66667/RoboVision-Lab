# -*- coding: utf-8 -*-
"""第八章：3 个月冲刺与 GitHub 项目复刻。"""

from common import (
    P, H, UL, NOTE, TABLE, FORMULA, CODE, seg, param, test, task, quiz, lesson, chapter,
)

L1 = lesson(
    "github-rotation",
    "GitHub 复刻：旋转角检测的 Pick & Place 视觉",
    "SIFT + FLANN + RANSAC 单应，从参考图估计目标旋转角",
    chapter="project",
    mode="vision",
    sample="github_card_scene.jpg",
    template="github_card_ref.jpg",
    difficulty=4,
    minutes=60,
    tags=["GitHub", "SIFT", "单应", "复刻"],
    objectives=[
        "读懂一个真实 GitHub 视觉项目的核心流水线",
        "用 SIFT/FLANN/单应复现旋转角检测，并定位原项目的坑",
        "把结果整理成可复现的命令、指标和限制说明",
    ],
    concept=[
        P("这一课复刻的是 MIT 协议项目 **rotation-angle-detection-for-pick-place-robots**（作者 Sasiri Chathurika）：用参考图和现场图的特征匹配，估计目标的旋转角，让机械臂不用预先摆正工件。"),
        TABLE(
            ["信息", "内容"],
            [
                ["项目", "github.com/SasiriChathurika/rotation-angle-detection-for-pick-place-robots"],
                ["协议", "MIT（保留版权声明）"],
                ["方法", "SIFT 特征 + FLANN 最近邻 + 比值筛选 + RANSAC 单应"],
                ["输入", "参考图 + 摄像头帧（本课改成静态图）"],
                ["输出", "旋转角（度）+ 匹配可视化"],
            ],
        ),
        P("原仓库的 `code/main.py` 依赖摄像头、使用全局变量，并且没有相机标定。本课把它改成静态图、显式参数和可测试函数；这不是“抄一遍”，而是把别人的项目变成自己能维护的代码。"),
        NOTE("复刻不是复制粘贴", "至少做三件事：跑通、改一个缺陷、加一个指标/测试。只把代码下载下来跑一次，面试时讲不出东西。", "tip"),
        CODE(
            """# 原项目的核心逻辑（简化）
knn = flann.knnMatch(desc_ref, desc_scene, k=2)
good = [m for m, n in knn if m.distance < 0.6 * n.distance]
H, mask = cv2.findHomography(dst, src, cv2.RANSAC, 5.0)
angle = degrees(arctan2(H[1, 0], H[0, 0]))""",
            "python",
        ),
    ],
    walkthrough=[
        seg(
            "读取参考图与场景图",
            r'''
import cv2
import numpy as np

ref_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
scene_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print("参考图:", ref_gray.shape, "场景图:", scene_gray.shape)
''',
            "`template` 是 GitHub 仓库里的参考图，`image` 是旋转了约 15° 的场景图。真实项目里参考图是事先拍好的标准件，场景图来自相机。",
        ),
        seg(
            "SIFT 关键点",
            r'''
sift = cv2.SIFT_create()
kp_ref, desc_ref = sift.detectAndCompute(ref_gray, None)
kp_scene, desc_scene = sift.detectAndCompute(scene_gray, None)
print("参考图关键点:", len(kp_ref))
print("场景图关键点:", len(kp_scene))
metric("参考图关键点", len(kp_ref))
''',
            "SIFT 对旋转、尺度变化比较稳，适合有纹理的工件。弱纹理、重复纹理、反光会让关键点变少；这时要考虑 ORB、模板匹配或深度学习特征。",
        ),
        seg(
            "FLANN 匹配 + 比值筛选",
            r'''
flann = cv2.FlannBasedMatcher(dict(algorithm=0, trees=5), {})
knn = flann.knnMatch(desc_ref, desc_scene, k=2)
ratio = float(p["ratio"])
good = [m for m, n in knn if m.distance < ratio * n.distance]
print("好匹配:", len(good))
metric("好匹配", len(good))
''',
            "对每个参考描述子找最近和次近两个；最近的距离明显更小才保留。比值阈值太小会匹配不足，太大则错配增多。",
        ),
        seg(
            "RANSAC 单应",
            r'''
src = np.float32([kp_ref[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
dst = np.float32([kp_scene[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
H, inlier_mask = cv2.findHomography(dst, src, cv2.RANSAC, float(p["ransac"]))
inliers = int(inlier_mask.sum()) if inlier_mask is not None else 0
print("单应:", H is not None, "内点:", inliers)
metric("内点", inliers)
''',
            "`findHomography(dst, src)` 求的是“场景→参考”的变换，所以后面的角度符号与“参考→场景”相反。这个方向必须和机器人旋转方向约定一致。",
        ),
        seg(
            "提取旋转角并画匹配",
            r'''
angle = float(np.degrees(np.arctan2(H[1, 0], H[0, 0])))
if angle > 90:
    angle -= 180
elif angle <= -90:
    angle += 180
print("旋转角: %.2f deg" % angle)
metric("旋转角(deg)", round(angle, 2))

vis = cv2.drawMatches(ref_gray, kp_ref, scene_gray, kp_scene, good[:60], None, flags=2)
vis = cv2.resize(vis, (1280, int(vis.shape[0] * 1280 / vis.shape[1])))
result = vis
''',
            "单应矩阵左上 2×2 的旋转部分可以直接用 `atan2(H[1,0], H[0,0])` 取角。平面件有 180° 歧义，工业上常用不对称标记/纹理或额外传感器消除。",
        ),
        seg(
            "复现结果与限制",
            r'''
print("expected ~15 deg; got %.2f" % angle)
print("limitations: no camera calibration, no scale/depth, no conveyor tracking")
print("next: add calibration + hand-eye + robot pose")
metric("匹配通过", "是" if abs(angle - 15.0) < 2.0 else "否")
''',
            "这个项目只解决“角度”，没有解决“在哪里、离多远、怎么抓”。要接机械臂，还要补相机标定、手眼标定、像素→毫米/三维、抓取规划和异常处理。",
        ),
    ],
    tests=[
        test("好匹配超过 100", "len(good) > 100"),
        test("单应矩阵成功", "H is not None"),
        test("角度约 15 度", "abs(angle - 15.0) < 2.0"),
        test("结果图已生成", "result.ndim == 3"),
    ],
    params=[
        param("ratio", "Lowe 比值阈值", 0.6, 0.4, 0.9, 0.01),
        param("ransac", "RANSAC 阈值（px）", 5.0, 1.0, 12.0, 0.5),
    ],
    tasks=[
        task("dev", "改成函数", "把整段代码封装成 `detect_angle(ref, scene, ratio, ransac)`，返回角度、内点数、可视化图。"),
        task("dev", "加相机标定", "先用棋盘格标定，再去畸变后匹配，比较角度变化。"),
        task("dev", "接抓取位姿", "用单应把目标中心映射到工作台毫米坐标，输出 (x, y, angle)。"),
    ],
    quiz_items=[
        quiz("SIFT 相比模板匹配的优势？", ["更快", "支持旋转/尺度", "不需要图像", "自动标定"], 1,
             "SIFT 特征具有旋转/尺度不变性。"),
        quiz("比值筛选的作用？", ["加速", "去掉歧义匹配", "改变颜色", "提高分辨率"], 1,
             "最近邻明显优于次近邻才保留，减少重复纹理错配。"),
        quiz("这个 GitHub 项目缺什么？", ["特征匹配", "相机标定/手眼/深度", "单应矩阵", "旋转角"], 1,
             "README 明确说没有相机标定；接机器人还需要手眼和坐标变换。"),
    ],
    industry="GitHub 上有大量视觉抓取项目，但能直接上产线的很少。真正的工程化要补标定、手眼、节拍、异常处理、日志和回归测试；复刻的价值是学会读别人的流水线并指出边界。",
    career="视觉应用开发要能选型、复现、改缺陷、补标定；调控岗位要能判断匹配失败是纹理、光照、运动模糊还是参数问题。",
    next_step="ROS2 + OpenCV 主线到这里闭环；GitHub 复刻作为选修，做完把 README、指标和限制写清楚。",
)

CHAPTER = chapter(
    "project", "10", "GitHub 复刻（选修）",
    "用真实 GitHub 项目练“读—跑—改—测”，把 OpenCV 视觉流水线收束成作品集。",
    [L1],
    color="#a3e635", icon="10",
)
