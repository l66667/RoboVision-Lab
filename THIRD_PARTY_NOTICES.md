# 第三方声明

本项目整体采用 MIT 协议（见根目录 `LICENSE`）。以下第三方内容/依赖按其各自协议使用。

## GitHub 复刻项目

- 项目：`rotation-angle-detection-for-pick-place-robots`
- 作者：Sasiri Chathurika
- 链接：<https://github.com/SasiriChathurika/rotation-angle-detection-for-pick-place-robots>
- 协议：MIT
- 位置：`projects/github-rotation/`
- 说明：`main_static.py` 是对原项目核心流水线的静态图改写；`data/samples/github_card_ref.jpg` 来自原仓库，`github_card_scene.jpg` 由原图旋转生成。原项目完整 MIT 文本见 `projects/github-rotation/LICENSE`。

## 运行时依赖（不随仓库提交）

`runtime/` 被 `.gitignore` 排除，不进入 Git。`setup.bat` / `requirements.txt` 会安装：

- Python（PSF License）
- OpenCV / opencv-contrib-python（Apache-2.0）
- NumPy（BSD-3-Clause）

这些依赖的许可证以各自发行包为准。

## 图片与截图

`docs/` 下的界面截图由本项目生成；`data/samples/` 除 GitHub 项目样图外，均为脚本生成的合成图。

如发现遗漏的第三方内容，请开 issue 补充。
