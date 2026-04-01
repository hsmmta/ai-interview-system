<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>已开始面试 - AI 模拟面试平台</title>
    <style>
        :root {
            --primary-color: #4A90E2;
            --bg-color: #F8F9FA;
            --header-height: 60px;
            --sidebar-width: 280px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg-color);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* 顶部导航 */
        .header {
            height: var(--header-height);
            background: white;
            border-bottom: 1px solid #eaeaea;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 24px;
            flex-shrink: 0;
            z-index: 10;
        }
        .brand { font-weight: 700; font-size: 18px; color: #333; display: flex; align-items: center; gap: 8px; }
        .brand span { color: var(--primary-color); }
        .progress-indicator {
            font-size: 14px;
            color: #666;
            background: #f0f0f0;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
        }

        /* 主体布局 */
        .main-wrapper {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        /* 左侧侧边栏 */
        .sidebar {
            width: var(--sidebar-width);
            background: white;
            border-right: 1px solid #eaeaea;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .sidebar-title { font-size: 12px; text-transform: uppercase; color: #999; margin-bottom: 16px; font-weight: 700; letter-spacing: 0.5px; }
        .question-list { list-style: none; }
        .question-item {
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            color: #555;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            border: 1px solid transparent;
        }
        .question-item:hover { background: #f5f9ff; }
        .question-item.active {
            background: #eefaee;
            border-color: #cfd;
            color: #2e7d32;
            font-weight: 600;
        }
        .question-item.completed .status-dot { background: #4caf50; }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ddd;
            margin-right: 12px;
        }

        /* 答题区域 */
        .content-area {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
            display: flex;
            justify-content: center;
        }
        .question-card {
            width: 100%;
            max-width: 800px;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            min-height: 500px;
            display: flex;
            flex-direction: column;
        }

        .loading-state { text-align: center; color: #999; margin-top: 100px; }

        .q-tag {
            display: inline-block;
            background: #e8f0fe;
            color: var(--primary-color);
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 16px;
        }

        .q-text {
            font-size: 18px;
            line-height: 1.6;
            color: #2c3e50;
            margin-bottom: 24px;
            font-weight: 500;
        }

        textarea {
            width: 100%;
            flex: 1;
            min-height: 300px;
            padding: 20px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            font-family: "Menlo", "Monaco", "Courier New", monospace;
            resize: none;
            transition: all 0.3s;
            background: #fafafa;
            color: #333;
            line-height: 1.6;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            background: white;
            box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
        }

        .action-bar {
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-secondary { background: #f0f0f0; color: #555; }
        .btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-secondary:hover:not(:disabled) { background: #e0e0e0; }

        .btn-primary { background: var(--primary-color); color: white; }
        .btn-primary:hover { background: #357ABD; box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3); }

        .btn-success { background: #52c41a; color: white; }
        .btn-success:hover { background: #389e0d; box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3); }

        /* 新增：子问题样式 */
        .q-context {
            font-size: 16px;
            color: #555;
            background: #f4f8fb;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            margin-bottom: 24px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .sub-q-item {
            margin-bottom: 30px;
        }
        .sub-q-label {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        .sub-answer-box {
            width: 100%;
            min-height: 150px;
            padding: 16px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            line-height: 1.6;
            resize: vertical;
            transition: all 0.2s;
            font-family: inherit;
        }
        .sub-answer-box:focus {
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
        }

    </style>
</head>
<body>
<div class="header">
    <div class="brand"> <span>AI 面试进行中</span></div>
    <div class="progress-indicator" id="progress">准备就绪</div>
</div>

<div class="main-wrapper">
    <!-- 侧边栏列表 -->
    <div class="sidebar">
        <div class="sidebar-title">题目列表</div>
        <ul class="question-list" id="sidebarList">
            <!-- 动态生成 -->
        </ul>
    </div>

    <!-- 主展示区 -->
    <div class="content-area">
        <div id="loading" class="loading-state">
            <p> 正在生成专属面试题，请稍候...</p>
        </div>

        <div id="questionBox" class="question-card" style="display: none;">
            <div>
                <span class="q-tag" id="questionType">简答题</span>
            </div>

            <div id="dynamicContainer">
                <!-- 动态生成的内容区域 -->
            </div>

            <div class="action-bar">
                <button class="btn btn-secondary" id="prevBtn">上一题</button>
                <div>
                   <button class="btn btn-primary" id="nextBtn" style="margin-right: 10px;">下一题</button>
                   <button class="btn btn-success" id="submitBtn" style="display: none;">提交试卷</button>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="questionTitle" style="display:none;"></div>

<script>
    const base = "<%= request.getContextPath() %>";
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("sessionId");
    const configuredQuestionCount = Number(urlParams.get("questionCount") || 0);

    let questions = [];
    let answers = []; // 依然存储最终的合并答案字符串，用于侧边栏状态和提交
    let questionStates = []; // 存储每道题的子问题状态和子答案 { parsed: {context, subs}, subAnswers: [] }
    let currentIndex = 0;
    let displayTotalCount = configuredQuestionCount > 0 ? configuredQuestionCount : 0;

    function normalizeQuestionType(t) {
        if (!t) return "题目";
        if (t === "short_answer") return "简答题";
        if (t === "coding") return "编程题";
        return t;
    }

    function normalizeQuestions(rawList) {
        if (!Array.isArray(rawList)) return [];
        return rawList.map((q, idx) => ({
            id: q.id != null ? q.id : (idx + 1),
            type: q.type || "short_answer",
            content: (q.content != null ? q.content : q.question) || ""
        }));
    }

    async function parseJsonSafe(res) {
        const text = await res.text();
        if (!text) return {};
        try {
            return JSON.parse(text);
        } catch (e) {
            throw new Error("服务端返回了非JSON: " + text);
        }
    }

    /**
     * 解析题目内容，分离上下文和子问题
     */
    function parseQuestionContent(content) {
        if (!content) return { context: "", subs: [] };

        // 简单判断是否有特定列表结构 (包含换行符 和 "- ")
        if (!content.includes("\n") || !/-\s/.test(content)) {
             return { context: "", subs: [content] };
        }

        const lines = content.split('\n');
        let contextLines = [];
        let subs = [];
        let foundFirstBullet = false;

        lines.forEach(line => {
            const trimmed = line.trim();
            // 匹配 "- " 或 "- 追问" 开头的行
            if (trimmed.startsWith("-")) {
                foundFirstBullet = true;
                // 去除开头的 "- ", "- 追问", "- 追问1：" 等
                // Regex: 匹配 "- " 后可能跟的 "追问" + 数字 + 冒号
                let clean = trimmed.replace(/^-\s*(追问\d*[：:]?)?\s*/, '');
                subs.push(clean);
            } else {
                if (!foundFirstBullet) {
                    contextLines.push(line);
                } else {
                    // 属于上一个问题的多行内容
                    if (subs.length > 0) {
                        subs[subs.length - 1] += "\n" + line;
                    } else {
                        // 异常情况，追加到上下文
                        contextLines.push(line);
                    }
                }
            }
        });

        return {
            context: contextLines.join('\n').trim(),
            subs: subs.length > 0 ? subs : [content]
        };
    }

    window.addEventListener("load", async () => {
        if (!sessionId) {
            alert("缺少 sessionId，请从配置页重新进入");
            return;
        }

        try {
            const res = await fetch(base + "/api/interview/generate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({sessionId: Number(sessionId)})
            });

            const data = await parseJsonSafe(res);
            if (!res.ok) {
                throw new Error(data.error || ("题目生成失败，HTTP " + res.status));
            }

            const rawQuestions =
                data.questions ||
                (data.data && data.data.questions) ||
                (data.result && data.result.questions) ||
                [];

            questions = normalizeQuestions(rawQuestions);

            if (questions.length === 0) {
                throw new Error("题目生成成功，但题目列表为空");
            }

            if (displayTotalCount <= 0) {
                displayTotalCount = questions.length;
            }

            answers = new Array(questions.length).fill("");
            questionStates = new Array(questions.length).fill(null); // 初始化状态数组

            document.getElementById("loading").style.display = "none";
            document.getElementById("questionBox").style.display = "flex";
            renderSidebar();
            renderQuestion();
        } catch (e) {
            console.error("generate error:", e);
            document.getElementById("loading").innerHTML = '<p style="color:red"> 生成题目失败: ' + e.message + '</p>';
        }
    });

    function renderSidebar() {
        const list = document.getElementById("sidebarList");
        list.innerHTML = "";
        questions.forEach((q, idx) => {
            const li = document.createElement("li");
            const hasAns = answers[idx] && answers[idx].trim().length > 0;
            const isActive = (idx === currentIndex) ? 'active' : '';
            const isCompleted = hasAns ? 'completed' : '';

            li.className = "question-item " + isActive + " " + isCompleted;
            li.innerHTML = '<div class="status-dot"></div> 第 ' + (idx + 1) + ' 题';

            li.onclick = () => {
                // 不需要在这里保存 answers，因为已经实时绑定了 inputs
                currentIndex = idx;
                renderQuestion();
                renderSidebar();
            };
            list.appendChild(li);
        });
    }

    function renderQuestion() {
        const q = questions[currentIndex];
        if (!q) return;

        // 初始化题目状态（解析内容）
        if (!questionStates[currentIndex]) {
            const parsed = parseQuestionContent(q.content);
            questionStates[currentIndex] = {
                parsed: parsed,
                subAnswers: new Array(parsed.subs.length).fill("")
            };
        }

        const state = questionStates[currentIndex];
        const { context, subs } = state.parsed;

        // 动态渲染 DOM
        const container = document.getElementById("dynamicContainer");
        container.innerHTML = "";

        // 题目类型标签
        document.getElementById("questionType").textContent = normalizeQuestionType(q.type);

        // 如果有上下文（考察点等），显示在顶部
        if (context) {
            const ctxDiv = document.createElement("div");
            ctxDiv.className = "q-context";
            ctxDiv.textContent = context;
            container.appendChild(ctxDiv);
        }

        // 渲染子问题和输入框
        subs.forEach((subQ, idx) => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "sub-q-item";

            const label = document.createElement("div");
            label.className = "sub-q-label";
            // 只有当有多个子问题时，才显示序号
            const showNum = subs.length > 1;
            label.textContent = showNum ? ("问题 " + (idx + 1) + ": " + subQ) : subQ;

            const textarea = document.createElement("textarea");
            textarea.className = "sub-answer-box";
            textarea.placeholder = showNum ? ("请输入问题 " + (idx + 1) + " 的回复...") : "请输入你的回答... (支持 Markdown 格式)";

            textarea.value = state.subAnswers[idx] || "";

            // 实时同步输入
            textarea.addEventListener("input", (e) => {
                 state.subAnswers[idx] = e.target.value;
                 syncAnswers(currentIndex);
            });

            itemDiv.appendChild(label);
            itemDiv.appendChild(textarea);
            container.appendChild(itemDiv);
        });

        // 更新顶部进度
        document.getElementById("progress").textContent = "进度：" + (currentIndex + 1) + " / " + questions.length;

        // 更新按钮状态
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        const submitBtn = document.getElementById("submitBtn");

        prevBtn.style.display = (currentIndex === 0) ? "none" : "inline-block";

        if (currentIndex === questions.length - 1) {
            nextBtn.style.display = "none";
            submitBtn.style.display = "inline-block";
        } else {
            nextBtn.style.display = "inline-block";
            submitBtn.style.display = "none";
        }

        renderSidebar();
    }

    // 将子答案合并回 answers 数组，保持兼容性
    function syncAnswers(idx) {
        const state = questionStates[idx];
        if (!state) return;

        if (state.parsed.subs.length === 1) {
            answers[idx] = state.subAnswers[0];
        } else {
             // 多个子问题，格式化拼接
             const parts = state.subAnswers.map((ans, i) => {
                 if (!ans || !ans.trim()) return "";
                 return "【回答 " + (i + 1) + "】\n" + ans;
             }).filter(s => s && s.length > 0);

             answers[idx] = parts.length > 0 ? parts.join("\n\n") : "";
        }
    }

    document.getElementById("prevBtn").addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex--;
            renderQuestion();
        }
    });

    document.getElementById("nextBtn").addEventListener("click", () => {
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            renderQuestion();
        }
    });

    document.getElementById("submitBtn").addEventListener("click", async () => {
        // 检查是否有题目未作答（检查合并后的 answers）
        // 可以根据需要改成检查是否每一题的每个子问都答了，或者只检查大题
        const hasEmpty = answers.some(a => !a || !a.trim());
        if (hasEmpty) {
             if (!confirm("还有题目未作答，确定提交吗？")) return;
        }

        const submitBtn = document.getElementById("submitBtn");
        submitBtn.disabled = true;
        submitBtn.textContent = "提交中...";

        try {
            const payloadAnswers = questions.map((q, i) => ({
                questionId: q.id,
                answer: answers[i] || ""
            }));

            const res = await fetch(base + "/api/interview/submit", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    sessionId: Number(sessionId),
                    answers: payloadAnswers
                })
            });

            const data = await parseJsonSafe(res);
            if (!res.ok) {
                throw new Error(data.error || ("提交失败，HTTP " + res.status));
            }

            alert("提交成功，正在评分...");
            window.location.href = base + "/result.jsp?sessionId=" + encodeURIComponent(sessionId);
        } catch (e) {
            console.error("submit error:", e);
            alert("提交失败: " + (e && e.message ? e.message : "未知错误"));
            submitBtn.disabled = false;
            submitBtn.textContent = "提交答案";
        }
    });
</script>
</body>
</html>
