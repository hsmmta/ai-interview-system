package com.aiassistant.web;

import com.aiassistant.model.User;
import com.aiassistant.service.SMSService;
import com.aiassistant.service.UserService;
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
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

public class RegisterServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final Map<String, CodeEntry> CODE_CACHE = new ConcurrentHashMap<>();
    private static final long EXPIRE_MS = 5 * 60 * 1000L;

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setCharacterEncoding(StandardCharsets.UTF_8.name());
        resp.setContentType("application/json;charset=UTF-8");

        try {
            JsonNode body = MAPPER.readTree(req.getInputStream());
            String action = body.path("action").asText("");
            String phone = body.path("phone").asText("").trim();

            if (phone.isEmpty()) {
                writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "手机号不能为空");
                return;
            }

            if ("sendCode".equals(action)) {
                handleSendCode(resp, phone);
                return;
            }

            if ("register".equals(action)) {
                String code = body.path("code").asText("").trim();
                String name = body.path("name").asText("").trim();
                String email = body.path("email").asText("").trim();
                String targetPosition = body.path("targetPosition").asText("").trim();
                handleRegister(req, resp, phone, code, name, email, targetPosition);
                return;
            }

            writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "不支持的action");
        } catch (Exception e) {
            e.printStackTrace();
            writeError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "系统错误: " + e.getMessage());
        }
    }

    private void handleSendCode(HttpServletResponse resp, String phone) throws IOException {
        try {
            User existing = UserService.findByPhone(phone);
            if (existing != null) {
                // If implementing strict registration, we might error here.
                // But for user convenience (maybe they forgot they registered), we might allow sending code
                // and then just update their info on 'register'.
                // However, usually register means "new user".
                // Let's warn but allow sending code, treating it as potential account recovery/update.
                // Or to be strict:
                // writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "该手机号已注册，请直接登录");
                // return;
            }

            // Reuse SMSService logic (simplified here)
            String devCode = null;
            try {
                devCode = SMSService.sendVerificationCode(phone);
            } catch (Exception e) {
                System.err.println("Register SMS Failed: " + e.getMessage());
            }

            if (devCode == null || devCode.isBlank()) {
                devCode = String.format("%04d", new Random().nextInt(10000));
            }

            CODE_CACHE.put(phone, new CodeEntry(devCode, System.currentTimeMillis() + EXPIRE_MS));

            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "message", "验证码已发送",
                    "devCode", devCode // Exposing for dev convenience as in LoginServlet
            ));
        } catch (Exception e) {
            writeError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "发送失败: " + e.getMessage());
        }
    }

    private void handleRegister(HttpServletRequest req, HttpServletResponse resp, String phone, String code,
                                String name, String email, String targetPosition) throws IOException {
        if (!verifyCode(phone, code)) {
            writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "验证码错误或已过期");
            return;
        }

        try {
            User user = UserService.registerUser(phone, name, email, targetPosition);

            // Auto login
            HttpSession session = req.getSession(true);
            session.setAttribute("userId", user.getId());
            session.setAttribute("phone", user.getPhone());

            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "message", "注册成功",
                    "userId", user.getId()
            ));
        } catch (Exception e) {
            writeError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "注册失败: " + e.getMessage());
        }
    }

    private boolean verifyCode(String phone, String code) {
        CodeEntry entry = CODE_CACHE.get(phone);
        if (entry == null || System.currentTimeMillis() > entry.expireAt) {
            CODE_CACHE.remove(phone);
            return false;
        }
        boolean match = entry.code.equals(code);
        if (match) CODE_CACHE.remove(phone);
        return match;
    }

    private void writeError(HttpServletResponse resp, int status, String msg) throws IOException {
        resp.setStatus(status);
        MAPPER.writeValue(resp.getWriter(), Map.of("success", false, "message", msg));
    }

    private static class CodeEntry {
        final String code;
        final long expireAt;
        CodeEntry(String code, long expireAt) { this.code = code; this.expireAt = expireAt; }
    }
}

