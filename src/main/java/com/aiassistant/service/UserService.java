package com.aiassistant.service;

import com.aiassistant.model.User;
import com.aiassistant.util.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.LocalDateTime;

public class UserService {

    public static User findOrCreateByPhone(String phone) throws Exception {
        User user = findByPhone(phone);
        if (user == null) {
            // Previously auto-created, now maybe we should return null if logic requires explicit registration?
            // But to keep backward compatibility and safety, we can keep auto-create but leave new fields empty.
            // However, the user wants a registration page.
            // For now, let's keep this for legacy login, but RegisterServlet will use a specific create method.
            user = new User(phone);
            user.setNickname("用户" + phone.substring(phone.length() - 4));
            createUser(user);
            user = findByPhone(phone);
        } else {
            updateLastLogin(user.getId());
        }
        return user;
    }

    public static User registerUser(String phone, String name, String email, String targetPosition) throws Exception {
        User existing = findByPhone(phone);
        if (existing != null) {
            // User exists, maybe update info? Or throw error?
            // Update info for now essentially acting as upsert or profile update on register
            existing.setName(name);
            existing.setEmail(email);
            existing.setTargetPosition(targetPosition);
            updateUser(existing);
            return existing;
        }

        User user = new User(phone);
        user.setNickname(name); // Use name as nickname initially
        user.setName(name);
        user.setEmail(email);
        user.setTargetPosition(targetPosition);
        createUser(user);
        return findByPhone(phone);
    }

    public static void updateUser(User user) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE users SET name = ?, email = ?, target_position = ?, nickname = ? WHERE id = ?")) {
            ps.setString(1, user.getName() != null ? user.getName() : "");
            ps.setString(2, user.getEmail() != null ? user.getEmail() : "");
            ps.setString(3, user.getTargetPosition() != null ? user.getTargetPosition() : "");
            ps.setString(4, user.getNickname());
            ps.setLong(5, user.getId());
            ps.executeUpdate();
        }
    }

    public static User findByPhone(String phone) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "SELECT * FROM users WHERE phone = ?")) {
            ps.setString(1, phone);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                User user = new User();
                user.setId(rs.getLong("id"));
                user.setPhone(rs.getString("phone"));
                user.setNickname(rs.getString("nickname"));
                user.setName(rs.getString("name"));
                user.setEmail(rs.getString("email"));
                user.setTargetPosition(rs.getString("target_position"));
                user.setCreatedAt(rs.getString("created_at"));
                user.setLastLoginAt(rs.getString("last_login_at"));
                return user;
            }
        }
        return null;
    }

    private static void createUser(User user) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "INSERT INTO users (phone, nickname, created_at, last_login_at, name, email, target_position) VALUES (?, ?, ?, ?, ?, ?, ?)")) {
            ps.setString(1, user.getPhone());
            ps.setString(2, user.getNickname());
            ps.setString(3, user.getCreatedAt());
            ps.setString(4, user.getLastLoginAt());
            ps.setString(5, user.getName() != null ? user.getName() : "");
            ps.setString(6, user.getEmail());
            ps.setString(7, user.getTargetPosition());
            ps.executeUpdate();
        }
    }

    private static void updateLastLogin(Long userId) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE users SET last_login_at = ? WHERE id = ?")) {
            ps.setString(1, LocalDateTime.now().toString());
            ps.setLong(2, userId);
            ps.executeUpdate();
        }
    }

    public static void deleteUser(Long userId) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement("DELETE FROM users WHERE id = ?")) {
            ps.setLong(1, userId);
            ps.executeUpdate();
        }
    }
}
