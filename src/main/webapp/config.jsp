<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>面试配置 - AI 模拟面试平台</title>
    <style>
        :root {
            --primary-color: #4A90E2;
            --primary-hover: #357ABD;
            --bg-color: #F4F7F6;
            --text-color: #333;
            --card-radius: 12px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg-color);
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: var(--card-radius);
            padding: 48px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }
        h1 { text-align: center; margin-bottom: 40px; color: var(--text-color); font-weight: 700; }

        .form-group { margin-bottom: 32px; }
        label.section-title {
            display: block;
            margin-bottom: 16px;
            color: #333;
            font-size: 16px;
            font-weight: 600;
        }

        /* 优化后的单选卡片样式 */
        .radio-group { display: flex; gap: 16px; }
        .radio-card {
            flex: 1;
            position: relative;
        }
        .radio-card input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            height: 0;
            width: 0;
        }
        .radio-card .card-content {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            border: 2px solid #eee;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
            color: #555;
        }
        .radio-card input:checked ~ .card-content {
            border-color: var(--primary-color);
            background-color: #f0f7ff;
            color: var(--primary-color);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
        }
        .radio-card:hover .card-content {
            border-color: #ccc;
        }

        /* 优化后的下拉框 */
        select {
            width: 100%;
            padding: 14px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            background: white;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23333%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
            background-repeat: no-repeat;
            background-position: right 14px top 50%;
            background-size: 12px auto;
            cursor: pointer;
            transition: all 0.3s;
        }
        select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
        }

        /* 优化后的输入框 */
        input[type="number"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.3s;
        }
        input[type="number"]:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
        }

        button.btn-primary {
            width: 100%;
            padding: 16px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 20px;
        }
        button.btn-primary:hover {
            background: var(--primary-hover);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
            transform: translateY(-1px);
        }
        button.btn-primary:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .message { text-align: center; margin-top: 20px; color: #d9534f; font-size: 14px; }
    </style>
</head>
<body>
<div class="container">
    <h1>配置面试信息</h1>

    <div class="form-group">
        <label class="section-title">招聘类型</label>
        <div class="radio-group">
            <label class="radio-card">
                <input type="radio" name="type" value="校招" checked>
                <div class="card-content">🎓 校园招聘</div>
            </label>
            <label class="radio-card">
                <input type="radio" name="type" value="社招">
                <div class="card-content">💼 社会招聘</div>
            </label>
        </div>
    </div>

    <div class="form-group">
        <label class="section-title">技术方向（根据您的个人信息自动设置）</label>
        <select id="direction" disabled style="background-color: #f9f9f9; cursor: not-allowed;">
            <option value="ai算法工程师">ai算法工程师</option>
            <option value="ai数据开发工程师">ai数据开发工程师</option>
        </select>
        <div style="margin-top: 8px; font-size: 13px; color: #666;">如需修改方向，请前往 <a href="profile.jsp" style="color: var(--primary-color);">个人中心</a> 更新意向岗位。</div>
    </div>

    <div class="form-group">
        <label class="section-title">题目数量</label>
        <input type="number" id="questionCount" value="6" min="5" max="30" />
    </div>

    <div class="form-group">
        <label class="section-title">答题方式</label>
        <div class="radio-group">
            <label class="radio-card">
                <input type="radio" name="mode" value="text" checked>
                <div class="card-content">⌨️ 文本回答</div>
            </label>
            <label class="radio-card">
                <input type="radio" name="mode" value="voice">
                <div class="card-content">🎙️ 语音回答</div>
            </label>
        </div>
    </div>

    <button id="startBtn" class="btn-primary">✨ 生成专属面试题</button>
    <div id="message" class="message"></div>
</div>

<script>
    const startBtn = document.getElementById("startBtn");
    const message = document.getElementById("message");
    const directionSelect = document.getElementById("direction");

    // Load user profile to set direction
    (async function loadUserProfile() {
        try {
            const res = await fetch("<%= request.getContextPath() %>/api/profile");
            if (res.ok) {
                const data = await res.json();
                if (data.success && data.user && data.user.targetPosition) {
                    // Normalize position string just in case, though it should match registration options
                    const userPos = data.user.targetPosition;
                    // Check if userPos is one of our options, if not add it dynamically or pick closest
                    let optionExists = false;
                    for (let i = 0; i < directionSelect.options.length; i++) {
                        if (directionSelect.options[i].value === userPos) {
                            directionSelect.selectedIndex = i;
                            optionExists = true;
                            break;
                        }
                    }
                    if (!optionExists) {
                        const opt = document.createElement('option');
                        opt.value = userPos;
                        opt.innerHTML = userPos;
                        directionSelect.appendChild(opt);
                        directionSelect.value = userPos;
                    }
                }
            }
        } catch (e) {
            console.error("Failed to load profile for config", e);
        }
    })();

    startBtn.addEventListener("click", async () => {
        const interviewType = document.querySelector('input[name="type"]:checked').value;
        const direction = document.getElementById("direction").value;
        const questionCount = parseInt(document.getElementById("questionCount").value);
        const mode = document.querySelector('input[name="mode"]:checked').value;

        startBtn.disabled = true;
        startBtn.textContent = "配置中...";

        try {
            const res = await fetch("<%= request.getContextPath() %>/api/interview/config", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({interviewType, direction, questionCount})
            });

            const data = await res.json();
            if (res.ok) {
                // 创建会话成功，跳转到生成题目
                if (mode === "voice") {
                    window.location.href = "<%= request.getContextPath() %>/interview_voice.jsp?sessionId=" + data.sessionId;
                } else {
                    window.location.href = "<%= request.getContextPath() %>/interview.jsp?sessionId=" + data.sessionId;
                }
            } else {
                message.textContent = data.error || "配置失败";
                startBtn.disabled = false;
                startBtn.textContent = "开始面试";
            }
        } catch (e) {
            message.textContent = "网络错误";
            startBtn.disabled = false;
            startBtn.textContent = "开始面试";
        }
    });
</script>
</body>
</html>

