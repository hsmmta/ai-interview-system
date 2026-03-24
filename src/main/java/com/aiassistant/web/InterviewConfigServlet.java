package com.aiassistant.web;

import com.aiassistant.model.InterviewSession;
import com.aiassistant.service.InterviewService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * 面试配置：用户选择招聘类型、方向、题目数量
 */
public class InterviewConfigServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        HttpSession session = req.getSession(false);
        if (session == null || session.getAttribute("userId") == null) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            MAPPER.writeValue(resp.getWriter(), Map.of("error", "请先登录"));
            return;
        }

        Long userId = (Long) session.getAttribute("userId");
        JsonNode body = MAPPER.readTree(req.getInputStream());

        String interviewType = body.path("interviewType").asText("");
        String direction = body.path("direction").asText("");
        int questionCount = body.path("questionCount").asInt(15);

        if (interviewType.isBlank() || direction.isBlank()) {
            resp.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            MAPPER.writeValue(resp.getWriter(), Map.of("error", "参数不完整"));
            return;
        }

        try {
            InterviewSession interviewSession = InterviewService.createSession(userId, interviewType, direction, questionCount);
            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "sessionId", interviewSession.getId()
            ));
        } catch (Exception e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            MAPPER.writeValue(resp.getWriter(), Map.of("error", e.getMessage()));
        }
    }
}

