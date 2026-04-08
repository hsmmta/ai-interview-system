# JTR_WSTZ
# @Time : 2026/3/23 19:04
# @Author :无题
# @Version: 未知
# @IDE:未知
# @Project : mock_interview
import os
import json
import random
import requests
import time
import webbrowser
from utils.kb_loader import load_questions, filter_by_job
from crewai import LLM
from crewai import Agent
from crewai import Task
from crewai.flow.flow import Flow, start, listen, router, or_
from dotenv import load_dotenv
load_dotenv()


llm = LLM(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# 面试官智能体
def create_interviewer_agent(interviewee_info="", job_position="AI算法工程师"):
    interviewer_agent = Agent(
        role=f"{job_position}岗位面试官",
        goal=f"""
        1.根据面试者的简历内容进行暖场，并礼貌地邀请面试者进行自我介绍；
        2.结合面试者的简历内容和自我介绍，总结出面试者的姓名、求职岗位名称、兴趣特长以及参加的项目或者比赛的名称，如果简历内容和自我介绍中某点都没有提及，你会继续询问来获取相关信息；
        3.结合面试者的简历内容和自我介绍，提取出不少于12个可以用于提问的关键词（主要是项目或者比赛中用到的技术栈）；
        4.根据上一题的题目和面试者回答情况（第一问除外），选择是否要进行追问；
        5.从提取到的关键词中选择一个没用过的关键词，先到相关岗位题库中寻找语义相近的题干，然后结合面试者简历内容和问答上下文（如果是追问），生成符合自然语境的题目；
        """,
        backstory=f"""
        1.你是资深{job_position}岗位面试官，有10年以上面试经验，非常熟悉该岗位的所有面试考点；
        2.你会从面试者简历中、自我介绍以及对问题的回答中准确提取你需要询问的关键词，并且视当前面试节奏选择需要的关键词进行提问；
        3.你深谙面试技巧，能够灵活控制面试节奏，当面试者回答模糊的时候，可以视情况追问施加压力，或者跳过追问开启下一个关键词的提问，当面试者回答清晰的时候，一定会寻找关键词进行追问；
        4.正常情况你对面试者都是礼貌用语，但是如果面试者非常不尊重你或者说了很多与你提问无关的内容，你会非常严厉地制止并提出批评；
        5.你拥有该岗位需要的题库，在提问时你会根据你选择的关键词去题库里面寻找语义相近的问题，并且结合面试者简历内容和问答上下文灵活调整题干，使所有的提问自然不突兀；
        6.对于指定的输出格式，你都严格执行，不会输出额外内容；
        7.你需要面试的都是应届生，所以会考虑他们缺乏实际工作经验，问题场景主要集中在校园而不是公司；
        8.你会根据面试者的简历丰富程度（参加比赛项目的多少、绩点高低、获得荣誉多少等影响因素）来初步决定提问问题的难度。
        9.你会根据面试者的回答情况灵活决定下一题的难度，比如上一题面试者回答非常好，那么下一题可以稍微难一点，相反如果面试者回答得比较差，下一题你会问简单一点的题目。
        """,
        verbose=False,  # 是否允许生成思考日志
        allow_delegation=False,  # 是否允许将任务指派给其他智能体
        llm=llm
    )
    return interviewer_agent


class interview_init(Flow):
    def __init__(self, agent, interviewee_info, post_job):
        super().__init__()
        self.agent = agent
        self.interviewee_info = interviewee_info
        self.post_job = post_job
        data = load_questions("action.json", "action")
        bank1 = filter_by_job(data, self.post_job)
        data = load_questions("project_experience.json", "project_experience")
        bank2 = filter_by_job(data, self.post_job)
        data = load_questions("scene.json", "scene")
        bank3 = filter_by_job(data, self.post_job)
        data = load_questions("technology.json", "technology")
        bank4 = filter_by_job(data, self.post_job)
        coding_bank_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'library', 'question_library', 'coding_bank.json')
        with open(coding_bank_path, 'r', encoding='utf-8') as f:
            coding_question_bank = json.load(f)["coding"]
        self.state.update({
            "history": [],  # 问答记录
            "follow_count": 3,  # 当前可追问次数
            "coding_result": None,
            "action_question_bank": bank1,
            "project_experience_question_bank": bank2,
            "scene_question_bank": bank3,
            "technology_question_bank": bank4,
            "coding_bank": coding_question_bank,
            "used_question": [3, 3, 3, 3],  # 剩余行为题、场景题、项目深挖题、技术题数量
            "coding_cnt": 3,
            "coding_history": [],
            "coding_ans": []
        })

    @start()
    def interview_init_task1(self):
        result = self.agent.llm.call(f"""
        1.从面试者简历信息{self.interviewee_info}中提取有效信息，并进行语义分割；
        2.根据语义分割的结果严格输出json结构化信息，不要任何解释、不要markdown、不要代码块、不要多余文字，只返回JSON字符串,简历信息里没有的字段忽略
        格式如下：
        "name": "张三",
        "post_position": "xxx",
        "projects_or_matches": ["xxx", "xxx"],
        "skills": ["机器学习与深度学习", "计算机视觉"],
        "honors": ["xxx", "xxx"],
        "courses": ["数据结构", "计算机组成原理"],
        "tech_stack":["TensorFlow","PyTorch"]
        """
        )
        self.interviewee_info = json.loads(result)

    @listen(interview_init_task1)
    def interview_init_task2(self):
        result = self.agent.llm.call(f"""
        1.根据面试者的初步信息{self.interviewee_info}进行暖场，并邀请面试者做自我介绍；
        2.如果初步信息里缺少项目经历和比赛经历以及相关技术栈，要委婉提醒面试者在自我介绍里补充相关信息；
        3.语言要自然贴切，能够让面试者放松下来，快速进入状态。
        """
        ).strip()
        print(result)

    @listen(interview_init_task2)
    def interview_init_task3(self):
        self_introduction = input("请输入:")
        result = self.agent.llm.call(f"""
        1.根据面试者的自我介绍{self_introduction}进一步补全{self.interviewee_info};
        2.严格输出json结构化信息，不要任何解释、不要markdown、不要代码块、不要多余文字，只返回JSON字符串
        格式如下：
        "name": "张三",
        "post_position": "xxx",
        "projects_or_matches": ["xxx", "xxx"],
        "skills": ["机器学习与深度学习", "计算机视觉", "自然语言处理"],
        "honors": ["xxx", "xxx"],
        "courses": ["数据结构", "计算机组成原理"],
        "tech_stack":["TensorFlow","PyTorch"]
        """
        ).strip()
        self.interviewee_info = json.loads(result)
        print("下面我们正式开始面试，请您做好准备")

    @router(interview_init_task3)
    def interview_task1(self):
        if any(x > 0 for x in self.state["used_question"]):
            return "interview_task2"
        else:
            return "interview_task6"

    def interview_task2(self):
        cur_list = []
        for i in range(4):
            if self.state["used_question"][i] > 0:
                cur_list.append(i)
        result = random.choice(cur_list)
        self.state["used_question"][result] -= 1
        ans = ""
        if result == 0:
            ans = "行为题"
        elif result == 1:
            ans = "项目深挖题"
        elif result == 2:
            ans = "场景题"
        else:
            ans = "技术题"
        return ans

    @listen(interview_task2)
    def interview_task3(self, chose):
        result = self.agent.llm.call(f"""
        1.你拥有下面四个题库：行为题库{self.state["action_question_bank"]}、场景题库{self.state["scene_question_bank"]}、项目深挖题库{self.state["project_experience_question_bank"]}和技术题库{self.state["technology_question_bank"]}
        2.现在需要选择{chose}题型的题目，你需要去对应题库里找一道题，然后结合面试者的简历信息{self.interviewee_info}出一道题，要求难度适中，语义连贯、语气自然。
        3.所选题目不得与之前的题目{self.state["history"]}重复。
        4.牢记你现在的身份是面试官，你现在要考察面试者，只需要返回你想要考察的题目内容，不需要返回出题思路等乱七八糟的东西。
        """).strip()
        cnt = 12 - sum(self.state["used_question"])
        print(f"第{cnt}道题:{result}")
        self.state["history"].append(result)
        self.state["follow_count"] = 3

    def interview_task5(self):
        last_answer = self.state["history"][-1]
        raw_words = last_answer.replace("，", " ").replace("。", " ").split()
        keywords = []
        for word in raw_words:
            if len(word) >= 2 and word not in ["我觉得", "大概", "可能", "就是"]:
                keywords.append(word)
        keywords = list(set(keywords))[:5]

        full_question_bank = []
        full_question_bank.extend(self.state["action_question_bank"])
        full_question_bank.extend(self.state["scene_question_bank"])
        full_question_bank.extend(self.state["project_experience_question_bank"])
        full_question_bank.extend(self.state["technology_question_bank"])

        match_list = []
        for q_item in full_question_bank:
            q_text = str(q_item.get("content", ""))
            if any(kw in q_text for kw in keywords) and q_text not in str(self.state["history"]):
                match_list.append(q_text)

        final_candidate = list(set(match_list))[:3]
        result = self.agent.llm.call(f"""
            1.目前根据面试者上一轮回答筛选出下面几道匹配的题目{final_candidate},你从中挑选一题结合语境进行润色
            并最终返回要追问的题目；
            2.你选择的题目不能是{self.state["history"]}里面出现过的问题，且你追问的题目要结合面试者上一轮的回答{last_answer}，语气自然不突兀；
            3.牢记你现在的身份是面试官，你现在要对面试者进行追问，返回你要追问的题目内容即可，不需要出题思路等其他乱七八糟的东西；
            4.比如这样追问：你刚才回答中提到xxx，你能对xxx里面参数具体是怎么调的详细展开说明吗？
            """).strip()
        print(f"追问:{result}")
        self.state["history"].append(result)

    @router(interview_task3)  # 出题后立即进入答题
    @listen(interview_task5)
    def interview_task4(self):
        answer = input("请回答:")
        self.state["history"].append(answer)
        if self.state["follow_count"] <= 0:
            return "interview_task2"
        result = self.agent.llm.call(f"""
            1.根据{self.state["history"][-2]}的提问内容和面试者的回答{answer}来决定是否需要追问，
            如果面试者对上一个问题回答得非常清晰，且回答中有关键词可以提问，则返回单个字符'Y'，反之如果
            面试者回答得非常模糊，不能达到你的预期，则你根据当前面试节奏选择是否要追问，整个面试问答都在{self.state["history"]}里面，
            如果选择不追问，返回单个字符'N'；
            2.若当前可追问次数小于等于0，则强制选择不追问；
            3.预期输出：Y 或者 N ,不得有任何多余的输出。
            """).strip()
        if result == 'Y':
            self.state["follow_count"] -= 1
            return "interview_task5"
        else:
            return "interview_task2"

    def interview_task6(self):
        print("全部简答题回答结束,下面进入限时编程题环节，请做好准备")
        result = self.agent.llm.call(f"""
        1.根据面试者前面简答题的回答情况{self.state["history"]}来决定编程题第一题的难度，
        若前面面试者回答非常出色，则第一题编程题出难题，若前面简答题回答得很差，则出简单题，如果回答得一般，则出中等难度题；
        2.输出仅从下面选其一:简单/中等/困难，不得存在其他任何多余字符。
        """).strip()
        if result == "简单":
            bank = [item for item in self.state["coding_bank"] if item["difficulty"]=="简单"]
        elif result == "中等":
            bank = [item for item in self.state["coding_bank"] if item["difficulty"]=="中等"]
        else:
            bank = [item for item in self.state["coding_bank"] if item["difficulty"] == "困难"]
        selected_question = random.choice(bank)
        self.state["coding_history"].append(selected_question)
        self.state["coding_cnt"] -= 1
        try:
            requests.post(
                "http://127.0.0.1:8000/set_question",  # 单发一题接口
                json={"question": selected_question},
                timeout=2
            )
        except:
            print("编程后端未启动，跳过发送")
        webbrowser.open("http://127.0.0.1:8000/index.html")

    @listen(interview_task6)
    def interview_task7(self):
        while True:
            try:
                status = requests.get("http://127.0.0.1:8000/get_coding_status").json()
                if status["finished"]:
                    break
            except:
                pass
            time.sleep(2)
        if self.state["coding_cnt"] > 0:
            return "interview_task8"
        else:
            return "interview_task9"

    def interview_task8(self):
        status = requests.get("http://127.0.0.1:8000/get_coding_status").json()
        code = requests.get("http://127.0.0.1:8000/get_user_code").json()["user_code"]
        cost_sec = status["cost_seconds"]
        result = self.agent.llm.call(f"""
        1.根据面试者上一题的用时{cost_sec}和完成的代码{code}来决定下一题的难度，如果完成得非常好，则返回困难，
        完成度一般返回中等，完成度很差返回简单；
        2.返回内容只能为：简单/中等/困难，不得有任何多余内容。
        """).strip()
        if result == "简单":
            bank = [item for item in self.state["coding_bank"] if item["difficulty"]=="简单"]
        elif result == "中等":
            bank = [item for item in self.state["coding_bank"] if item["difficulty"]=="中等"]
        else:
            bank = [item for item in self.state["coding_bank"] if item["difficulty"] == "困难"]
        used_ids = [q["id"] for q in self.state["coding_history"]]
        available_bank = [item for item in bank if item["id"] not in used_ids]
        selected_question = random.choice(available_bank)
        self.state["coding_history"].append(selected_question)
        self.state["coding_ans"].append(code)
        self.state["coding_cnt"] -= 1
        try:
            requests.post(
                "http://127.0.0.1:8000/set_question",  # 单发一题接口
                json={"question": selected_question},
                timeout=2
            )
        except:
            print("编程后端未启动，跳过发送")
        return "interview_task7"

    def interview_task9(self):
        print("所有编程题已回答完毕，面试结束")



