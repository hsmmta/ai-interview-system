# crew/agents.py
import os
from crewai import Agent
# from utils.llm_config import get_llm
from utils.logger import setup_logger
logger = setup_logger()


def create_interviewer_agent():
    logger.info("开始创建「Python技术面试官」智能体")
    interviewer_agent = Agent(
        role="Python技术面试官",
        goal="Ϊ1年经验的Python开发工程师生成针对性的技术面试问题，覆盖基础、框架、项目经验维度",
        backstory="""你是资深Python技术面试官，有5年面试经验，擅长针对不同经验层级的候选人制定面试问题，
        熟悉Flask、MySQL等技术栈，能精准考察候选人的实际开发能力和知识盲区""",
        verbose=True,
        allow_delegation=False,
        # llm=llm,
        llm_config={
            "provider": "openai",
            "config": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "timeout": 60,  # 延长超时到60秒
                "max_retries": 3  # 重试3次
            }
        },
        # 规避 CrewAI 强制校验 OPENAI_API_KEY
        config={"llm": {"provider": "openai", "config": {"api_key": "dummy"}}}
    )
    logger.info("「Python技术面试官」智能体创建完成")
    return interviewer_agent

def create_evaluator_agent():
    logger.info("开始创建「技术能力评估师」智能体")
    evaluator_agent = Agent(
        role="Python技术能力评估师",
        goal="基于面试问题和候选人背景，量化评估技术能力，分析短板和匹配度",
        backstory="""你是技术专家，擅长评估Python开发工程师的能力，能客观打分并指出知识盲区，
        熟悉初级开发岗位的能力要求，给出精准的匹配度评价""",
        verbose=True,
        allow_delegation=False,
        llm_config={
            "provider": "openai",
            "config": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "timeout": 60,
                "max_retries": 3
            }
        },
        config={"llm": {"provider": "openai", "config": {"api_key": "dummy"}}}
    )
    logger.info("「技术能力评估师」智能体创建完成")
    return evaluator_agent

def create_mentor_agent():
    logger.info("开始创建「能力培养指导师」智能体")
    mentor_agent = Agent(
        role="Python能力提升指导师",
        goal="基于评估报告，给出针对性的学习建议、资源推荐和短期学习计划",
        backstory="""你是Python技术导师，擅长为初级开发工程师制定学习计划，
        熟悉优质的学习资源和实战项目，能给出可落地的提升建议""",
        verbose=True,
        allow_delegation=False,
        # llm=llm,
        llm_config={
            "provider": "openai",
            "config": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "timeout": 60,
                "max_retries": 3
            }
        },
        config={"llm": {"provider": "openai", "config": {"api_key": "dummy"}}}
    )
    logger.info("「能力培养指导师」智能体创建完成")
    return mentor_agent

# 测试代码
if __name__ == "__main__":
    try:
        interviewer = create_interviewer_agent()
        evaluator = create_evaluator_agent()
        mentor = create_mentor_agent()
        print("所有智能体创建成功！")
    except Exception as e:
        print(f"智能体创建失败：{str(e)}")