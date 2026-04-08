# AI 模拟面试与能力培养平台 (AI Mock Interview & Training Platform)

基于大语言模型与多智能体架构（Multi-Agent）的高校学生全真模拟面试与能力提升平台。本系统旨在帮助应届生通过基于简历定制的自动化面试、编程测试、维度评分及专属培养方案，提升求职竞争力。

## 🌟 核心功能 (Core Features)

1. **智能简历解析与定制化提问**
   - 支持上传 PDF 简历，系统自动提取面试者基本信息、意向岗位、项目经历及核心技术栈。
   - 动态生成 12 道针对性面试题（围绕提取的技术关键字），并支持根据用户的回答进行深度追问（每个大题最多两次追问）。

2. **多模态交互式面试 (Text & Voice)**
   - 支持纯文本作答与语音语义作答。
   - 接入 **阿里 SenseVoice** 大模型，实现高精度的语音转文字识别，深度模拟真实面试交流场景。

3. **在线编程测试 (Coding Test)**
   - 类似真实笔试的在线 OJ 系统体验，集成 `Vue-Codemirror` 实现代码高亮和语法错误提示。
   - 支持 Python, Java, C++, JavaScript 等多种语言。
   - 包含 3 道梯度题目（Debug纠错、基础编程、进阶综合抗压），并带有倒计时限时机制。

4. **全方位评估与专属培养方案**
   - **多智能体协作 (CrewAI)**：由 Appraiser（评估师）和 Mentor（培养师）等 Agent 联合工作。
   - **雷达图评估**：综合评估候选人的“专业技术模块”与“核心软素质模块”，并以可视化雷达图展示。
   - **竞争力评级**：打出综合 S/A/B/C/D 竞争力评级，并提供详尽的优缺点逐题点评分析。
   - **可落地培养方案**：针对候选人表现，提供短期与长期结合、具备真实链接和可操作性的能力提升及简历修改指南。

5. **知识图谱管理 (Knowledge Graph)**
   - 后台基于 Neo4j 构建“岗位-技能-问题”星状知识图谱。
   - 提供管理员专属看板（力导向图可视化），直观显示技术栈与面试题的关联，支持动态添加与删除图谱节点。

## 🛠️ 技术栈 (Tech Stack)

### 前端 (Frontend)
- **框架**: Vue 3 + Vite
- **路由 & 状态**: Vue Router
- **可视化**: Chart.js / vue-chartjs (雷达图)
- **代码编辑器**: Vue-Codemirror 6
- **图引擎**: Neo4j-driver / Vis-Network

### 后端与 AI (Backend & AI)
- **主框架**: FastAPI (Python)
- **AI 编排**: CrewAI (多智能体架构框架)
- **大预言模型**: DeepSeek API (核心推理与生成)
- **语音识别**: Alibaba Cloud SenseVoice (FunASR/torchaudio)
- **数据库**: SQLite (`interview.db` 用于存储用户信息) + Neo4j (知识图谱)

### 第三方服务 (3rd-Party Services)
- 阿里云短信服务 (Aliyun SMS) - 验证码登录注册功能。

## 🚀 快速启动 (Getting Started)

### 1. 环境准备 (Prerequisites)
- [Node.js](https://nodejs.org/) (建议 18+)
- [Python](https://www.python.org/) 3.10+ (建议使用 Conda 虚拟环境)
- FFmpeg (用于音频处理及 SenseVoice 解析)
- Neo4j 实例 (本地或 AuraDB 云端)

### 2. 前端部署 (Frontend Setup)
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器 (默认端口 3000 左右)
npm run dev
```

### 3. 后端部署 (Backend Setup)
后端主要分为两个服务模块：主线模拟面试 API 与 SenseVoice 语音识别 API。

```bash
cd mock_interview

# 创建并激活虚拟环境 (推荐)
conda create -n ai-interview python=3.10
conda activate ai-interview

# 安装依赖
pip install -r requirements.txt
pip install fastapi uvicorn funasr torchaudio

# 配置环境变量 (.env)
# 根目录下需要创建 .env 文件，填入：
# DEEPSEEK_API_KEY=xxx
# ALIYUN_ACCESS_KEY_ID=xxx
# ALIYUN_ACCESS_KEY_SECRET=xxx
# NEO4J_URI=xxx
# NEO4J_USER=xxx
# NEO4J_PASSWORD=xxx

# 启动主核心 API (端口 8010)
cd api
uvicorn main:app --host 127.0.0.1 --port 8010 --reload

# 启动 SenseVoice 语音识别 API (端口 8020)
uvicorn sensevoice_api:app --host 127.0.0.1 --port 8020 --reload
```

## 📂 项目结构主要说明 (Project Structure)
- `/frontend`: Vue3 前端源码目录。包含 `/src/views` (配置页、面试页、语音面试、结果报表、知识图谱后台等)。
- `/mock_interview`: Python 后端目录。
  - `/api`: FastAPI 路由控制器。
  - `/crew`: CrewAI 智能体核心逻辑 (生成面试题、评估及导师Agent)。
  - `/utils`: 常用工具与服务 (大模型请求, PDF解析, 日志等)。

## 📝 注意事项
- 由于系统调用了真实的 LLM 和阿里云服务，请务必保证配置文件（`.env`）中的 Token/Key 真实有效。
- Windows 环境下进行语音测试时，若遇到缺少 `ffprobe` / `ffmpeg` 报错，请手动下载 FFmpeg 并将其 bin 目录配置到系统环境变量 `PATH` 中。

