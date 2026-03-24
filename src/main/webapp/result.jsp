<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>评估结果 - AI 模拟面试平台</title>
    <style>
        :root {
            --primary-color: #4A90E2;
            --success-color: #52c41a;
            --text-color: #333;
            --bg-color: #F4F7F6;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg-color);
            margin: 0;
            padding-bottom: 40px;
        }

        /* 顶部通栏 */
        .hero-banner {
            background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
            color: white;
            padding: 40px 20px 80px;
            text-align: center;
        }
        .hero-banner h2 { margin: 0; font-size: 28px; }
        .hero-banner p { opacity: 0.9; margin-top: 8px; }

        .container {
            max-width: 900px;
            margin: -60px auto 0;
            padding: 0 20px;
            position: relative;
            z-index: 10;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 20px;
            border-left: 4px solid var(--primary-color);
            padding-left: 12px;
            display: flex;
            align-items: center;
        }

        .markdown-body {
            line-height: 1.8;
            color: #444;
            font-size: 15px;
        }
        /* 美化标题，增加层次感 */
        .markdown-body h3, .markdown-body h2 {
            font-size: 18px;
            color: #2c3e50;
            background: #f8faff;
            padding: 10px 15px;
            border-left: 4px solid var(--primary-color);
            border-radius: 0 4px 4px 0;
            margin: 24px 0 16px 0;
            font-weight: 600;
        }
        /* 第一个标题去掉上边距 */
        .markdown-body > h3:first-child, .markdown-body > h2:first-child {
            margin-top: 0;
        }

        .markdown-body p { margin-bottom: 12px; }
        .markdown-body ul { padding-left: 20px; margin-bottom: 16px; color: #555; }
        .markdown-body li { margin-bottom: 8px; }
        .markdown-body strong { color: #2c3e50; font-weight: 700; background: rgba(74, 144, 226, 0.1); padding: 0 4px; border-radius: 4px; }

        .qa-card {
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s;
        }
        .qa-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .qa-header {
            background: #fafafa;
            padding: 16px 20px;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            color: #555;
            display: flex;
            justify-content: space-between;
        }
        .qa-body { padding: 20px; }
        .qa-label { font-size: 12px; color: #999; margin-bottom: 6px; display: block; }
        .qa-content { margin-bottom: 16px; color: #333; white-space: pre-wrap; }
        .qa-answer { background: #f9fbfd; padding: 12px; border-radius: 6px; border: 1px dashed #dbe9f6; color: #444; }
        .no-answer { color: #999; font-style: italic; }

        .btn-back {
            display: block;
            width: fit-content;
            margin: 0 auto;
            padding: 12px 32px;
            background: var(--primary-color);
            color: #fff;
            text-decoration: none;
            border-radius: 24px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
            transition: transform 0.2s;
        }
        .btn-back:hover { transform: translateY(-2px); }

        .loading, .error { padding: 40px; text-align: center; background: white; border-radius: 12px; margin-top: 40px; }
        .error { color: #c00; }

        /* 新增：子问题样式 (result.jsp 也需要) */
        .q-context { font-size: 15px; color: #555; background: #f4f8fb; padding: 12px; border-radius: 6px; border-left: 4px solid var(--primary-color); margin-bottom: 12px; white-space: pre-wrap; }
        .sub-q-item { margin-bottom: 20px; border-bottom: 1px dashed #eee; padding-bottom: 16px; }
        .sub-q-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .sub-q-label { font-size: 15px; font-weight: 600; color: #2c3e50; margin-bottom: 8px; }
        .sub-answer-box { background: #f9fbfd; padding: 12px; border-radius: 6px; border: 1px solid #dbe9f6; color: #444; white-space: pre-wrap; font-size: 14px; }
    </style>
</head>
<body>

<div class="hero-banner">
    <h2>🎯 面试能力评估报告</h2>
    <p>AI 助力，发现更好的自己</p>
</div>

<div class="container">
    <div id="loading" class="loading">正在生成分析报告，请稍候...</div>
    <div id="error" class="error" style="display:none;"></div>

    <div id="content" style="display:none;">
        <!-- 综合评价卡片 -->
        <div class="card">
            <div class="section-title">综合评价与建议</div>
            <div id="evaluationText" class="markdown-body"></div>
        </div>

        <!-- 详细回顾卡片 -->
        <div class="card">
            <div class="section-title">答题详情回顾</div>
            <div id="qaList"></div>
        </div>

        <a class="btn-back" href="<%=request.getContextPath()%>/config.jsp">开始新一轮模拟</a>
    </div>
</div>

<script>
    // ...existing code...
    // 适配新的 DOM 结构

    // 我们需要修改 populate 逻辑来使用 div 构造 qaList 而不是纯文本

    // Override loadResult part

    const base = "<%= request.getContextPath() %>";
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get("sessionId");

    async function loadResult() {
        const loadingEl = document.getElementById("loading");
        const errorEl = document.getElementById("error");
        const contentEl = document.getElementById("content");
        const qaListEl = document.getElementById("qaList"); // 确保获取这个元素

        if (!sessionId) {
            loadingEl.style.display = "none";
            errorEl.style.display = "block";
            errorEl.textContent = "缺少 sessionId 参数";
            return;
        }

        try {
            const res = await fetch(base + "/api/interview/result?sessionId=" + encodeURIComponent(sessionId), {
                method: "GET",
                headers: { "Accept": "application/json" }
            });

            const raw = await res.text();
            let data = {};
            try { data = raw ? JSON.parse(raw) : {}; } catch (e) { }

            if (!res.ok || !data.success) {
                throw new Error(data.error || "获取结果失败");
            }

            const evaluationText =
                data.evaluationText ||
                (data.evaluation && data.evaluation.realtime_evaluation) ||
                "该次面试暂无有效评价";

            const questions = Array.isArray(data.questions) ? data.questions : [];
            const answers = Array.isArray(data.answers) ? data.answers : [];

            // 使用自定义渲染函数处理 markdown
            document.getElementById("evaluationText").innerHTML = renderMarkdown(evaluationText);

            // 重新渲染 QA 列表为卡片
            qaListEl.innerHTML = "";
            questions.forEach((q, i) => {
                const qText = q.question || q.content || ("题目 " + (i + 1));

                // 使用解析函数拆分题目
                const parsedQ = parseQuestionContent(qText);
                const context = parsedQ.context;
                const subs = parsedQ.subs;

                let aText = "";
                if (i < answers.length) {
                    const a = answers[i];
                    if (a && typeof a === "object") { aText = a.answer || ""; }
                    else { aText = a || ""; }
                }
                aText = aText || ""; // 确保是字符串

                // 尝试解析组合答案：【回答 1】...
                let subAnswers = [];
                // 如果包含标准分隔符，则尝试分割
                if (aText.indexOf("【回答 ") !== -1) {
                    // 简单的按标识拆分
                    // 正则分割可能会丢失第一个元素前的空字符，手动简单处理
                    const partsCheck = aText.split(/【回答 \d+】[\r\n]*/);
                    // 通常 split 后第一个元素是空字符串（如果开头就是【回答 1】）
                    // 过滤掉空项
                    subAnswers = partsCheck.filter(function(s){ return s && s.trim().length > 0; });
                } else {
                    subAnswers = [aText.trim()];
                }

                // 构建 HTML 字符串
                var bodyContent = '';

                // 显示上下文（考察点）
                if (context) {
                    bodyContent += '<div class="q-context">' + context + '</div>';
                }

                // 逐个显示子问题和对应的回答
                subs.forEach(function(subQ, idx) {
                    // 尝试匹配答案：如果拆分出来的答案数量 >= 子问题数量，则一一对应；否则全显示在第一个或者做适配
                    // 简单策略：按顺序取，取不到就显示空
                    var myAns = "";
                    if (idx < subAnswers.length) {
                        myAns = subAnswers[idx];
                    } else if (idx === 0 && subAnswers.length === 1) {
                        myAns = subAnswers[0];
                    }

                    var showNum = subs.length > 1;
                    var label = showNum ? ("问题 " + (idx + 1)) : "题目内容";

                    bodyContent += '<div class="sub-q-item">';
                    if (showNum) {
                        bodyContent += '<div class="sub-q-label">' + label + '</div>';
                    }
                    bodyContent += '<div class="qa-content">' + subQ + '</div>';
                    bodyContent += '<div class="sub-q-label">你的作答</div>';
                    var ansClass = (!myAns || myAns.trim().length === 0) ? 'sub-answer-box no-answer' : 'sub-answer-box';
                    var ansText = (myAns && myAns.trim().length > 0) ? myAns : "（未作答）";
                    bodyContent += '<div class="' + ansClass + '">' + ansText + '</div>';
                    bodyContent += '</div>';
                });

                var card = document.createElement("div");
                card.className = "qa-card";
                card.innerHTML =
                    '<div class="qa-header">' +
                        '<span>第 ' + (i + 1) + ' 题</span>' +
                    '</div>' +
                    '<div class="qa-body">' + bodyContent + '</div>';

                qaListEl.appendChild(card);
            });

            loadingEl.style.display = "none";
            contentEl.style.display = "block";
        } catch (err) {
            console.error(err);
            loadingEl.style.display = "none";
            errorEl.style.display = "block";
            errorEl.textContent = "加载失败: " + err.message;
        }
    }

    /**
     * 简单的 Markdown 解析函数，优化展示效果
     */
    function renderMarkdown(text) {
        if (!text) return '<div class="no-answer">暂无评价内容</div>';

        // 基础转义
        let safeText = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        let lines = safeText.split(/\r?\n/);
        let html = '';
        let inList = false;

        lines.forEach(line => {
            let trimmed = line.trim();

            // 空行处理
            if (!trimmed) {
                if (inList) { html += '</ul>'; inList = false; }
                return;
            }

            // 标题处理：兼容 Markdown 标准标题 (#) 和 加粗独占一行 (**标题**)
            let headerRegex = new RegExp("^" + "#" + "{1,3}\\s+");
            if (headerRegex.test(trimmed)) {
                if (inList) { html += '</ul>'; inList = false; }
                let content = trimmed.replace(headerRegex, '');
                html += '<h3>' + parseInline(content) + '</h3>';
                return;
            }

            // 特殊处理：被 ** 包裹的短句视为小标题（如：**逐题点评**）
            if (/^\*\*.+?\*\*[：:]?$/.test(trimmed) && trimmed.length < 50) {
                 if (inList) { html += '</ul>'; inList = false; }
                 let content = trimmed.replace(/^\*\*/, '').replace(/\*\*[：:]?$/, '');
                 html += '<h3>' + content + '</h3>';
                 return;
            }

            // 列表处理
            if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                if (!inList) { html += '<ul>'; inList = true; }
                html += '<li>' + parseInline(trimmed.substring(2)) + '</li>';
                return;
            }

            // 数字列表简单处理为段落（带粗体头）
            if (/^\d+\.\s/.test(trimmed)) {
                 if (inList) { html += '</ul>'; inList = false; }
                 // 1. 逐题点评 -> 1. 逐题点评
                 html += '<p class="list-num">' + parseInline(trimmed) + '</p>';
                 return;
            }

            // 普通段落
            if (inList) { html += '</ul>'; inList = false; }
            html += '<p>' + parseInline(trimmed) + '</p>';
        });

        if (inList) { html += '</ul>'; }

        return html;
    }

    function parseInline(str) {
        // 解析 **加粗**
        return str.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }

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

    loadResult();
</script>
</body>
</html>

