package com.aiassistant.service;

import com.aliyun.credentials.Client;
import com.aliyun.dypnsapi20170525.models.SendSmsVerifyCodeRequest;
import com.aliyun.dypnsapi20170525.models.SendSmsVerifyCodeResponse;
import com.aliyun.tea.TeaException;
import com.aliyun.teaopenapi.models.Config;
import com.aiassistant.util.EnvLoader;
import java.lang.reflect.Method;

public class SMSService {

    /**
     * 发送验证码并返回验证码字符串（LoginServlet 会缓存并用于校验）
     * 约定：
     * - SMS_REAL_SEND=true  -> 调阿里云真实发送
     * - SMS_REAL_SEND=false -> 直接返回 null（让上层走本地兜底）
     */
    public static String sendVerificationCode(String phone) throws Exception {
        // 读取 AccessKey 配置
        String accessKeyId = EnvLoader.get("ALIBABA_CLOUD_ACCESS_KEY_ID", null);
        String accessKeySecret = EnvLoader.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", null);

        // 如果未配置 AccessKey，则无法发送真实短信，返回 null 走本地模拟
        if (accessKeyId == null || accessKeySecret == null || accessKeyId.isEmpty() || accessKeySecret.isEmpty()) {
            System.err.println("【SMSService】未找到 ALIYUN AccessKey 配置，将使用本地模拟短信发送。");
            return null;
        }

        // 默认开启真实发送，除非显式关闭
        boolean realSend = Boolean.parseBoolean(EnvLoader.get("SMS_REAL_SEND", "true"));
        if (!realSend) {
            System.out.println("【SMSService】SMS_REAL_SEND=false，跳过真实发送。");
            return null;
        }

        String endpoint = EnvLoader.get("ALIYUN_SMS_ENDPOINT", "dypnsapi.aliyuncs.com");
        String schemeName = EnvLoader.get("ALIYUN_SMS_SCHEME_NAME", "ai-assistant");
        String countryCode = EnvLoader.get("ALIYUN_SMS_COUNTRY_CODE", "86");
        String signName = EnvLoader.get("ALIYUN_SMS_SIGN_NAME", "速通互联验证码"); // 默认签名防乱码
        String templateCode = EnvLoader.get("ALIYUN_SMS_TEMPLATE_CODE", "100001");
        String templateParam = EnvLoader.get("ALIYUN_SMS_TEMPLATE_PARAM", "{\"code\":\"##code##\",\"min\":\"5\"}");
        String outId = EnvLoader.get("ALIYUN_SMS_OUT_ID", "ai-assistant");

        long codeLength = 4L;
        try { codeLength = Long.parseLong(EnvLoader.get("ALIYUN_SMS_CODE_LENGTH", "4")); } catch (Exception e) {}

        long validTime = 300L;
        try { validTime = Long.parseLong(EnvLoader.get("ALIYUN_SMS_VALID_TIME", "300")); } catch (Exception e) {}

        long interval = 60L;
        try { interval = Long.parseLong(EnvLoader.get("ALIYUN_SMS_INTERVAL", "60")); } catch (Exception e) {}

        // 直接显式使用 AccessKey 初始化，避免依赖环境变量注入不生效的问题
        Config config = new Config()
                .setAccessKeyId(accessKeyId)
                .setAccessKeySecret(accessKeySecret);
        config.endpoint = endpoint;

        com.aliyun.dypnsapi20170525.Client smsClient = new com.aliyun.dypnsapi20170525.Client(config);

        SendSmsVerifyCodeRequest req = new SendSmsVerifyCodeRequest()
                .setSchemeName(schemeName)
                .setCountryCode(countryCode)
                .setPhoneNumber(phone)
                .setSignName(signName)
                .setTemplateCode(templateCode)
                .setTemplateParam(templateParam)
                .setOutId(outId)
                .setCodeLength(codeLength)
                .setValidTime(validTime)
                .setInterval(interval)
                .setReturnVerifyCode(true); // 必须开启才会有返回值

        try {
            SendSmsVerifyCodeResponse resp = smsClient.sendSmsVerifyCode(req);

            if (resp != null && resp.getBody() != null) {
                // 打印调试信息，方便排查
                System.out.println("【SMSService】阿里云响应: " + new com.google.gson.Gson().toJson(resp.getBody()));

                String verifyCode = extractVerifyCode(resp.getBody());
                if (verifyCode != null && !verifyCode.isEmpty()) {
                    return verifyCode;
                }
            }
            return "";
        } catch (TeaException e) {
            String recommend = "";
            try {
                Object r = e.getData() == null ? null : e.getData().get("Recommend");
                recommend = r == null ? "" : String.valueOf(r);
            } catch (Exception ignore) {}
            throw new RuntimeException(
                    "阿里云短信发送失败: " + e.getMessage() + (recommend.isEmpty() ? "" : " | Recommend: " + recommend),
                    e
            );
        } catch (Exception e) {
            throw new RuntimeException("短信发送异常: " + e.getMessage(), e);
        }
    }
    private static String extractVerifyCode(Object body) {
        if (body == null) return null;

        // 1. 尝试获取内部模型对象 (Model / Data)
        Object dataObj = body;
        try {
            // 大部分 Dypnsapi 响应将数据放在 getModel() 中
            Method getModel = body.getClass().getMethod("getModel");
            Object model = getModel.invoke(body);
            if (model != null) {
                dataObj = model;
            }
        } catch (Exception ignore) {
            // 没有 getModel，继续尝试使用 body 本身
        }

        // 2. 优先查找 getVerifyCode (这是通常存放验证码的字段)
        try {
            Method m = dataObj.getClass().getMethod("getVerifyCode");
            Object v = m.invoke(dataObj);
            if (v != null) {
                String s = String.valueOf(v).trim();
                if (!s.isEmpty()) return s;
            }
        } catch (Exception ignore) {}

        // 3. 其次查找 getCode，但必须排除状态码 "OK"
        try {
            Method m = dataObj.getClass().getMethod("getCode");
            Object v = m.invoke(dataObj);
            if (v != null) {
                String s = String.valueOf(v).trim();
                // 排除常见的状态码值
                if (!s.isEmpty() && !"OK".equalsIgnoreCase(s) && !"Success".equalsIgnoreCase(s)) {
                    return s;
                }
            }
        } catch (Exception ignore) {}

        return null; // 未提取到有效验证码
    }
}
