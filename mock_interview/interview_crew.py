import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.kb_loader import load_knowledge
from utils.llm_config import call_deepseek


def extract_core_questions(questions):
    if not questions:
        return []
    core = [q.strip() for q in questions.split("\n") if q.strip()][:5]
    return core


def run_interview_flow(exp_job):
    try:
        # full_kb = load_knowledge_base()
        job_keywords = ["AI绠楁硶宸ョ▼甯?"]
        user_job = exp_job  # 榛樿宀椾綅
        # matched_kb = retrieve_by_job(full_kb, job_name=user_job)
        # 格式化知识点为Prompt文本
        # kb_prompt_text = format_for_prompt(matched_kb)
        kb_prompt_text = str(load_knowledge("ai_algorithm_engineer", "exam_point.json"))
        work_experience = "1年"

        # ====================== 鏋勯€犲嚭棰楶rompt锛堟暣鍚堢煡璇嗗簱锛?======================
        question_prompt = f"""
你是资深AI算法工程师面试官，请严格基于以下信息生成面试题：

### 候选人工作年限信息
{work_experience}

### 知识库参考内容
{kb_prompt_text}

### 出题要求
1. 题目必须基于上述知识库内容；
2. 共生成5道题，其中核心知识题3道、基础知识题2道；
3. 每道题标注考察知识点，格式：【考察点：XXX】+ 题目内容；
4. 题目需贴合AI算法工程师岗位要求，符合真实面试场景；
5. 结构化输出，每道题单独成行，无多余解释。
6.根据应试者回答实时调整题目难度，如当前难度题回答不了或者回答错误可以下一题难度适当降低
"""

        # ====================== 调用大模型生成题目 ======================
        interview_questions = call_deepseek(
            prompt=question_prompt
        )


        final_result = {
            "interview_questions": interview_questions,
            "status": "success"
        }

        return final_result

    except Exception as e:
        return {
            "status": "error",
            "error_msg": str(e)
        }


def run_interactive_interview(user_name, exp_job, wk_experience):
    try:
        print(f"你好，{user_name}!")
        print("下面我们开始面试")
        base_result = run_interview_flow(exp_job)
        core_questions = extract_core_questions(base_result["interview_questions"])
        user_answers = {}
        print("首先是简答题 - 共{}道题".format(len(core_questions)))
        print("提示：请逐题回答，输入完成后按回车提交（可输入'跳过'跳过当前题）")
        print("=" * 80 + "\n")

        for idx, question in enumerate(core_questions, 1):
            print(f"\n【第{idx}题/{len(core_questions)}题】")
            print(f"题目：{question}")
            answer = input("你的回答：").strip()
            if answer.lower() == "跳过":
                answer = "候选人跳过此题"
            elif not answer:
                answer = "候选人未作答"
            user_answers[f"第{idx}题"] = {
                "question": question,
                "answer": answer
            }
            print(f"已保存你的回答，继续下一题...\n")

        logger.info("调用 DeepSeek 生成实时回答评估...")
        eval_prompt = f"""
        你是资深{exp_job}面试官，请基于以下信息对候选人的回答进行专业评估：
        1. 候选人已有工作年限：{wk_experience}
        2. 面试问题及回答：{user_answers}
        3. 评估要求：
           - 逐题点评：每道题从「准确性、完整性、深度」3个维度点评（0-10分）
           - 整体评分：给出总分（0-100分）和能力等级（初级/中级/待提升）
           - 改进建议：针对回答中的不足，给出具体的改进方向和学习建议
           - 格式要求：分段清晰，语言简洁，适合候选人直接查看
        """
        realtime_evaluation = call_deepseek(
            eval_prompt
        )

        # 4. 整合最终结果并输出
        final_result = {
            "user_name": user_name,
            "core_questions": core_questions,
            "user_answers": user_answers,
            "realtime_evaluation": realtime_evaluation,
            "full_questions": base_result["interview_questions"],
            "status": "success"
        }

        print("简答题作答完成")
        print("下面开始编程题测试")

        print("\n" + "=" * 80)
        print("你的实时面试评估结果")
        print("=" * 80)
        print(realtime_evaluation)
        print("=" * 80 + "\n")

        return final_result

    except Exception as e:
        logger.error(f"交互式面试流程失败：{str(e)}", exc_info=True)
        error_msg = f"交互式面试异常：{str(e)}"
        print(f"\n错误消息如下：{error_msg}\n")
        return {
            "user_name": user_name,
            "user_answers": {},
            "status": "error",
            "error_msg": str(e)
        }


if __name__ == "__main__":
    test_user_info = "AI算法工程师，1年工作经验，熟悉Transformer架构和基础深度学习知识"
    print("\n" + "=" * 80)
    print("欢迎使用面试模拟与能力培养系统！")
    print("下面请根据提示输入个人基本信息")
    name = input("请输入姓名:")
    job = input("请输入您想要面试的岗位名称:")
    work_experience = input("请输入您目前有多少年的工作经验:")
    print("是否现在开始面试？")
    ans = input("请输入(y/n)")
    while True:
        if ans.upper() == 'N':
            print("感谢您的使用，再见！")
            break
        elif ans.upper() == 'Y':
            result = run_interactive_interview(name, job, work_experience)
            print("面试流程结束，系统自动退出")
            break
        else:
            print("无效的输入")
            ans = input("请重新输入:")
