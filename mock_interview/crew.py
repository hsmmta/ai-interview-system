# 根目录 crew.py
import os
import re
from crew.agents import create_interviewer_agent, create_evaluator_agent, create_mentor_agent
from crew.tasks import create_interview_task, create_evaluation_task, create_mentor_task
from utils.logger import setup_logger
from utils.llm_config import (
    call_deepseek,
    get_mock_interview_questions,
    get_mock_evaluation_report,
    get_mock_mentor_suggestion
)

logger = setup_logger()


def run_interview_flow(user_info):
    """
    非交互式流程：仅生成面试问题、评估报告、提升建议（原逻辑保留）
    """
    try:
        logger.info(f"开始执行面试流程，候选人信息：{user_info}")

        # 1. 创建智能体/任务（仅用其描述生成 prompt）
        interviewer = create_interviewer_agent()
        interview_task = create_interview_task(interviewer, user_info)

        # 2. 直接调用 DeepSeek 生成面试问题（核心！避开 CrewAI 封装）
        logger.info("调用 DeepSeek 生成面试问题...")
        interview_questions = call_deepseek(
            interview_task.description,
            fallback=get_mock_interview_questions()
        )

        # 3. 生成评估报告
        logger.info("调用 DeepSeek 生成评估报告...")
        evaluation_prompt = f"""基于以下面试问题和候选人信息，按要求生成评估报告：
        候选人信息：{user_info}
        面试问题：{interview_questions}
        {create_evaluation_task(None, "").description}"""
        evaluation_report = call_deepseek(
            evaluation_prompt,
            fallback=get_mock_evaluation_report()
        )

        # 4. 生成提升建议
        logger.info("调用 DeepSeek 生成提升建议...")
        mentor_prompt = f"""基于以下评估报告，按要求生成提升建议：
        评估报告：{evaluation_report}
        {create_mentor_task(None, "").description}"""
        mentor_suggestion = call_deepseek(
            mentor_prompt,
            fallback=get_mock_mentor_suggestion()
        )

        logger.info("面试流程执行完成！")
        return {
            "interview_questions": interview_questions,
            "evaluation_report": evaluation_report,
            "mentor_suggestion": mentor_suggestion,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"面试流程执行失败：{str(e)}", exc_info=True)
        # 异常时返回模拟数据兜底
        return {
            "interview_questions": get_mock_interview_questions(),
            "evaluation_report": get_mock_evaluation_report(),
            "mentor_suggestion": get_mock_mentor_suggestion(),
            "status": "error",
            "error_msg": str(e)
        }


def extract_core_questions(questions_text):
    """
    解析生成的面试问题文本
    返回完整的题目块（包含背景和所有追问），交给前端去解析结构
    """
    try:
        # 优化正则：匹配【问题X】开始直到下一个问题或文件结束
        # DOTALL模式下 . 匹配换行
        # 我们寻找 【问题\d+】作为分隔符

        # 简单清洗
        text = questions_text.strip()

        # 使用 split 切分
        # pattern: (【问题\d+】.*?)(?=【问题\d+】|$)
        # 但是 re.split 会更好

        matches = re.finditer(r"【问题\d+】", text)
        indices = [m.start() for m in matches]
        indices.append(len(text))

        core_questions = []
        for i in range(len(indices) - 1):
            start = indices[i]
            end = indices[i+1]
            segment = text[start:end].strip()

            # 去除 【问题X】 标题本身，或者保留?
            # 前端 parseQuestionContent 期望的是内容。
            # 通常 【问题X】是标题，后面是内容 (考察点...) Context ... - 追问

            # 去除标题 【问题\d+】
            segment_content = re.sub(r"^【问题\d+】", "", segment).strip()

            if segment_content:
                core_questions.append(segment_content)

        if not core_questions:
             # Fallback logic if regex finds nothing
             logger.warning("Regex split found no questions, returning full text or fallback")
             # Try simple line split check
             if "【问题" not in text:
                 return [text] # Just return as one chunk to be safe?

             core_questions = [
                "请解释Python中可变对象（如list, dict）和不可变对象（如int, str, tuple）的区别，并举例说明在函数参数传递时的行为差异？\n- 追问：深拷贝和浅拷贝的区别？",
                "请描述Flask应用从接收HTTP请求到返回响应的完整生命周期？\n- 追问：请求上下文和程序上下文的作用？"
            ]

        return core_questions
    except Exception as e:
        logger.warning(f"解析问题失败：{str(e)}，使用默认问题列表")
        return [
            "请解释Python中可变对象（如list, dict）和不可变对象（如int, str, tuple）的区别，并举例说明在函数参数传递时的行为差异？",
            "请描述Flask应用从接收HTTP请求到返回响应的完整生命周期，以及请求上下文和程序上下文的作用？",
            "请比较SQLAlchemy ORM和原生SQL的优缺点，以及N+1查询问题的产生原因和解决方法？",
            "请解释Python的GIL（全局解释器锁），并说明多线程和多进程的适用场景？",
            "请说明Flask蓝图（Blueprint）的作用、使用场景和注册方式？"
        ]


