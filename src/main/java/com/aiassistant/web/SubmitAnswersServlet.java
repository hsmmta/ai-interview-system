package com.aiassistant.web;

import com.aiassistant.client.FastApiClient;
import com.aiassistant.model.InterviewSession;
import com.aiassistant.service.InterviewService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * 鎻愪氦鎵€鏈夌瓟妗堬紝璋冪敤 AI 杩涜璇勫垎
 */
public class SubmitAnswersServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        JsonNode body = MAPPER.readTree(req.getInputStream());
        Long sessionId = body.path("sessionId").asLong(0);
        JsonNode answersNode = body.path("answers");

        if (sessionId == 0) {
            resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            MAPPER.writeValue(resp.getWriter(), Map.of("error", "缺少 sessionId"));
            return;
        }

        try {
            InterviewSession session = InterviewService.getSessionById(sessionId);
            if (session == null) {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                MAPPER.writeValue(resp.getWriter(), Map.of("error", "会话不存在"));
                return;
            }

            if (session.getQuestionsJson() == null || session.getQuestionsJson().isBlank()) {
                resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                MAPPER.writeValue(resp.getWriter(), Map.of("error", "题目不存在，无法评分"));
                return;
            }

            ArrayNode normalizedAnswers = normalizeAnswers(answersNode);
            String answersJson = MAPPER.writeValueAsString(normalizedAnswers);
            InterviewService.submitAnswers(sessionId, answersJson);

            JsonNode stored = MAPPER.readTree(session.getQuestionsJson());
            JsonNode questionsNode = stored.isArray() ? stored : stored.path("questions");
            JsonNode fastApiResp = FastApiClient.evaluateAnswers(sessionId, questionsNode, normalizedAnswers);

            String evaluationJson = MAPPER.writeValueAsString(fastApiResp);
            InterviewService.updateEvaluation(sessionId, evaluationJson);

            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "evaluation", fastApiResp
            ));

        } catch (Exception e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            MAPPER.writeValue(resp.getWriter(), Map.of("error", "评分失败: " + e.getMessage()));
        }
    }

    private ArrayNode normalizeAnswers(JsonNode answersNode) {
        ArrayNode result = MAPPER.createArrayNode();
        if (answersNode == null || answersNode.isNull()) {
            return result;
        }

        // 1) 前端常见格式：[{questionId:1, answer:"..."}, ...]
        if (answersNode.isArray()) {
            for (JsonNode n : answersNode) {
                if (n == null || n.isNull()) {
                    result.add("");
                    continue;
                }
                if (n.isObject()) {
                    // 优先取 answer 字段，其次 content/text，最后兜底为空
                    String ans = n.path("answer").asText("");
                    if (ans.isEmpty()) ans = n.path("content").asText("");
                    if (ans.isEmpty()) ans = n.path("text").asText("");
                    result.add(ans);
                } else {
                    // 兼容旧格式：["a1","a2",...]
                    result.add(n.asText(""));
                }
            }
            return result;
        }

        // 2) 旧对象格式：{"1":"...","2":"..."} 或 {"1":{"answer":"..."}}
        if (answersNode.isObject()) {
            int i = 1;
            while (true) {
                JsonNode item = answersNode.get(String.valueOf(i));
                if (item == null) {
                    break;
                }
                if (item.isObject()) {
                    String ans = item.path("answer").asText("");
                    if (ans.isEmpty()) ans = item.path("content").asText("");
                    if (ans.isEmpty()) ans = item.path("text").asText("");
                    result.add(ans);
                } else {
                    result.add(item.asText(""));
                }
                i++;
            }
            return result;
        }

        // 3) 纯文本兜底
        result.add(answersNode.asText(""));
        return result;
    }

}

