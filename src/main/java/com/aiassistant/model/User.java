package com.aiassistant.model;

import java.time.LocalDateTime;

public class User {
    private Long id;
    private String phone;
    private String nickname;
    private String name;
    private String email;
    private String targetPosition;
    private String createdAt;
    private String lastLoginAt;

    // Force rebuild
    public User() {}

    public User(String phone) {
        this.phone = phone;
        this.createdAt = LocalDateTime.now().toString();
        this.lastLoginAt = LocalDateTime.now().toString();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getNickname() { return nickname; }
    public void setNickname(String nickname) { this.nickname = nickname; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getTargetPosition() { return targetPosition; }
    public void setTargetPosition(String targetPosition) { this.targetPosition = targetPosition; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getLastLoginAt() { return lastLoginAt; }
    public void setLastLoginAt(String lastLoginAt) { this.lastLoginAt = lastLoginAt; }
}
