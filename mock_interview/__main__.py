# JTR_WSTZ
# @Time : 2026/3/24 9:11
# @Author :无题
# @Version: δ֪
# @IDE:δ֪
# @Project : mock_interview
from crewai import Crew
from crew.interviewer import create_interviewer_agent, interview_init
from crew.appraiser import create_evaluator_agent, create_evaluation_task
from crew.educator import create_mentor_agent,create_mentor_task
from crewai import Crew
from utils.kb_loader import load_knowledge
import pdfplumber


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


if __name__ == "__main__":
    post_position = input("请输入你的求职意向岗位名称:")
    interviewee_info = extract_text_from_pdf("测试用简历.pdf")
    interview_agent = create_interviewer_agent(interviewee_info=interviewee_info)
    flow = interview_init(agent=interview_agent, interviewee_info=interviewee_info, post_job="AI算法工程师")
    flow.kickoff()
    interviewee_info = flow.interviewee_info
    history = flow.state["history"]
    file_name = ""
    if post_position == "AI算法工程师":
        file_name = "ai_algorithm_engineer"
    elif post_position == "AI数据开发工程师":
        file_name = "ai_data_dev"

    data1 = load_knowledge(file_name, "exam_point.json")
    data2 = load_knowledge(file_name, "tech_stack.json")
    data3 = load_knowledge("common", "tech_stack.json")
    data4 = load_knowledge("common", "tech_stack.json")
    data1.append(data2)
    data1.append(data3)
    data1.append(data4)

    evaluate_agent = create_evaluator_agent(post_position)
    evaluation_task = create_evaluation_task(
        agent=interview_agent,
        interview_content=history,  # 完整面试对话文本
        interviewee_info=interviewee_info,  # 候选人的结构化信息
        post_type=post_position,
        knowledge_base=data1
    )

    crew = Crew(
        agents=[evaluate_agent],
        tasks=[evaluation_task],
    )
    report = crew.kickoff()
    print(f"评估报告如下：{report}")  # 输出评估报告

    educator_agent = create_mentor_agent(post_position)
    educate_task = create_mentor_task(
        agent=educator_agent,
        evaluation_report=report,
        post_type=post_position
    )

    crew = Crew(
        agents=[educator_agent],
        tasks=[educate_task],
    )
    training_program = crew.kickoff()
    print(f"培养方案如下:{training_program}")


