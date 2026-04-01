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
 * 根据用户选择的方向，调用 AI 生成面试题目
 */
public class GenerateQuestionsServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        JsonNode body = MAPPER.readTree(req.getInputStream());
        long sessionId = body.path("sessionId").asLong(0);

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

            JsonNode fastApiResp = FastApiClient.generateQuestions(
                    sessionId,
                    session.getInterviewType(),
                    session.getDirection(),
                    session.getQuestionCount() <= 0 ? 15 : session.getQuestionCount()
            );
            System.out.println("[GenerateQuestionsServlet] fastApiResp = " + fastApiResp.toString());
            ArrayNode questions = extractQuestionsArray(fastApiResp);
            if (questions == null) {
                throw new IOException("FastAPI 返回格式错误：未找到题目数组，返回内容=" + fastApiResp.toString());
            }

            // 建议保存成对象结构，方便后续 ResultServlet 按 .get(\"questions\") 读取
            String questionsJson = MAPPER.writeValueAsString(Map.of("questions", questions));
            InterviewService.updateQuestions(sessionId, questionsJson);



            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "questions", questions
            ));
        } catch (Exception e) {
            e.printStackTrace(); // 关键：把真实异常打印到 Tomcat 控制台
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "error", "生成题目失败: " + (e.getMessage() == null ? e.getClass().getName() : e.getMessage())
            ));
        }
    }

    private ArrayNode extractQuestionsArray(JsonNode root) {
        if (root == null || root.isNull()) {
            return null;
        }

        // 1) 直接 questions
        JsonNode q1 = root.path("questions");
        if (q1.isArray()) {
            return (ArrayNode) q1;
        }

        // 2) data.questions
        JsonNode data = root.path("data");
        JsonNode q2 = data.path("questions");
        if (q2.isArray()) {
            return (ArrayNode) q2;
        }

        // 3) data 本身就是数组
        if (data.isArray()) {
            return (ArrayNode) data;
        }

        // 4) result.questions
        JsonNode q3 = root.path("result").path("questions");
        if (q3.isArray()) {
            return (ArrayNode) q3;
        }

        return null;
    }
}
