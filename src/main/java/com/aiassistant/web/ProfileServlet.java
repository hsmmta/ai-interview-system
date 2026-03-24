package com.aiassistant.web;

import com.aiassistant.model.User;
import com.aiassistant.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class ProfileServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    protected void doDelete(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        handleRequest(req, resp, false, true);
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        handleRequest(req, resp, false, false);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        handleRequest(req, resp, true, false);
    }

    private void handleRequest(HttpServletRequest req, HttpServletResponse resp, boolean isPost, boolean isDelete) throws IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        HttpSession session = req.getSession(false);
        Long userId = (session != null) ? (Long) session.getAttribute("userId") : null;
        String phoneSession = (session != null) ? (String) session.getAttribute("phone") : null;

        if (userId == null && phoneSession == null) {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            MAPPER.writeValue(resp.getWriter(), Map.of("success", false, "message", "未登录"));
            return;
        }

        try {
            User user = null;
            if (phoneSession != null) {
                user = UserService.findByPhone(phoneSession);
            }
            if (user == null) {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
                MAPPER.writeValue(resp.getWriter(), Map.of("success", false, "message", "用户不存在"));
                return;
            }

            if (isDelete) {
                UserService.deleteUser(user.getId());
                if (session != null) session.invalidate();
                MAPPER.writeValue(resp.getWriter(), Map.of("success", true, "message", "账号已注销"));
                return;
            }

            if (isPost) {
                // Update profile
                try {
                    String name = req.getParameter("name");
                    String email = req.getParameter("email");
                    String targetPosition = req.getParameter("targetPosition");
                    String action = req.getParameter("action"); // Check for "delete" action in POST

                    // Also support JSON body if params are null
                    if (name == null && req.getContentType() != null && req.getContentType().contains("json")) {
                         com.fasterxml.jackson.databind.JsonNode body = MAPPER.readTree(req.getInputStream());
                         if ("delete".equals(body.path("action").asText())) {
                             UserService.deleteUser(user.getId());
                             if (session != null) session.invalidate();
                             MAPPER.writeValue(resp.getWriter(), Map.of("success", true, "message", "账号已注销"));
                             return;
                         }
                         name = body.path("name").asText(user.getName());
                         email = body.path("email").asText(user.getEmail());
                         targetPosition = body.path("targetPosition").asText(user.getTargetPosition());
                    } else if ("delete".equals(action)) {
                         UserService.deleteUser(user.getId());
                         if (session != null) session.invalidate();
                         MAPPER.writeValue(resp.getWriter(), Map.of("success", true, "message", "账号已注销"));
                         return;
                    }

                    if (name != null) user.setName(name);
                    if (email != null) user.setEmail(email);
                    if (targetPosition != null) user.setTargetPosition(targetPosition);

                    UserService.updateUser(user);

                    MAPPER.writeValue(resp.getWriter(), Map.of("success", true, "message", "更新成功", "user", user));
                } catch (Exception e) {
                    resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                    MAPPER.writeValue(resp.getWriter(), Map.of("success", false, "message", "操作失败: " + e.getMessage()));
                }
            } else {
                // Get profile
                MAPPER.writeValue(resp.getWriter(), Map.of("success", true, "user", user));
            }
        } catch (Exception e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            MAPPER.writeValue(resp.getWriter(), Map.of("success", false, "message", "系统错误: " + e.getMessage()));
        }
    }
}

