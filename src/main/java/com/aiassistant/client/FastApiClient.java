package com.aiassistant.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Java <-> Python FastAPI 客户端
 * 当前对接 mock_interview 服务：
 *   base: http://127.0.0.1:8010
 *   generate: /api/interview/generate
 *   evaluate: /api/interview/interactive/evaluate
 */
public class FastApiClient {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final String BASE_URL = "http://127.0.0.1:8010";

    public static JsonNode generateQuestions(long sessionId, String interviewType, String direction, int questionCount) throws IOException {
        String url = BASE_URL + "/api/interview/generate";

        ObjectNode req = MAPPER.createObjectNode();
        req.put("name", "候选人");
        req.put("position", direction == null ? "Java后端" : direction);
        req.put("experience", interviewType == null ? "校招" : interviewType);
        req.put("skills", "Java,Spring Boot,MySQL");

        JsonNode resp = postJson(url, req);

        // mock_interview 返回 data.interview_questions(大文本)，转成标准数组给前端
        String interviewQuestionsText = resp.path("data").path("interview_questions").asText("");
        ArrayNode questions = parseQuestionsTextToArray(interviewQuestionsText, questionCount);

        ObjectNode out = MAPPER.createObjectNode();
        out.put("session_id", String.valueOf(sessionId));
        out.set("questions", questions);
        return out;
    }

    public static JsonNode evaluateAnswers(long sessionId, JsonNode questions, JsonNode answers) throws IOException {
        String url = BASE_URL + "/api/interview/interactive/evaluate";

        ObjectNode req = MAPPER.createObjectNode();
        req.put("user_info", "sessionId=" + sessionId);

        ObjectNode userAnswers = MAPPER.createObjectNode();
        int qSize = (questions != null && questions.isArray()) ? questions.size() : 0;
        int aSize = (answers != null && answers.isArray()) ? answers.size() : 0;
        int size = Math.max(qSize, aSize);

        for (int i = 0; i < size; i++) {
            String qText = "";
            if (i < qSize) {
                JsonNode q = questions.get(i);
                qText = q.path("question").asText(q.path("content").asText(""));
            }

            String aText = "";
            if (i < aSize) {
                JsonNode a = answers.get(i);
                if (a.isObject()) {
                    aText = a.path("answer").asText("");
                } else {
                    aText = a.asText("");
                }
            }

            ObjectNode item = MAPPER.createObjectNode();
            item.put("question", qText);
            item.put("answer", aText);
            userAnswers.set("第" + (i + 1) + "题", item);
        }

        req.set("user_answers", userAnswers);

        try {
            JsonNode resp = postJson(url, req);
            ObjectNode out = MAPPER.createObjectNode();
            out.put("status", "success");
            out.put("realtime_evaluation", resp.path("data").path("realtime_evaluation").asText(""));
            return out;
        } catch (Exception ex) {
            // 不抛 500，返回可展示兜底评价，避免前端“网络错误”
            ObjectNode out = MAPPER.createObjectNode();
            out.put("status", "fallback");
            out.put("realtime_evaluation",
                    "评分服务暂时不可用，已保存你的答案。\n" +
                            "错误信息：" + ex.getMessage() + "\n" +
                            "建议：稍后在结果页重试评分。");
            return out;
        }
    }


    private static JsonNode postJson(String urlStr, JsonNode body) throws IOException {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setConnectTimeout(20000);
        conn.setReadTimeout(300000);
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setRequestProperty("Accept", "application/json");

        byte[] payload = MAPPER.writeValueAsBytes(body);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(payload);
        }

        int code = conn.getResponseCode();
        InputStream is = (code >= 200 && code < 300) ? conn.getInputStream() : conn.getErrorStream();
        String respText = readAll(is);

        if (code < 200 || code >= 300) {
            throw new IOException("FastAPI request failed: HTTP " + code + " body=" + respText);
        }

        return MAPPER.readTree(respText);
    }

    private static String readAll(InputStream is) throws IOException {
        if (is == null) return "";
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) sb.append(line);
        }
        return sb.toString();
    }

    // 将大文本题目按“【问题X】”切成数组
    private static ArrayNode parseQuestionsTextToArray(String text, int questionCount) {
        ArrayNode arr = MAPPER.createArrayNode();

        if (text != null && !text.isBlank()) {
            String[] blocks = text.split("【问题\\d+】");
            int id = 1;
            for (String b : blocks) {
                String t = b == null ? "" : b.trim();
                if (t.isEmpty()) continue;

                // 直接保留整题文本（含题干/追问/考察点），避免只显示考察点
                String fullText = normalizeQuestionBlock(t);
                if (fullText.isEmpty()) continue;

                ObjectNode q = MAPPER.createObjectNode();
                q.put("id", id);
                q.put("type", id <= 10 ? "short_answer" : "coding");
                q.put("question", fullText);
                arr.add(q);
                id++;
            }
        }

        int target = questionCount > 0 ? questionCount : 15;
        while (arr.size() < target) {
            int id = arr.size() + 1;
            ObjectNode q = MAPPER.createObjectNode();
            q.put("id", id);
            q.put("type", id <= 10 ? "short_answer" : "coding");
            q.put("question", "本题内容解析失败，请联系管理员（占位题 " + id + "）");
            arr.add(q);
        }

        return arr;
    }

    /**
     * 从单题文本块中提取真正的题干，避免只拿到“考察点”或“追问”
     */
    private static String normalizeQuestionBlock(String block) {
        if (block == null) return "";
        // 保留换行，去掉首尾空白
        String s = block.replace("\r\n", "\n").replace("\r", "\n").trim();
        if (s.isEmpty()) return "";
        return s;
    }
}
