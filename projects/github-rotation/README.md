# GitHub 复刻：旋转角度检测（Pick & Place）

本目录复刻并改写了这个 MIT 协议项目：

- 原项目：<https://github.com/SasiriChathurika/rotation-angle-detection-for-pick-place-robots>
- 作者：Sasiri Chathurika
- 协议：MIT（见 `LICENSE`）

原项目用 SIFT + FLANN + 单应矩阵，从摄像头画面估计目标相对参考图的旋转角，用于让机械臂按任意角度抓取。  
原脚本依赖摄像头和全局变量，本目录的 `main_static.py` 做了三件事：

1. 改成读两张静态图，便于离线复现和做回归测试；
2. 把关键点/描述子作为参数传入函数，去掉全局变量；
3. 增加 inlier 数量、角度周期归一等诊断输出。

## 运行

在项目根目录：

```powershell
runtime\Scripts\python.exe projects\github-rotation\main_static.py
```

或指定图片：

```powershell
runtime\Scripts\python.exe projects\github-rotation\main_static.py ^
  data\samples\github_card_ref.jpg ^
  data\samples\github_card_scene.jpg ^
  projects\github-rotation\result.jpg
```

预期输出：

```text
good matches: 180+
inliers: 170+
rotation: ~15 deg
```

## 复现步骤（从 GitHub 开始）

```bash
git clone https://github.com/SasiriChathurika/rotation-angle-detection-for-pick-place-robots.git
cd rotation-angle-detection-for-pick-place-robots
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

原项目需要摄像头；先在 `code/main.py` 里确认 `REFERENCE_IMAGE_PATH` 和 `cv2.VideoCapture(0)`。  
没有摄像头时，用本目录的静态版验证算法，再把函数接回视频流。

## 这个项目教什么 / 不教什么

- 教：SIFT 特征、FLANN 最近邻、比值筛选、RANSAC 单应、旋转角提取、特征匹配可视化。
- 不教：相机标定、手眼标定、深度/尺度、传送带跟踪、抓取规划、运动控制。
- 原项目明确说明没有相机标定，镜头畸变会影响角度和定位精度；工业落地要补标定和手眼。

## 关键代码

```python
knn = flann.knnMatch(desc_ref, desc_scene, k=2)
good = [m for m, n in knn if m.distance < 0.6 * n.distance]

src = np.float32([kp_ref[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
dst = np.float32([kp_scene[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
H, mask = cv2.findHomography(dst, src, cv2.RANSAC, 5.0)

angle = np.degrees(np.arctan2(H[1, 0], H[0, 0]))
```

注意 `findHomography(dst, src)` 的方向：这里求的是“场景 → 参考”的变换，所以角度符号与“参考 → 场景”相反。工业代码里要统一约定，否则机械臂会反向转。

## 许可证

原项目 MIT。复制、修改、商用请保留原版权声明和 `LICENSE`。
