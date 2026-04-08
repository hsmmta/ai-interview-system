# JTR_WSTZ
# @Time : 2026/3/23 19:10
# @Author :无题
# @Version: 未知
# @IDE:未知
# @Project : mock_interview
import os
from crewai import Agent
from crewai import Task
from crewai import LLM

llm = LLM(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    timeout=120,
    max_retries=3
)


# 培养师智能体
def create_mentor_agent(job_position="AI算法工程师"):
    if not job_position.strip():
        raise ValueError("岗位名称不能为空！")
    mentor_agent = Agent(
        role=f"{job_position}岗位能力提升指导师",
        goal=f"""
        1. 基于{job_position}岗位的面试评估报告，为应届生制定针对性的能力提升方案；
        2. 方案需结合面试中暴露的知识盲区、简历核心/次要关键词对应的能力短板；
        3. 内容包含：
        - 分阶段学习计划（入门→进阶，适配应届生学习节奏）；
        - 应届生易获取的免费学习资源、低成本实战项目；
        - 简历优化指导（针对项目描述不完整、技术栈缺失、无量化成果的问题，给出可落地的改写示例）；
        4. 所有建议需贴合应届生求职场景，优先覆盖岗位核心关键词对应的技能，兼顾通用软素质提升；
        5. 方案需具体可落地，避免空泛，明确学习周期、核心知识点和验收标准。
        """,
        backstory=f"""
        你是{job_position}岗位资深技术导师，有5年以上应届生培养经验，熟悉校招面试考点、应届生学习特点和应届生培养流程：
        1. 你会先分析面试评估报告，重点关注应届生在岗位核心关键词（如技术栈、项目、比赛）上的知识盲区；
        2. 你制定的学习计划符合应届生的时间节奏（如按学期/求职季划分阶段），优先推荐免费/低成本资源（如MOOC、开源文档、GitHub实战项目）；
        3. 你会结合校招高频考点，补充简历中缺失的核心关键词对应的技能学习建议（如应届生简历无项目经验，则推荐入门级实战项目）；
        4. 你会提供「简历优化指导」：
        - 针对项目仅写名称的问题：给出「项目背景+核心职责+技术栈+量化成果」的改写模板，比如将「基于Python的数据分析平台」改写为「基于Python+Pandas/Sklearn搭建用户行为分析平台，负责数据清洗/特征工程模块，处理10万+条用户日志，优化后分析效率提升30%」；
        - 针对无量化成果的问题：指导应届生从「性能优化、数据量、功能落地」等维度补充可量化的项目成果；
        5. 你会兼顾软素质提升（如面试表达、简历优化），适配应届生求职全流程；
        6. 你给出的建议会明确优先级，先攻克岗位核心技能，再补充通用能力，避免信息过载。
        """,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )
    return mentor_agent


def create_mentor_task(agent, evaluation_report, post_type="AI算法工程师"):
    mentor_task = Task(
        name=f"{post_type}岗位面试应届生能力提升指导",
        description=f"""
            应聘岗位类型：{post_type}
            能力评估报告：{evaluation_report}

            核心任务要求：
            1. 针对性提升建议：针对每个短板，结合对应岗位知识库，给出具体可落地的学习方向+实战案例（拒绝空泛话术）；
            2. 学习资源推荐：3-5个应届生友好资源（书籍/官方文档/实战教程/开源项目），优先贴合知识库考点；
            3. 1个月短期学习计划：按周划分重点，适配应届生学习节奏，聚焦薄弱点+岗位核心考点；
            4. 建议接地气、可执行，符合应届生时间安排，不推荐高阶晦涩内容。

            输出格式标准：
            【针对性提升建议】
            1. XXX短板：具体学习动作+实战练习（对应知识库考点）
            2. XXX短板：具体学习动作+实战练习（对应知识库考点）
            【推荐学习资源】
            1. XXX（类型：书籍/文档/课程，适配考点：XXX）
            2. XXX（类型：书籍/文档/课程，适配考点：XXX）
            3. XXX（类型：开源项目/实战，适配考点：XXX）
            ...
            【1个月应届生专属学习计划】
            - 第1周：夯实薄弱基础（对应知识库基础考点）
            - 第2周：突破核心技能（对应岗位专属考点）
            - 第3周：实战案例练习（贴合项目场景题）
            - 第4周：复盘巩固+模拟自测
        """,
        expected_output=f"""
            结构化{post_type}岗位提升方案，建议具体可落地、资源贴合知识库，计划适配应届生，总字数≤800字。
        """,
        agent=agent
    )
    return mentor_task