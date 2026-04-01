# JTR_WSTZ
# @Time : 2026/3/6 13:05
# @Author :无题
# @Version: 1.0
# @IDE: PyCharm
# @Project : mock_interview
import logging
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def setup_logger():
    utils_dir = os.path.dirname(os.path.abspath(__file__))  # utils 目录路径
    project_root = os.path.dirname(utils_dir)  # 项目根目录路径

    log_dir = os.path.join(project_root, "logs")  # 日志目录：项目根目录/logs
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = os.path.join(log_dir, "interview_system.log")
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    final_level = level_mapping.get(log_level, logging.INFO)

    logger = logging.getLogger("interview_system")
    logger.setLevel(final_level)
    logger.handlers.clear()  # 清空已有处理器，防止重复输出

    console_handler = logging.StreamHandler()
    console_handler.setLevel(final_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(final_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"日志工具初始化完成！")
    logger.info(f"日志级别：{log_level}（映射后：{final_level}）")
    logger.info(f"日志文件路径：{log_file}")

    return logger


if __name__ == "__main__":
    # 初始化日志器
    logger = setup_logger()

    logger.debug("这是 DEBUG 级日志（调试信息，仅开发时查看）")
    logger.info("这是 INFO 级日志（正常运行信息）")
    logger.warning("这是 WARNING 级日志（警告信息，需关注）")
    logger.error("这是 ERROR 级日志（错误信息，需修复）")
    logger.critical("这是 CRITICAL 级日志（严重错误，系统可能崩溃）")

    print("=" * 80)
    print("日志测试完成！")
    print(f"日志文件生成路径：{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'interview_system.log')}")
    print("请查看：")
    print("  1. 控制台输出的日志内容")
    print("  2. 项目根目录 logs/interview_system.log 文件内容")
    print("  3. 确认中文是否乱码、路径是否正确")
    print("=" * 80)