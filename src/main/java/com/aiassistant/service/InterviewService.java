package com.aiassistant.service;

import com.aiassistant.model.InterviewSession;
import com.aiassistant.util.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.LocalDateTime;

public class InterviewService {

    public static InterviewSession createSession(Long userId, String interviewType, String direction, int questionCount) throws Exception {
        InterviewSession session = new InterviewSession();
        session.setUserId(userId);
        session.setInterviewType(interviewType);
        session.setDirection(direction);
        session.setQuestionCount(questionCount);
        session.setStatus("created");
        session.setCreatedAt(LocalDateTime.now());

        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "INSERT INTO interview_sessions (user_id, interview_type, direction, question_count, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                     PreparedStatement.RETURN_GENERATED_KEYS)) {
            ps.setLong(1, session.getUserId());
            ps.setString(2, session.getInterviewType());
            ps.setString(3, session.getDirection());
            ps.setInt(4, session.getQuestionCount());
            ps.setString(5, session.getStatus());
            ps.setString(6, session.getCreatedAt().toString());
            ps.executeUpdate();

            ResultSet rs = ps.getGeneratedKeys();
            if (rs.next()) {
                session.setId(rs.getLong(1));
            }
        }
        return session;
    }

    public static InterviewSession getSessionById(Long sessionId) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "SELECT * FROM interview_sessions WHERE id = ?")) {
            ps.setLong(1, sessionId);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                InterviewSession session = new InterviewSession();
                session.setId(rs.getLong("id"));
                session.setUserId(rs.getLong("user_id"));
                session.setInterviewType(rs.getString("interview_type"));
                session.setDirection(rs.getString("direction"));
                session.setQuestionCount(rs.getInt("question_count"));
                session.setQuestionsJson(rs.getString("questions_json"));
                session.setAnswersJson(rs.getString("answers_json"));
                session.setEvaluationJson(rs.getString("evaluation_json"));
                session.setStatus(rs.getString("status"));
                session.setCreatedAt(LocalDateTime.parse(rs.getString("created_at")));
                String submittedAt = rs.getString("submitted_at");
                if (submittedAt != null) {
                    session.setSubmittedAt(LocalDateTime.parse(submittedAt));
                }
                return session;
            }
        }
        return null;
    }

    public static void updateQuestions(Long sessionId, String questionsJson) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE interview_sessions SET questions_json = ?, status = 'answering' WHERE id = ?")) {
            ps.setString(1, questionsJson);
            ps.setLong(2, sessionId);
            ps.executeUpdate();
        }
    }

    public static void submitAnswers(Long sessionId, String answersJson) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE interview_sessions SET answers_json = ?, status = 'submitted', submitted_at = ? WHERE id = ?")) {
            ps.setString(1, answersJson);
            ps.setString(2, LocalDateTime.now().toString());
            ps.setLong(3, sessionId);
            ps.executeUpdate();
        }
    }

    public static void updateEvaluation(Long sessionId, String evaluationJson) throws Exception {
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE interview_sessions SET evaluation_json = ?, status = 'evaluated' WHERE id = ?")) {
            ps.setString(1, evaluationJson);
            ps.setLong(2, sessionId);
            ps.executeUpdate();
        }
    }
}

