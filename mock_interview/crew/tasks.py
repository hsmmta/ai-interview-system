# JTR_WSTZ
# @Time : 2026/3/6 13:03
# @Author :无题
# @Version: δ֪
# @IDE:δ֪
# @Project : mock_interview
from crewai import Task
from utils.logger import setup_logger

# 初始化日志器
logger = setup_logger()


def create_interview_task(agent, user_info):
    logger.info(f"为候选人创建面试提问任务：{user_info}")
    interview_task = Task(
        # 任务名称（便于日志识别）
        name="Python技术面试提问",
        # 任务描述（核心：告诉智能体具体要做什么）
        description=f"""
            候选人基础信息：{user_info}

            任务要求：
            1. 生成5-8个核心技术问题，按「基础→进阶→项目」的逻辑顺序排列；
            2. 每个问题必须明确标注考察的知识点（例：「解释和编译有什么区别？」→ 考察点：代码的解释和编译）；
            3. 针对每个问题，补充1-2个追问问题（用于候选人回答不完整时）；
            4. 问题难度必须匹配候选人的经验（新手→基础题，1-3年→进阶题，3年以上→深度题）；
            5. 输出格式要求（便于后续解析）：
               【问题1】（考察点：XXX）
               - 追问1：XXX
               - 追问2：XXX
               【问题2】（考察点：XXX）
               - 追问1：XXX
               ...
        """,
        # 预期输出（明确格式，提升结果规范性）
        expected_output="""
            结构化的面试问题列表，包含问题、考察点、追问，格式清晰，无冗余内容，总字数控制在800字以内。
        """,
        # 绑定执行该任务的智能体
        agent=agent
    )
    logger.info("面试提问任务创建完成")
    return interview_task


def create_evaluation_task(agent, interview_content):
    """
    为评估师智能体创建「能力评估任务」：
    :param agent: 评估师智能体实例
    :param interview_content: 面试问题+候选人回答（现阶段先传面试问题，后续扩展真实回答）
    :return: 配置好的 Task 实例
    """
    logger.info("创建技术能力评估任务")
    evaluation_task = Task(
        name="Python技术能力评估",
        description=f"""
            面试对话内容：{interview_content}

            任务要求：
            1. 量化评分（0-10分，保留1位小数）：
               - 基础能力（语法/数据结构/内置函数）
               - 框架使用（Flask/Django/FastAPI等）
               - 项目经验（项目复杂度/解决问题的能力）
               - 问题解决能力（逻辑思维/故障排查）
            2. 短板分析：针对每个维度的低分项，分析具体的知识盲区或能力不足；
            3. 整体评价：总结候选人的核心优势、短板，以及与应聘岗位的匹配度；
            4. 输出格式要求：
               【评分结果】
               - 基础能力：X.X分
               - 框架使用：X.X分
               - 项目经验：X.X分
               - 问题解决能力：X.X分
               【短板分析】
               1. XXX维度：XXX问题
               2. ...
               【整体评价】
               XXX
        """,
        expected_output="""
            结构化的评估报告，评分客观，分析精准，格式清晰，总字数控制在600字以内。
        """,
        agent=agent
    )
    logger.info("技术能力评估任务创建完成")
    return evaluation_task


def create_mentor_task(agent, evaluation_report):
    """
    为指导师智能体创建「能力提升指导任务」：
    :param agent: 指导师智能体实例
    :param evaluation_report: 评估师生成的评估报告
    :return: 配置好的 Task 实例
    """
    logger.info("创建能力提升指导任务")
    mentor_task = Task(
        name="Python能力提升指导",
        description=f"""
            评估报告内容：{evaluation_report}

            任务要求：
            1. 针对性提升建议：针对每个短板，给出具体、可落地的学习建议（例：「装饰器学习」→ 推荐《流畅的Python》第7章 + 3个实战案例）；
            2. 学习资源推荐：推荐3-5个优质资源（书籍/官方文档/视频课程/开源项目）；
            3. 短期学习计划：制定1个月的学习计划，按周划分重点（例：第1周：补基础语法，第2周：练框架实战）；
            4. 输出格式要求：
               【针对性提升建议】
               1. XXX短板：XXX建议
               2. ...
               【推荐学习资源】
               1. XXX（类型：书籍，链接/来源：XXX）
               2. ...
               【1个月学习计划】
               - 第1周：XXX
               - 第2周：XXX
               - 第3周：XXX
               - 第4周：XXX
        """,
        expected_output="""
            结构化的能力提升计划，建议具体可落地，资源优质，计划合理，总字数控制在800字以内。
        """,
        agent=agent
    )
    logger.info("能力提升指导任务创建完成")
    return mentor_task


# 测试代码（简化版：仅验证任务函数定义，不依赖智能体导入）
if __name__ == "__main__":
    try:
        # 仅打印提示，验证代码无语法错误、核心函数可加载
        print("="*50)
        print("tasks.py 核心函数加载成功！")
        print("create_interview_task 函数已定义")
        print("create_evaluation_task 函数已定义")
        print("create_mentor_task 函数已定义")
        print("="*50)
    except Exception as e:
        logger.error(f"tasks.py 加载失败：{str(e)}", exc_info=True)
        print(f"tasks.py 加载失败：{str(e)}")