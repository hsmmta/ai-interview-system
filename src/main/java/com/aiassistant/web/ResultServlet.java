package com.aiassistant.web;

import com.aiassistant.model.InterviewSession;
import com.aiassistant.service.InterviewService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class ResultServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        String sessionIdStr = req.getParameter("sessionId");
        if (sessionIdStr == null || sessionIdStr.isBlank()) {
            resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            ObjectNode err = MAPPER.createObjectNode();
            err.put("error", "缺少 sessionId");
            MAPPER.writeValue(resp.getWriter(), err);
            return;
        }

        try {
            Long sessionId = Long.parseLong(sessionIdStr);
            InterviewSession session = InterviewService.getSessionById(sessionId);

            if (session == null) {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                ObjectNode err = MAPPER.createObjectNode();
                err.put("error", "会话不存在");
                MAPPER.writeValue(resp.getWriter(), err);
                return;
            }

            JsonNode questionsNode = normalizeQuestions(session.getQuestionsJson());
            JsonNode answersNode = safeReadJsonOrArray(session.getAnswersJson());
            JsonNode evaluationRaw = safeReadJsonOrObject(session.getEvaluationJson());
            String evaluationText = extractEvaluationText(evaluationRaw);

            ObjectNode out = MAPPER.createObjectNode();
            out.put("success", true);
            out.set("questions", questionsNode == null ? MAPPER.createArrayNode() : questionsNode);
            out.set("answers", answersNode == null ? MAPPER.createArrayNode() : answersNode);
            out.set("evaluation", evaluationRaw == null ? MAPPER.createObjectNode() : evaluationRaw);
            out.put("evaluationText", evaluationText == null ? "" : evaluationText);

            MAPPER.writeValue(resp.getWriter(), out);
        } catch (Exception e) {
            e.printStackTrace();
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            ObjectNode err = MAPPER.createObjectNode();
            err.put("error", "加载结果失败: " + (e.getMessage() == null ? e.getClass().getName() : e.getMessage()));
            MAPPER.writeValue(resp.getWriter(), err);
        }
    }

    private String extractEvaluationText(JsonNode node) {
        if (node == null || node.isNull()) return "";

        String t1 = node.path("realtime_evaluation").asText("");
        if (!t1.isBlank()) return t1;

        String t2 = node.path("data").path("realtime_evaluation").asText("");
        if (!t2.isBlank()) return t2;

        if (node.isTextual()) return node.asText("");

        return node.toString();
    }

    private JsonNode normalizeQuestions(String raw) throws IOException {
        if (raw == null || raw.isBlank()) {
            return MAPPER.createArrayNode();
        }
        JsonNode root = MAPPER.readTree(raw);
        if (root.isArray()) return root;
        JsonNode q = root.path("questions");
        if (q.isArray()) return q;
        return MAPPER.createArrayNode();
    }

    private JsonNode safeReadJsonOrArray(String raw) throws IOException {
        if (raw == null || raw.isBlank()) {
            return MAPPER.createArrayNode();
        }
        try {
            return MAPPER.readTree(raw);
        } catch (Exception ignore) {
            ArrayNode arr = MAPPER.createArrayNode();
            arr.add(raw);
            return arr;
        }
    }

    private JsonNode safeReadJsonOrObject(String raw) throws IOException {
        if (raw == null || raw.isBlank()) {
            return MAPPER.createObjectNode();
        }
        try {
            return MAPPER.readTree(raw);
        } catch (Exception ignore) {
            ObjectNode obj = MAPPER.createObjectNode();
            obj.put("realtime_evaluation", raw);
            return obj;
        }
    }
}
