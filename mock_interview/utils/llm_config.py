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
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置，请检查 .env 文件")

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            timeout=120,
            max_retries=2
        )
        return client
    except Exception as e:
        logger.error(f"DeepSeek 客户端初始化失败：{str(e)}")
        raise Exception(f"客户端初始化失败：{str(e)}")


def call_deepseek(prompt, model="deepseek-chat", fallback=None):
    client = get_deepseek_client()
    try:
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
        if fallback:
            return fallback
        raise Exception(f"DeepSeek 真实错误：{str(e)}")


