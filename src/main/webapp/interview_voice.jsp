<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>语音面试中 - AI 模拟面试平台</title>
    <style>
        :root {
            --primary-color: #4A90E2;
            --bg-color: #F8F9FA;
            --header-height: 60px;
            --sidebar-width: 280px;
            --recording-color: #ff4d4f;
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

        /* 语音特有样式 */
        .voice-controls {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            background: #f9f9f9;
            padding: 10px;
            border-radius: 8px;
        }
        .voice-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 20px;
        }
        .btn-record {
            background: white;
            border: 2px solid var(--recording-color);
            color: var(--recording-color);
        }
        .btn-record:hover { background: #fff1f0; }
        .btn-record.recording {
            background: var(--recording-color);
            color: white;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 77, 79, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0); }
        }
        .voice-status { font-size: 14px; color: #666; flex: 1; }
        .waveform { height: 30px; width: 100px; display: none; align-items: center; gap: 3px; }
        .bar { background: var(--recording-color); width: 3px; border-radius: 2px; animation: dance 0.5s infinite ease-in-out; }
        .bar:nth-child(1) { animation-delay: 0.1s; height: 10px; }
        .bar:nth-child(2) { animation-delay: 0.2s; height: 20px; }
        .bar:nth-child(3) { animation-delay: 0.3s; height: 15px; }
        .bar:nth-child(4) { animation-delay: 0.4s; height: 25px; }
        .bar:nth-child(5) { animation-delay: 0.5s; height: 12px; }
        @keyframes dance {
            0%, 100% { transform: scaleY(1); }
            50% { transform: scaleY(1.5); }
        }

        .transcribed-text {
            width: 100%;
            min-height: 100px;
            padding: 16px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            line-height: 1.6;
            resize: vertical;
            transition: all 0.2s;
            font-family: inherit;
            background: #fff;
        }
        .transcribed-text:focus {
            border-color: var(--primary-color);
            outline: none;
        }

    </style>
</head>
<body>
<div class="header">
    <div class="brand">🎙️ <span>AI 语音面试</span></div>
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
            <p>Listen... 正在配置语音面试环境...</p>
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

<script>
    const base = "<%= request.getContextPath() %>";
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("sessionId");
    const configuredQuestionCount = Number(urlParams.get("questionCount") || 0);

    let questions = [];
    let answers = [];
    let questionStates = [];
    let currentIndex = 0;
    let displayTotalCount = configuredQuestionCount > 0 ? configuredQuestionCount : 0;

    // WAV Recording Globals
    let audioContext = null;
    let audioSource = null;
    let audioProcessor = null;
    let audioLeftChannel = [];
    let audioRecordingLength = 0;
    let audioSampleRate = 44100;

    let isRecording = false;
    let activeSubQuestionIndex = -1; // 当前正在录音的子问题索引

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

    function parseQuestionContent(content) {
        if (!content) return { context: "", subs: [] };
        if (!content.includes("\n") || !/-\s/.test(content)) {
             return { context: "", subs: [content] };
        }
        const lines = content.split('\n');
        let contextLines = [];
        let subs = [];
        let foundFirstBullet = false;
        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith("-")) {
                foundFirstBullet = true;
                let clean = trimmed.replace(/^-\s*(追问\d*[：:]?)?\s*/, '');
                subs.push(clean);
            } else {
                if (!foundFirstBullet) {
                    contextLines.push(line);
                } else {
                    if (subs.length > 0) subs[subs.length - 1] += "\n" + line;
                    else contextLines.push(line);
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
            alert("缺少 sessionId");
            return;
        }
        try {
            // 请求权限
            await navigator.mediaDevices.getUserMedia({ audio: true });

            const res = await fetch(base + "/api/interview/generate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({sessionId: Number(sessionId)})
            });
            const data = await parseJsonSafe(res);
            if (!res.ok) throw new Error(data.error || ("题目生成失败，HTTP " + res.status));

            const rawQuestions = data.questions || (data.data && data.data.questions) || [];
            questions = normalizeQuestions(rawQuestions);

            if (questions.length === 0) throw new Error("题目生成成功，但题目列表为空");

            answers = new Array(questions.length).fill("");
            questionStates = new Array(questions.length).fill(null);

            document.getElementById("loading").style.display = "none";
            document.getElementById("questionBox").style.display = "flex";
            renderSidebar();
            renderQuestion();
        } catch (e) {
            console.error("error:", e);
            document.getElementById("loading").innerHTML = '<p style="color:red">😢 错误: ' + e.message + '<br>请确保允许麦克风权限</p>';
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
            li.onclick = () => { currentIndex = idx; renderQuestion(); renderSidebar(); };
            list.appendChild(li);
        });
    }

    function renderQuestion() {
        const q = questions[currentIndex];
        if (!q) return;

        if (!questionStates[currentIndex]) {
            const parsed = parseQuestionContent(q.content);
            questionStates[currentIndex] = {
                parsed: parsed,
                subAnswers: new Array(parsed.subs.length).fill("")
            };
        }

        const state = questionStates[currentIndex];
        const { context, subs } = state.parsed;
        const container = document.getElementById("dynamicContainer");
        container.innerHTML = "";

        document.getElementById("questionType").textContent = normalizeQuestionType(q.type);

        if (context) {
            const ctxDiv = document.createElement("div");
            ctxDiv.className = "q-context";
            ctxDiv.textContent = context;
            container.appendChild(ctxDiv);
        }

        subs.forEach((subQ, idx) => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "sub-q-item";

            const label = document.createElement("div");
            label.className = "sub-q-label";
            label.textContent = (subs.length > 1 ? ("问题 " + (idx + 1) + ": ") : "") + subQ;

            // 语音控制区
            const voiceControls = document.createElement("div");
            voiceControls.className = "voice-controls";

            const recordBtn = document.createElement("button");
            recordBtn.className = "voice-btn btn-record";
            recordBtn.innerHTML = "🎙️";
            recordBtn.title = "点击开始录音 / 结束录音";

            const statusText = document.createElement("span");
            statusText.className = "voice-status";
            statusText.textContent = "点击麦克风开始说话...";

             const waveform = document.createElement("div");
            waveform.className = "waveform";
            for(let i=0; i<5; i++) {
                const bar = document.createElement("div");
                bar.className = "bar";
                waveform.appendChild(bar);
            }

            // 文本区域（可编辑识别结果）
            const textarea = document.createElement("textarea");
            textarea.className = "transcribed-text";
            textarea.placeholder = "语音识别结果将显示在这里，您也可以手动编辑...";
            textarea.value = state.subAnswers[idx] || "";

            textarea.addEventListener("input", (e) => {
                 state.subAnswers[idx] = e.target.value;
                 syncAnswers(currentIndex);
            });

            // 录音逻辑
            recordBtn.addEventListener("click", () => {
                toggleRecording(idx, recordBtn, statusText, waveform, textarea);
            });

            voiceControls.appendChild(recordBtn);
            voiceControls.appendChild(statusText);
            voiceControls.appendChild(waveform);

            itemDiv.appendChild(label);
            itemDiv.appendChild(voiceControls);
            itemDiv.appendChild(textarea);
            container.appendChild(itemDiv);
        });

        document.getElementById("progress").textContent = "进度：" + (currentIndex + 1) + " / " + questions.length;

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

    function syncAnswers(idx) {
        const state = questionStates[idx];
        if (!state) return;
        if (state.parsed.subs.length === 1) {
            answers[idx] = state.subAnswers[0];
        } else {
             const parts = state.subAnswers.map((ans, i) => {
                 if (!ans || !ans.trim()) return "";
                 return "【回答 " + (i + 1) + "】\n" + ans;
             }).filter(s => s && s.length > 0);
             answers[idx] = parts.length > 0 ? parts.join("\n\n") : "";
        }
    }

    // WAV 编码辅助工具
    function mergeBuffers(channelBuffer, recordingLength) {
        const result = new Float32Array(recordingLength);
        let offset = 0;
        for (let i = 0; i < channelBuffer.length; i++) {
            const buffer = channelBuffer[i];
            result.set(buffer, offset);
            offset += buffer.length;
        }
        return result;
    }

    function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    function floatTo16BitPCM(output, offset, input) {
        for (let i = 0; i < input.length; i++, offset += 2) {
            let s = Math.max(-1, Math.min(1, input[i]));
            output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
    }

    function encodeWAV(samples, sampleRate) {
        const buffer = new ArrayBuffer(44 + samples.length * 2);
        const view = new DataView(buffer);

        /* RIFF identifier */
        writeString(view, 0, 'RIFF');
        /* RIFF chunk length */
        view.setUint32(4, 36 + samples.length * 2, true);
        /* RIFF type */
        writeString(view, 8, 'WAVE');
        /* format chunk identifier */
        writeString(view, 12, 'fmt ');
        /* format chunk length */
        view.setUint32(16, 16, true);
        /* sample format (raw) */
        view.setUint16(20, 1, true);
        /* channel count */
        view.setUint16(22, 1, true);
        /* sample rate */
        view.setUint32(24, sampleRate, true);
        /* byte rate (sample rate * block align) */
        view.setUint32(28, sampleRate * 2, true);
        /* block align (channel count * bytes per sample) */
        view.setUint16(32, 2, true);
        /* bits per sample */
        view.setUint16(34, 16, true);
        /* data chunk identifier */
        writeString(view, 36, 'data');
        /* data chunk length */
        view.setUint32(40, samples.length * 2, true);

        floatTo16BitPCM(view, 44, samples);

        return new Blob([view], { type: 'audio/wav' });
    }

    async function toggleRecording(subIdx, btn, status, wave, textarea) {
        if (isRecording) {
            // STOP RECORDING
            if (activeSubQuestionIndex !== subIdx) return;

            // 停止音频处理
            if (audioSource && audioProcessor) {
                audioSource.disconnect();
                audioProcessor.disconnect();
                audioProcessor.onaudioprocess = null;
            }

            // 编码为 WAV
            const pcmBuffer = mergeBuffers(audioLeftChannel, audioRecordingLength);
            const audioBlob = encodeWAV(pcmBuffer, audioSampleRate);

            // 清理
            audioLeftChannel = [];
            audioRecordingLength = 0;

            btn.classList.remove("recording");
            wave.style.display = "none";
            status.textContent = "正在转写(WAV)...";
            isRecording = false;

            if (audioBlob.size === 0) {
                status.textContent = "录音数据为空，请重试";
                return;
            }
            console.log("录音完成，大小:", audioBlob.size, "类型: audio/wav");

            // 上传
            try {
                const formData = new FormData();
                const fileName = "recording_" + Date.now() + ".wav";
                formData.append("audio_file", audioBlob, fileName);

                const res = await fetch("http://127.0.0.1:8020/api/analyze-interview", {
                    method: "POST",
                    body: formData
                });

                if (!res.ok) {
                    throw new Error("语音服务响应异常 HTTP " + res.status);
                }

                const result = await res.json();
                console.log("语音识别API响应:", result);

                // 优先处理标准结构 { code: 200, data: { ... } }
                if (result.code === 200) {
                    if (result.data && result.data.candidate_text) {
                        const newText = result.data.candidate_text;
                        const emotion = result.data.emotion;

                        const currentVal = textarea.value;
                        textarea.value = currentVal ? (currentVal + " " + newText) : newText;
                        textarea.dispatchEvent(new Event('input'));

                        status.textContent = "识别成功";
                        if (emotion && emotion !== 'NEUTRAL') {
                            status.textContent += " [情绪: " + emotion + "]";
                        }
                    } else {
                        console.warn("识别成功但无内容:", result);
                        status.textContent = "未检测到有效语音内容";
                    }
                }
                // 处理明确的后端错误 { code: 500, msg: "..." }
                else if (result.code === 500) {
                        let errorMsg = result.msg || result.message || result.detail;
                        if (!errorMsg) errorMsg = "后端处理失败 (500)";

                        // 友好提示
                        status.innerHTML = `<span style="color: var(--recording-color);">❌ ${errorMsg}</span>`;
                        console.error("Backend Error:", errorMsg);
                }
                // 兼容直接返回数据的格式 { candidate_text: "..." }
                else if (result.candidate_text) {
                        const newText = result.candidate_text;
                        const currentVal = textarea.value;
                        textarea.value = currentVal ? (currentVal + " " + newText) : newText;
                        textarea.dispatchEvent(new Event('input'));
                        status.textContent = "识别成功";
                }
                // 其他情况
                else {
                        const msg = result.msg || result.message || "未知响应格式";
                        status.innerHTML = `<span style="color: red;">识别异常: ${msg}</span>`;
                }

            } catch (err) {
                console.error("语音识别错误:", err);
                status.innerHTML = `<span style="color: red;">请求失败: ${err.message}</span>`;
            }

        } else {
            // START RECORDING
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioSampleRate = audioContext.sampleRate;
                audioSource = audioContext.createMediaStreamSource(stream);

                // 使用 ScriptProcessor 录制原始 PCM (bufferSize, inputChannels, outputChannels)
                audioProcessor = audioContext.createScriptProcessor(2048, 1, 1);

                audioLeftChannel = [];
                audioRecordingLength = 0;

                audioProcessor.onaudioprocess = function(e) {
                    if (!isRecording) return;
                    const left = e.inputBuffer.getChannelData(0);
                    // 克隆数据
                    audioLeftChannel.push(new Float32Array(left));
                    audioRecordingLength += left.length;
                };

                audioSource.connect(audioProcessor);
                // 需要连接到 destination 否则 Chrome 不会触发 onaudioprocess
                audioProcessor.connect(audioContext.destination);

                isRecording = true;
                activeSubQuestionIndex = subIdx;

                btn.classList.add("recording");
                wave.style.display = "flex";
                status.textContent = "正在录音 (WAV)...";

            } catch (err) {
                console.error("Error accessing microphone:", err);
                status.textContent = "麦克风访问失败: " + err.message;
            }
        }
    }

    document.getElementById("prevBtn").addEventListener("click", () => {
        if(currentIndex > 0) { currentIndex--; renderQuestion(); }
    });
    document.getElementById("nextBtn").addEventListener("click", () => {
        if(currentIndex < questions.length - 1) { currentIndex++; renderQuestion(); }
    });
    document.getElementById("submitBtn").addEventListener("click", async () => {
        const hasEmpty = answers.some(a => !a || !a.trim());
        if (hasEmpty && !confirm("还有题目未作答，确定提交吗？")) return;

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
            if (!res.ok) throw new Error("提交失败");
            alert("提交成功！");
            window.location.href = base + "/result.jsp?sessionId=" + encodeURIComponent(sessionId);
        } catch (e) {
            console.error(e);
            alert("提交失败: " + e.message);
            submitBtn.disabled = false;
        }
    });
</script>
</body>
</html>
