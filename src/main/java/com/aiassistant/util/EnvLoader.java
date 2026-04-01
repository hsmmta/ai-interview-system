package com.aiassistant.util;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lightweight .env loader for local/server startup.
 * It only loads once and never overrides existing system env values.
 */
public final class EnvLoader {
    private static volatile boolean loaded = false;
    // 使用内部 Map 存储配置，不再尝试通过反射修改 System.getenv()
    private static final Map<String, String> ENV_CACHE = new ConcurrentHashMap<>();

    private EnvLoader() {
    }

    public static synchronized void loadIfNeeded() {
        if (loaded) {
            return;
        }

        // 尝试 1: 当前工作目录
        File envFile = new File(".env");

        // 尝试 2: 常见项目路径 (针对 IDE 或 Tomcat 启动路径不一致的情况)
        if (!envFile.exists()) {
            // 针对用户的绝对路径回退
            envFile = new File("E:\\项目网站\\ai-assistant\\.env");
        }

        // 尝试 3: 尝试从 ClassPath 根目录找（有时候会被拷贝过去）
        if (!envFile.exists()) {
             URL url = EnvLoader.class.getClassLoader().getResource(".env");
             if (url != null) {
                 envFile = new File(url.getFile());
             }
        }

        if (!envFile.exists() || !envFile.isFile()) {
            System.err.println("【EnvLoader】警告: 未找到 .env 文件。当前工作目录: " + new File(".").getAbsolutePath());
            loaded = true;
            return;
        }

        System.out.println("【EnvLoader】正在加载配置文件: " + envFile.getAbsolutePath());

        // 读取文件内容到 ENV_CACHE
        try (BufferedReader br = new BufferedReader(new FileReader(envFile, StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                String t = normalizeLine(line);
                if (t.isEmpty() || t.startsWith("#")) {
                    continue;
                }
                if (t.startsWith("export ")) {
                    t = t.substring("export ".length()).trim();
                }
                int idx = t.indexOf('=');
                if (idx <= 0) {
                    continue;
                }
                String key = t.substring(0, idx).trim();
                String value = cleanValue(t.substring(idx + 1));
                if (!key.isEmpty()) {
                    ENV_CACHE.put(key, value);
                }
            }
            System.out.println("【EnvLoader】已加载配置项数量: " + ENV_CACHE.size());
            if (ENV_CACHE.containsKey("ALIBABA_CLOUD_ACCESS_KEY_ID")) {
                System.out.println("【EnvLoader】检测到包含 ALIYUN AccessKey 配置。");
            } else {
                System.err.println("【EnvLoader】警告: 未在 .env 文件中发现 ALIBABA_CLOUD_ACCESS_KEY_ID 配置。");
            }

        } catch (Exception e) {
            System.err.println("【EnvLoader】读取 .env 文件失败: " + e.getMessage());
            e.printStackTrace();
            loaded = true;
            return;
        }

        loaded = true;
    }

    public static String get(String key, String defaultValue) {
        loadIfNeeded();

        // 1. 优先从系统环境变量读取
        String v = System.getenv(key);
        if (v != null && !v.trim().isEmpty()) {
            return v.trim();
        }

        // 2. 尝试从加载的 .env 缓存中读取
        v = ENV_CACHE.get(key);
        if (v != null && !v.trim().isEmpty()) {
            return v.trim();
        }

        // 3. 返回默认值
        return defaultValue;
    }

    public static String getRequired(String key) {
        String v = get(key, null);
        if (v == null || v.isEmpty()) {
            throw new IllegalStateException("Missing required environment variable: " + key);
        }
        return v;
    }

    private static String normalizeLine(String line) {
        if (line == null) {
            return "";
        }
        String t = line.trim();
        // 处理 UTF-8 BOM
        if (!t.isEmpty() && t.charAt(0) == '\uFEFF') {
            t = t.substring(1).trim();
        }
        return t;
    }

    private static String cleanValue(String rawValue) {
        if (rawValue == null) {
            return "";
        }
        String v = rawValue.trim();
        if (!(v.startsWith("\"") || v.startsWith("'"))) {
            int commentIdx = v.indexOf(" #");
            if (commentIdx >= 0) {
                v = v.substring(0, commentIdx).trim();
            }
        }
        if (v.length() >= 2) {
            char first = v.charAt(0);
            char last = v.charAt(v.length() - 1);
            if ((first == '"' && last == '"') || (first == '\'' && last == '\'')) {
                v = v.substring(1, v.length() - 1);
            }
        }
        return v.trim();
    }
}