def run_interactive_interview(user_info):
    """
    交互式面试流程：生成问题 → 用户逐题回答 → 基于回答生成实时评估
    优化：明确显示「考察点+完整题干」，增加交互提示
    """
    try:
        logger.info(f"开始交互式面试流程，候选人信息：{user_info}")

        # 1. 先生成面试问题
        base_result = run_interview_flow(user_info)
        core_questions = extract_core_questions(base_result["interview_questions"])

        # 2. 交互式获取用户回答（优化交互体验）
        user_answers = {}
        print("\n" + "=" * 80)
        print("Python技术交互式面试 - 共{}道题".format(len(core_questions)))
        print("提示：请逐题回答，输入完成后按回车提交（可输入'跳过'跳过当前题）")
        print("=" * 80 + "\n")

        for idx, question in enumerate(core_questions, 1):
            # 清晰显示题号+完整题干
            print(f"\n【第{idx}题/{len(core_questions)}题】")
            print(f"题目：{question}")
            # 接收用户输入（支持跳过）
            answer = input("你的回答：").strip()
            if answer.lower() == "跳过":
                answer = "候选人跳过此题"
            elif not answer:
                answer = "候选人未作答"
            user_answers[f"第{idx}题"] = {
                "question": question,
                "answer": answer
            }
            # 每答完一题给出反馈
            print(f"已保存你的回答，继续下一题...\n")

        # 3. 基于用户回答生成实时评估
        logger.info("调用 DeepSeek 生成实时回答评估...")
        eval_prompt = f"""
        你是资深Python技术面试官，请基于以下信息对候选人的回答进行专业评估：
        1. 候选人背景：{user_info}
        2. 面试问题及回答：{user_answers}
        3. 评估要求：
           - 逐题点评：每道题从「准确性、完整性、深度」3个维度点评（0-10分）
           - 整体评分：给出总分（0-100分）和能力等级（初级/中级/待提升）
           - 改进建议：针对回答中的不足，给出具体的改进方向和学习建议
           - 格式要求：分段清晰，语言简洁，适合候选人直接查看
        """
        realtime_evaluation = call_deepseek(
            eval_prompt,
            fallback="""
【实时面试评估结果】
1. 逐题点评：
   - 第1题（Python可变/不可变对象）：准确性8分，完整性7分，深度6分。
     点评：回答基本正确，但未举例说明函数参数传递时的行为差异，缺乏实战案例支撑。
   - 第2题（Flask请求生命周期）：准确性7分，完整性6分，深度5分。
     点评：仅了解基本概念，未说明上下文的生命周期和销毁时机。
   - 第3题（SQLAlchemy N+1问题）：准确性6分，完整性5分，深度4分。
     点评：听说过该问题，但无法说明具体解决方法（如joinedload/eagerload）。
   - 第4题（Python GIL）：准确性7分，完整性6分，深度5分。
     点评：知道GIL的存在，但不了解I/O密集型任务中多线程的有效性。
   - 第5题（Flask蓝图）：准确性5分，完整性4分，深度3分。
     点评：仅知道概念，无法说明具体使用场景和注册方式。

2. 整体评分：68分
   能力等级：初级（符合1年Python开发经验水平）

3. 改进建议：
   - 补充Python核心概念的实战案例，避免仅停留在理论层面；
   - 深入学习Flask高级特性（蓝图、上下文、中间件），尝试重构现有项目；
   - 系统学习数据库优化知识，重点掌握ORM性能调优和慢查询分析。
            """
        )

        # 4. 整合最终结果并输出
        final_result = {
            "user_info": user_info,
            "core_questions": core_questions,
            "user_answers": user_answers,
            "realtime_evaluation": realtime_evaluation,
            "full_questions": base_result["interview_questions"],
            "evaluation_report": base_result["evaluation_report"],
            "mentor_suggestion": base_result["mentor_suggestion"],
            "status": "success"
        }

        logger.info("交互式面试流程执行完成！")

        # 输出最终评估结果
        print("\n" + "=" * 80)
        print("你的实时面试评估结果")
        print("=" * 80)
        print(realtime_evaluation)
        print("=" * 80 + "\n")

        return final_result

    except Exception as e:
        logger.error(f"交互式面试流程失败：{str(e)}", exc_info=True)
        # 异常兜底
        error_msg = f"交互式面试异常：{str(e)}"
        print(f"\n{error_msg}，已切换为模拟评估结果\n")
        return {
            "user_info": user_info,
            "core_questions": extract_core_questions(get_mock_interview_questions()),
            "user_answers": {},
            "realtime_evaluation": error_msg + "\n" + get_mock_evaluation_report(),
            "full_questions": get_mock_interview_questions(),
            "evaluation_report": get_mock_evaluation_report(),
            "mentor_suggestion": get_mock_mentor_suggestion(),
            "status": "error",
            "error_msg": str(e)
        }


