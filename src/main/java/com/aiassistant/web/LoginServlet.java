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

public class LoginServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    // 本地兜底验证码缓存（5分钟）
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

            if ("verify".equals(action)) {
                String code = body.path("code").asText("").trim();
                handleVerify(req, resp, phone, code);
                return;
            }

            writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "不支持的action");
        } catch (Exception e) {
            String msg = safeErr(e);
            writeError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "请求处理失败: " + msg);
        }
    }

    private void handleSendCode(HttpServletResponse resp, String phone) throws Exception {
        // 先尝试真实短信，失败则走本地兜底码
        try {
            String devCode = SMSService.sendVerificationCode(phone);
            if (devCode == null || devCode.isBlank()) {
                System.out.println("【LoginServlet】真实短信发送返回空，转为本地模拟模式。");
                devCode = genAndCacheCode(phone);
            } else {
                System.out.println("【LoginServlet】真实短信发送成功。");
                cacheCode(phone, devCode);
            }

            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "message", "验证码已发送",
                    "devCode", devCode
            ));
        } catch (Exception ex) {
            System.err.println("【LoginServlet】短信发送过程发生异常，已降级为本地模拟。异常信息: " + ex.getMessage());
            ex.printStackTrace();

            String fallbackCode = genAndCacheCode(phone);
            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "message", "短信网关不可用，已使用本地验证码",
                    "devCode", fallbackCode,
                    "gatewayError", safeErr(ex)
            ));
        }
    }

    private void handleVerify(HttpServletRequest req, HttpServletResponse resp, String phone, String code) throws Exception {
        if (code.isEmpty()) {
            writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "验证码不能为空");
            return;
        }

        System.out.println("【LoginServlet】收到登录验证请求: phone=" + phone + ", code=" + code);

        boolean ok = verifyLocalCode(phone, code);

        if (!ok) {
            System.out.println("【LoginServlet】验证失败。");
            writeError(resp, HttpServletResponse.SC_UNAUTHORIZED, "验证码错误或已过期");
            return;
        }

        // 检查用户是否存在（不再自动创建）
        User user = UserService.findByPhone(phone);
        if (user == null) {
            // 用户未注册，拒绝登录
            System.out.println("【LoginServlet】用户未注册，登录失败: phone=" + phone);
            // 401 也可以，或者 403，前端需要识别 message
            writeError(resp, HttpServletResponse.SC_UNAUTHORIZED, "该手机号未注册，请先点击注册");
            return;
        }

        HttpSession session = req.getSession(true);
        session.setAttribute("userId", user.getId());
        session.setAttribute("phone", phone);

        MAPPER.writeValue(resp.getWriter(), Map.of(
                "success", true,
                "message", "登录成功",
                "userId", user.getId()
        ));
    }

    private String genAndCacheCode(String phone) {
        String code = String.format("%04d", new Random().nextInt(10000));
        cacheCode(phone, code);
        return code;
    }

    private void cacheCode(String phone, String code) {
        CODE_CACHE.put(phone, new CodeEntry(code, System.currentTimeMillis() + EXPIRE_MS));
    }

    private boolean verifyLocalCode(String phone, String code) {
        CodeEntry entry = CODE_CACHE.get(phone);
        System.out.println("【LoginServlet】本地校验: phone=" + phone + ", inputCode=" + code);
        if (entry == null) {
            System.out.println("【LoginServlet】本地校验失败: 缓存中无此手机号记录。");
            return false;
        }
        if (System.currentTimeMillis() > entry.expireAt) {
            System.out.println("【LoginServlet】本地校验失败: 验证码已过期。");
            CODE_CACHE.remove(phone);
            return false;
        }
        boolean match = entry.code.equals(code);
        System.out.println("【LoginServlet】本地校验结果: " + match);
        // 验证成功后移除，防止重用
        if (match) {
            CODE_CACHE.remove(phone);
        }
        return match;
    }

    private String safeErr(Throwable t) {
        return t.getClass().getSimpleName() + ": " + String.valueOf(t.getMessage());
    }

    private void writeError(HttpServletResponse resp, int status, String msg) throws IOException {
        resp.setStatus(status);
        MAPPER.writeValue(resp.getWriter(), Map.of("error", msg));
    }

    private static class CodeEntry {
        final String code;
        final long expireAt;

        CodeEntry(String code, long expireAt) {
            this.code = code;
            this.expireAt = expireAt;
        }
    }
}
