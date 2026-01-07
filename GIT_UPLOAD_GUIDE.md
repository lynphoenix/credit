# Git 代码上传指引

## 准备工作

### 1. 安装 Git（如果未安装）

**Windows**:
- 下载安装: https://git-scm.com/download/win
- 或使用 `winget install Git.Git`

**Ubuntu**:
```bash
sudo apt update
sudo apt install git -y
```

### 2. 配置 Git 用户信息

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

## 创建 .gitignore 文件

在项目根目录创建 `.gitignore` 文件，避免上传不必要的文件：

```bash
# 在项目目录下执行
cd D:\work\code\credit
```

创建 `.gitignore` 文件内容（已为您生成在下方）

## 初始化 Git 仓库

### 方式一：从本地开始（推荐）

```bash
# 1. 进入项目目录
cd D:\work\code\credit

# 2. 初始化 Git 仓库
git init

# 3. 添加所有文件
git add .

# 4. 创建第一次提交
git commit -m "Initial commit: 海关证件识别与鉴伪系统"

# 5. 创建主分支（如果使用main而不是master）
git branch -M main
```

### 方式二：从现有仓库克隆

如果您已经在 GitHub/GitLab 等平台创建了仓库：

```bash
# 1. 克隆空仓库
git clone <你的仓库URL>

# 2. 将项目文件复制到克隆的目录
cp -r D:\work\code\credit/* <克隆目录>/

# 3. 添加并提交
cd <克隆目录>
git add .
git commit -m "Initial commit: 海关证件识别与鉴伪系统"
```

## 连接到远程仓库

### GitHub 示例

**1. 在 GitHub 上创建新仓库**
- 访问: https://github.com/new
- 仓库名: `credit-detection-system`
- 选择: Private（私有）或 Public（公开）
- **不要**勾选 "Initialize with README"

**2. 连接本地仓库到 GitHub**

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/credit-detection-system.git

# 推送代码
git push -u origin main
```

**3. 如果使用 SSH 密钥（推荐）**

生成 SSH 密钥:
```bash
ssh-keygen -t ed25519 -C "你的邮箱@example.com"
```

添加到 GitHub:
- 访问: https://github.com/settings/keys
- 点击 "New SSH key"
- 复制 `~/.ssh/id_ed25519.pub` 内容并粘贴

使用 SSH URL:
```bash
git remote set-url origin git@github.com:你的用户名/credit-detection-system.git
git push -u origin main
```

### GitLab 示例

```bash
# 添加 GitLab 远程仓库
git remote add origin https://gitlab.com/你的用户名/credit-detection-system.git
git push -u origin main
```

### 私有 Git 服务器示例

```bash
# 添加自建 Git 服务器
git remote add origin git@your-server.com:path/to/credit-detection-system.git
git push -u origin main
```

## 推送代码到 Ubuntu 服务器

### 方式一：通过 Git（推荐）

**在 Ubuntu 服务器上**:
```bash
# 1. 克隆仓库
cd ~
git clone <你的仓库URL> credit

# 2. 进入项目目录
cd credit

# 3. 运行部署脚本
bash deploy_ubuntu_gpu.sh
```

### 方式二：使用 rsync 直接传输

**从 Windows 传输到 Ubuntu**:

使用 WSL 或 Git Bash:
```bash
# 同步整个项目目录（排除不必要的文件）
rsync -avz --exclude='uploads/*' \
           --exclude='database/*' \
           --exclude='test_results/*' \
           --exclude='__pycache__' \
           --exclude='*.pyc' \
           --exclude='.git' \
           /d/work/code/credit/ \
           username@ubuntu-server-ip:~/credit/
```

或使用 SCP:
```bash
# 打包项目
cd D:\work\code\credit
tar --exclude='uploads' --exclude='database' --exclude='test_results' \
    --exclude='__pycache__' --exclude='*.pyc' \
    -czf credit.tar.gz .

# 传输到服务器
scp credit.tar.gz username@ubuntu-server-ip:~/

# 在服务器上解压
ssh username@ubuntu-server-ip
tar -xzf credit.tar.gz -C ~/credit/
cd ~/credit
bash deploy_ubuntu_gpu.sh
```

### 方式三：使用 WinSCP 图形界面

1. 下载 WinSCP: https://winscp.net/
2. 连接到 Ubuntu 服务器
3. 将项目文件拖拽上传到 `~/credit/` 目录
4. 使用 SSH 登录服务器运行部署脚本

## 日常 Git 操作

### 修改代码后提交

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .                    # 添加所有修改
git add file1.py file2.py   # 添加特定文件

# 3. 提交修改
git commit -m "描述本次修改内容"

# 4. 推送到远程仓库
git push
```

### 在服务器上更新代码

```bash
# 在 Ubuntu 服务器上
cd ~/credit

# 停止服务
./stop_server.sh

# 拉取最新代码
git pull

# 重启服务
./start_server.sh
```

### 查看提交历史

```bash
git log --oneline          # 简洁显示
git log --graph --all      # 图形化显示
```

### 创建分支进行开发

```bash
# 创建并切换到新分支
git checkout -b feature-new-detection

# 开发完成后提交
git add .
git commit -m "添加新的检测功能"

# 推送分支到远程
git push -u origin feature-new-detection

# 切换回主分支
git checkout main

# 合并分支
git merge feature-new-detection
```

## 团队协作

### 克隆项目

团队成员获取代码:
```bash
git clone <仓库URL>
cd credit-detection-system
```

### 保持代码同步

```bash
# 拉取最新代码
git pull

# 如果有冲突，手动解决后
git add .
git commit -m "解决合并冲突"
git push
```

## 重要文件说明

上传到 Git 的核心文件:
- ✅ `*.py` - 所有 Python 代码
- ✅ `*.sh` - 部署和管理脚本
- ✅ `*.yml` - Conda 环境配置
- ✅ `*.md` - 文档文件
- ✅ `requirements.txt` - Python 依赖
- ✅ `config.py` - 配置文件
- ❌ `uploads/` - 上传文件目录（不上传）
- ❌ `database/` - 数据库文件（不上传）
- ❌ `test_results/` - 测试结果（不上传）
- ❌ `books/` - 证书样本图片（可选，如果很大建议不上传）
- ❌ `__pycache__/` - Python 缓存（不上传）
- ❌ `.git/` - Git 元数据（自动管理）

## 故障排除

### 推送被拒绝

```bash
# 先拉取远程更新
git pull --rebase origin main

# 解决冲突后推送
git push origin main
```

### 撤销最后一次提交

```bash
# 保留修改
git reset --soft HEAD^

# 不保留修改
git reset --hard HEAD^
```

### 查看远程仓库

```bash
git remote -v
```

### 修改远程仓库 URL

```bash
git remote set-url origin <新的URL>
```

## 快速部署流程总结

**完整流程**:

1. **本地提交代码**
   ```bash
   cd D:\work\code\credit
   git add .
   git commit -m "更新部署配置和GPU支持"
   git push
   ```

2. **服务器获取代码**
   ```bash
   ssh username@ubuntu-server
   cd ~
   git clone <你的仓库URL> credit
   cd credit
   ```

3. **部署应用**
   ```bash
   bash deploy_ubuntu_gpu.sh
   ```

4. **启动服务**
   ```bash
   ./start_server.sh
   # 或使用 systemd
   sudo systemctl start credit-detection
   ```

5. **测试服务**
   ```bash
   curl http://localhost:5000
   ```

完成！您的应用已在 Ubuntu GPU 服务器上运行。