# 测试代码（支持两种模式）
if __name__ == "__main__":
    # 测试用户信息（可修改为自定义信息）
    test_user_info = "姓名：张三，应聘岗位：Python开发工程师，工作经验：1年，熟悉Flask框架和MySQL数据库，无大型项目经验"

    # 选择运行模式
    print("=" * 80)
    print("AI Python模拟面试系统")
    print("=" * 80)
    print("请选择运行模式：")
    print("1 - 非交互式（仅生成问题/评估/建议）")
    print("2 - 交互式（问答+实时评估）")
    mode = input("输入数字选择模式（默认1）：").strip() or "1"

    if mode == "1":
        # 非交互式模式
        result = run_interview_flow(test_user_info)
        print("\n" + "=" * 80)
        print("【Python技术面试问题】")
        print(result["interview_questions"])

        print("\n" + "=" * 80)
        print("【技术能力评估报告】")
        print(result["evaluation_report"])

        print("\n" + "=" * 80)
        print("【能力提升指导建议】")
        print(result["mentor_suggestion"])
        print("=" * 80 + "\n")

    elif mode == "2":
        # 交互式模式
        result = run_interactive_interview(test_user_info)
        show_full = input("是否查看完整的评估报告和提升建议？(y/n，默认n)：").strip() or "n"
        if show_full.lower() == "y":
            print("\n" + "=" * 80)
            print("【完整技术能力评估报告】")
            print(result["evaluation_report"])

            print("\n" + "=" * 80)
            print("【详细能力提升指导建议】")
            print(result["mentor_suggestion"])
            print("=" * 80 + "\n")
    else:
        print("无效模式，默认运行非交互式模式...")
        result = run_interview_flow(test_user_info)
        print("\n" + "=" * 80)
        print("【Python技术面试问题】")
        print(result["interview_questions"])
        print("=" * 80 + "\n")