# 把 RoboVision Lab 发布到 GitHub

> 目标：把项目目录（例如 `$env:USERPROFILE\Desktop\RoboVision-Lab`）变成一个干净的 GitHub 仓库，**不包含** 216MB 的 `runtime/`、API key、运行产物。
>
> 当前这台电脑还没装 Git。先装 Git，再按下面做。

---

## 0. 发布前检查（已经帮你准备好）

仓库根目录现在有：

- `LICENSE`：MIT
- `THIRD_PARTY_NOTICES.md`：GitHub 复刻项目/依赖的第三方声明
- `.gitignore`：已排除 `runtime/`、`runs/`、`tmp/`、`.server.json`、`data/ai_config.json`、`__pycache__/`、`result.jpg` 等
- `README.md`、`100天ROS2计划.md`、`代码阅读检查表.md`
- `docs/` 截图，`projects/github-rotation/` 复刻项目

**绝对不要提交：**

| 路径 | 原因 |
|---|---|
| `runtime/` | 本地 Python 环境，约 216MB，含二进制 |
| `data/ai_config.json` | 可能含 API key |
| `.server.json` | 本机端口/局域网信息 |
| `runs/`、`tmp/` | 运行产物、测试缓存 |
| `projects/github-rotation/result.jpg` | 每次运行生成的结果图 |

这些已经在 `.gitignore` 里；但第一次 `git add` 后仍要用 `git status` 确认。

---

## 1. 安装 Git

下载：<https://git-scm.com/download/win>

安装时保持默认即可（会装 Git Credential Manager）。装完**重新打开 PowerShell**：

```powershell
git --version
```

第一次使用配置身份：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

邮箱最好和 GitHub 账号一致。

---

## 2. 在 GitHub 创建空仓库

1. 登录 GitHub，右上角 **+ → New repository**。
2. 名字建议：`RoboVision-Lab`（或 `robovision-lab`）。
3. 可见性：Public（想开源）或 Private。
4. **不要勾选** Add a README / .gitignore / license——本地已经有，避免第一次推送冲突。
5. 创建后复制仓库地址：

```text
https://github.com/<你的用户名>/RoboVision-Lab.git
```

---

## 3. 本地初始化并推送

在 PowerShell 里：

```powershell
cd $env:USERPROFILE\Desktop\RoboVision-Lab

git init
git add .
git status --short
```

### 先看 `git status`，确认没有这些：

```text
runtime/
runs/
tmp/
data/ai_config.json
.server.json
__pycache__/
```

如果出现了，先修正：

```powershell
git rm -r --cached runtime
git rm --cached data/ai_config.json
git rm --cached .server.json
```

> `git rm --cached` 只是从 Git 索引移除，不删本地文件。

确认干净后提交：

```powershell
git commit -m "feat: initial RoboVision Lab - OpenCV + ROS2 learning app"
git branch -M main
git remote add origin https://github.com/<你的用户名>/RoboVision-Lab.git
git push -u origin main
```

第一次 `push` 会弹出浏览器登录 GitHub，点授权即可。

---

## 4. 认证方式（三选一）

### 推荐：Git Credential Manager

安装 Git for Windows 时自带。`git push` 弹窗后浏览器登录，之后自动记住。

### 备选：Personal Access Token（PAT）

GitHub 已不支持账号密码。用 PAT：

1. GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)**。
2. Generate new token，勾选 `repo`（私有仓库必须；公开也建议）。
3. 复制 token，`git push` 时用户名填 GitHub 用户名，密码填 token。
4. **不要把 token 写进远程 URL 或 README**；泄露后立即 revoke。

### 备选：SSH

