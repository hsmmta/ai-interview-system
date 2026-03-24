package com.aiassistant.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

public class DBUtil {
    private static final String DB_URL = "jdbc:sqlite:E:/项目网站/ai-assistant/interview.db";

    static {
        try {
            Class.forName("org.sqlite.JDBC");
            initDB();
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("SQLite JDBC driver not found", e);
        }
    }

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    private static void initDB() {
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {

            // 用户表
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE NOT NULL,
                    nickname TEXT,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT NOT NULL
                )
            """);

            try { stmt.execute("ALTER TABLE users ADD COLUMN name TEXT"); } catch (Exception e) {/* ignore if exists */}
            try { stmt.execute("ALTER TABLE users ADD COLUMN email TEXT"); } catch (Exception e) {/* ignore if exists */}
            try { stmt.execute("ALTER TABLE users ADD COLUMN target_position TEXT"); } catch (Exception e) {/* ignore if exists */}

            // 面试会话表
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS interview_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    interview_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    question_count INTEGER NOT NULL,
                    questions_json TEXT,
                    answers_json TEXT,
                    evaluation_json TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    submitted_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """);

            // 验证码缓存表（简单实现）
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS sms_codes (
                    phone TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """);

        } catch (SQLException e) {
            throw new RuntimeException("Database initialization failed", e);
        }
    }
}
