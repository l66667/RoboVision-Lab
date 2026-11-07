# 归档课程（不在 100 天主线上）

这里保留早期扩展的 Halcon / 手眼 / FOC / EtherCAT / 驱控一体课程源码，方便以后单独开方向时复用。

- `ch6_halcon.py`：Halcon 入门、手眼标定、Halcon Pick
- `ch7_motion.py`：FOC、电流环、EtherCAT、CSP/CSV/CST

当前 `tools/build_lessons.py` **不会加载本目录**，所以软件里不显示这些章节。  
如果以后要恢复，把它们移回 `content/` 并加入 `MODULES`，同时补回技能地图/路线图即可。

归档原因：当前主线聚焦 **OpenCV + ROS2 工程**，100 天内不铺开商业视觉库和电机控制；先就业/实习最需要的接口、CMake、colcon 优先。
