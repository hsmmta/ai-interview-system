package com.aiassistant.web;

import com.aiassistant.model.User;
import com.aiassistant.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class ResumeServlet extends HttpServlet {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final String UPLOAD_DIR = "resumes";
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        resp.setContentType("application/json;charset=UTF-8");

        HttpSession session = req.getSession(false);
        Long userId = (session != null) ? (Long) session.getAttribute("userId") : null;

        if (userId == null) {
            writeError(resp, HttpServletResponse.SC_UNAUTHORIZED, "未登录");
            return;
        }

        if (!ServletFileUpload.isMultipartContent(req)) {
            writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "请上传文件");
            return;
        }

        try {
            User user = UserService.findByPhone((String) session.getAttribute("phone"));
            if (user == null) {
                writeError(resp, HttpServletResponse.SC_NOT_FOUND, "用户不存在");
                return;
            }

            DiskFileItemFactory factory = new DiskFileItemFactory();
            ServletFileUpload upload = new ServletFileUpload(factory);
            upload.setFileSizeMax(MAX_FILE_SIZE);

            List<FileItem> items = upload.parseRequest(req);
            FileItem fileItem = null;
            for (FileItem item : items) {
                if (!item.isFormField() && item.getSize() > 0) {
                    fileItem = item;
                    break;
                }
            }

            if (fileItem == null) {
                writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "未找到文件");
                return;
            }

            // check extension
            String fileName = fileItem.getName();
            if (!fileName.toLowerCase().endsWith(".pdf")) {
                writeError(resp, HttpServletResponse.SC_BAD_REQUEST, "仅支持PDF格式简历");
                return;
            }

            // Save file
            String uploadPath = getServletContext().getRealPath("") + File.separator + UPLOAD_DIR;
            File uploadDir = new File(uploadPath);
            if (!uploadDir.exists()) uploadDir.mkdirs();

            String newFileName = userId + "_" + UUID.randomUUID().toString() + ".pdf";
            String filePath = uploadPath + File.separator + newFileName;
            File storeFile = new File(filePath);
            fileItem.write(storeFile);

            // Parse PDF
            String extractedText = parsePdfContent(storeFile);
            String intention = extractIntention(extractedText);

            // Update User
            user.setResumePath(UPLOAD_DIR + "/" + newFileName);
            if (intention != null && !intention.isEmpty()) {
                user.setTargetPosition(intention);
            } else {
                user.setTargetPosition("通用岗位"); // Fallback
            }
            UserService.updateUser(user);

            MAPPER.writeValue(resp.getWriter(), Map.of(
                    "success", true,
                    "message", "简历上传成功",
                    "targetPosition", user.getTargetPosition(),
                    "resumePath", user.getResumePath()
            ));

        } catch (Exception e) {
            e.printStackTrace();
            writeError(resp, HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "上传失败: " + e.getMessage());
        }
    }

    private String parsePdfContent(File file) {
        try (PDDocument document = PDDocument.load(file)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        } catch (IOException e) {
            System.err.println("PDF Parse Error: " + e.getMessage());
            return "";
        }
    }

    private String extractIntention(String text) {
        // Simple keyword matching for now
        // This is a naive implementation. In a real world, we might use NLP or regex.
        if (text.contains("算法") || text.contains("AI") || text.contains("深度学习")) return "AI算法工程师";
        if (text.contains("数据") || text.contains("ETL") || text.contains("Data")) return "AI数据开发工程师";
        if (text.contains("Java") || text.contains("后端") || text.contains("Spring")) return "Java后端开发";
        if (text.contains("前端") || text.contains("Vue") || text.contains("React")) return "前端开发";

        return "Java后端开发"; // Default
    }

    private void writeError(HttpServletResponse resp, int status, String msg) throws IOException {
        resp.setStatus(status);
        PrintWriter writer = resp.getWriter();
        MAPPER.writeValue(writer, Map.of("success", false, "message", msg));
    }
}

