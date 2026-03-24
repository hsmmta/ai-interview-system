# utils/llm_config.py
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger("interview_system")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_deepseek_client():
    """获取 DeepSeek 客户端（优化超时配置）"""
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置，请检查 .env 文件")

        # 核心优化：配置客户端超时（全局）
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",  # 官方标准地址
            timeout=120,  # 客户端全局超时120秒
            max_retries=2  # 失败自动重试2次
        )
        return client
    except Exception as e:
        logger.error(f"DeepSeek 客户端初始化失败：{str(e)}")
        raise Exception(f"客户端初始化失败：{str(e)}")


# 模拟数据函数（保留，仅作为最后兜底）
def get_mock_interview_questions():
    return """
【问题1】（考察点：Python装饰器原理与应用）
- 追问1：装饰器可以传递参数吗？如何实现？
- 追问2：装饰器和闭包的关系是什么？
【问题2】（考察点：Flask路由与视图函数）
- 追问1：Flask中如何获取GET/POST请求参数？
- 追问2：Flask的上下文对象（request/session）的生命周期？
【问题3】（考察点：MySQL索引优化）
- 追问1：什么情况下索引会失效？
- 追问2：如何优化慢查询SQL？
【问题4】（考察点：Python异常处理）
- 追问1：try-except-else-finally 的执行顺序？
- 追问2：自定义异常如何实现？
【问题5】（考察点：Flask项目结构与部署）
- 追问1：Flask项目如何实现模块化？
- 追问2：Flask项目部署到服务器的常用方式？
    """


def get_mock_evaluation_report():
    return """
【评分结果】
- 基础能力：7.5分
- 框架使用：7.0分
- 项目经验：5.0分
- 问题解决能力：6.5分

【短板分析】
1. 框架使用维度：对Flask蓝图概念理解模糊，缺乏中等规模应用经验。
2. 项目经验维度：无大型项目经验，数据模型设计考虑不深入。
3. 问题解决能力维度：对并发编程仅有概念性了解。

【整体评价】
适合初级Python开发岗位，缺乏中级工程师所需的进阶技能。
    """


def get_mock_mentor_suggestion():
    return """
【针对性提升建议】
1. 精读Flask官方文档蓝图章节，重构单文件项目为多蓝图结构。
2. 从零实现完整博客系统，包含用户认证、文章CRUD、评论功能。
3. 学习Python并发/GIL知识，完成asyncio并发请求实验。

【推荐学习资源】
1. 《Flask Web开发实战》（书籍）；
2. Flask官方文档（https://flask.palletsprojects.com/）；
3. Real Python 并发编程教程。

【1个月学习计划】
- 第1周：掌握Flask蓝图，启动博客项目；
- 第2周：完成核心功能，深化数据库操作；
- 第3周：模拟并解决性能问题；
- 第4周：学习并发/异步，总结复盘。
    """


def call_deepseek(prompt, model="deepseek-chat", fallback=None):
    """
    核心优化：
    1. 延长超时到120秒
    2. 减少返回token数（加快响应）
    3. 降低temperature（更稳定）
    4. 自动重试2次
    5. 仅最后才用fallback，优先保证真实调用
    """
    client = get_deepseek_client()
    try:
        # 优化Prompt：明确要求简洁、快速返回
        optimized_prompt = f"""
        请严格按照要求回答，控制内容长度（不超过800字），优先保证回答速度：
        {prompt}
        """

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是专业的Python技术面试官，回答简洁、准确、结构化，无多余内容。"},
                {"role": "user", "content": optimized_prompt}
            ],
            stream=False,
            timeout=120,  # 超时120秒
            max_tokens=800,  # 限制返回长度（加快响应）
            temperature=0.3,  # 降低随机性，加快响应
            top_p=0.9
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"DeepSeek 调用成功，返回内容长度：{len(result)}")
        return result

    except APITimeoutError:
        logger.warning("DeepSeek 调用超时（120秒），使用兜底数据")
        return fallback if fallback else "调用超时，使用默认回答"
    except Exception as e:
        logger.error(f"DeepSeek 调用失败：{str(e)}", exc_info=True)
        # 仅在最后才用fallback，优先暴露真实错误
        if fallback:
            return fallback
        raise Exception(f"DeepSeek 真实错误：{str(e)}")


# 测试代码（验证长Prompt调用）
if __name__ == "__main__":
    try:
        # 测试长Prompt（模拟生成面试问题）
        test_prompt = """
        为1年经验的Python开发工程师（应聘Python开发岗位，熟悉Flask、MySQL）生成5道面试题，要求：
        1. 每道题包含考察点+核心问题+2个追问
        2. 难度匹配1年经验
        3. 覆盖Python基础、Flask、MySQL、异常处理、项目部署
        4. 内容简洁，结构化展示
        """
        print("开始测试长Prompt调用DeepSeek（预计10-30秒）...")
        result = call_deepseek(test_prompt, fallback=get_mock_interview_questions())
        print("\n" + "=" * 80)
        print("DeepSeek 真实调用结果：")
        print(result)
        print("=" * 80)
    except Exception as e:
        print(f"\n调用失败：{str(e)}")