```powershell
ssh-keygen -t ed25519 -C "你的邮箱"
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

把输出的公钥加到 GitHub → Settings → SSH and GPG keys → New SSH key。然后：

```powershell
git remote set-url origin git@github.com:<你的用户名>/RoboVision-Lab.git
git push -u origin main
```

---

## 5. 常见问题

### `remote origin already exists`

```powershell
git remote -v
git remote set-url origin https://github.com/<你的用户名>/RoboVision-Lab.git
```

### `failed to push some refs` / 远端有 README

```powershell
git pull --rebase origin main
git push -u origin main
```

不要一上来 `git push -f`；只有在确认远端没有你要保留的内容时才强推。

### 文件太大 / `GH001`

说明 `runtime/` 或大文件被加进去了：

```powershell
git rm -r --cached runtime
git commit -m "chore: remove local runtime from git"
git push
```

GitHub 单文件上限 100MB；`runtime/` 里很多文件会超标。

### 推送后还能看到 `data/ai_config.json`

```powershell
git rm --cached data/ai_config.json
git commit -m "chore: remove local API config"
git push
```

**只要 key 曾经被 push 过，就要去模型平台 revoke/轮换。** 删文件不等于从历史消失；必要时用 `git filter-repo` 或 BFG 清理历史。

### 国内访问 GitHub 慢/失败

- 先确认能打开 <https://github.com>；
- 用 SSH 或代理；
- 不要为了推代码把 token 发到聊天/群里。

---

## 6. 仓库设置建议

在 GitHub 仓库页面：

- **Description**：

```text
OpenCV + ROS2 机器人视觉工程学习台：32 节课程、100 天路线、可运行 Python/OpenCV 实验。
```

- **Topics**：

```text
robotics, computer-vision, opencv, ros2, python, education, robot-programming
```

- **About → Website**：暂时留空。  
  **不要开 GitHub Pages**：这个软件需要本地 Python 后端，Pages 只能托管静态页面，跑不了课程代码。

### 打一个版本 tag

```powershell
git tag -a v1.0.0 -m "RoboVision Lab v1.0.0"
git push origin v1.0.0
```

然后在 GitHub → Releases → Draft a new release，选择 `v1.0.0`，写更新说明。  
**不要上传 `runtime/` 压缩包**；用户用 `setup.bat` 自建环境。

---

## 7. 发布后自检

换一个临时目录克隆，确认别人能跑：

```powershell
cd $env:TEMP
git clone https://github.com/<你的用户名>/RoboVision-Lab.git
cd RoboVision-Lab
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

浏览器打开 `http://127.0.0.1:8770/`。

如果克隆里没有 `runtime/`，这是正常的；`setup.bat` 会创建。

---

## 8. 安全 / 隐私清单

- [ ] `git status` 没有 `runtime/`、`runs/`、`tmp/`
- [ ] 没有 `data/ai_config.json`、`.server.json`
- [ ] 没有 token、私钥、`.env`
- [ ] `docs/` 截图里的局域网 IP 已打码/可接受
- [ ] `LICENSE` 和 `THIRD_PARTY_NOTICES.md` 已提交
- [ ] 如果 key 曾泄露，已 revoke/轮换
- [ ] 仓库是 Public 还是 Private 已确认
- [ ] Git 提交邮箱是否愿意公开；介意就用 GitHub noreply 邮箱
- [ ] **没有用 GitHub 网页上传整个文件夹**（网页上传不读取 `.gitignore`）

> `data/ai_config.json` 里是真实 API key。只要它被 push 过一次，就算后来删除文件，历史里仍然存在；必须先去模型平台 revoke，再用 BFG / git filter-repo 清历史。最省事的做法：**不要提交它**。

Git 邮箱隐私：

```powershell
git config --global user.email "你的ID+用户名@users.noreply.github.com"
```

GitHub → Settings → Emails → Keep my email addresses private 也可以隐藏真实邮箱。

---

## 9. 不想用命令行：GitHub Desktop

1. 安装 GitHub Desktop，登录账号。
2. **File → Add local repository**，选项目目录。
3. 它会读取 `.gitignore`；在 Changes 里确认没有 `runtime/`。
4. 填 Summary → **Commit to main**。
5. **Publish repository**，选择 Public/Private。
6. 之后每次改完：写 summary → Commit → Push origin。

GUI 更直观，但 `.gitignore` 和“不要提交 key”的检查同样要做。

---

## 10. 一句话流程

```powershell
cd $env:USERPROFILE\Desktop\RoboVision-Lab
git init
git add .
git status --short          # 确认没有 runtime / key
git commit -m "feat: initial RoboVision Lab"
git branch -M main
git remote add origin https://github.com/<你>/RoboVision-Lab.git
git push -u origin main
```

推送成功后，把仓库地址发给我，我可以继续帮你检查 README 首屏、目录结构和 Release 说明。
