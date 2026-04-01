# JTR_WSTZ
# @Time : 2026/3/23 19:04
# @Author :无题
# @Version: δ֪
# @IDE:δ֪
# @Project : mock_interview
import os
import json
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
        self.state.update({
            "history": [],  # 问答记录
            "follow_count": 3,  # 当前可追问次数
            "action_question_bank": bank1,
            "project_experience_question_bank": bank2,
            "scene_question_bank": bank3,
            "technology_question_bank": bank4,
            "used_question":[3, 3, 3, 3]  # 剩余行为题、场景题、项目深挖题、技术题数量
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
        result = self.agent.llm.call(f"""
        1.{self.state["used_question"]}为四种题目类型的可出剩余题数，从左到右分别是行为题、场景题、项目深挖题和技术题的剩余题数；
        2.根据该列表选择随机选择一个不为0的题目类型，并返回该题目类型，不得返回任何多余的东西；
        3.返回值只能四选一："行为题"/"场景题"/"项目深挖题"/"技术题"。
        """).strip()
        if result == "行为题":
            self.state["used_question"][0] -= 1
        elif result == "场景题":
            self.state["used_question"][1] -= 1
        elif result == "项目深挖题":
            self.state["used_question"][2] -= 1
        elif result == "技术题":
            self.state["used_question"][3] -= 1
        else:
            result = "技术题"
            self.state["used_question"][3] -= 1
        return result

    @listen(interview_task2)
    def interview_task3(self, chose):
        result = self.agent.llm.call(f"""
        1.你拥有下面四个题库：行为题库{self.state["action_question_bank"]}、场景题库{self.state["scene_question_bank"]}、项目深挖题库{self.state["project_experience_question_bank"]}和技术题库{self.state["technology_question_bank"]}
        2.现在需要选择{chose}题型的题目，你需要去对应题库里找一道题，然后结合面试者的信息{self.interviewee_info}出一道题，要求难度适中，语义连贯、语气自然。
        3.所选题目不得与之前的题目{self.state["history"]}重复。
        """).strip()
        cnt = 12 - sum(self.state["used_question"])
        print(f"第{cnt}道题:{result}")
        self.state["history"].append(result)
        self.state["follow_count"] = 3

    def interview_task5(self):
        result = self.agent.llm.call(f"""
        1.你将根据面试者的最新回答{self.state["history"]}进行追问，你可以选择一个或者两个面试者回答中的关键词去对应题库中
        寻找合适的题目，如果题库中没有匹配关键词的问题，你可以自己出一道难度合适的题结合语境追问面试者；
        2.你可以参考的题库如下：
        行为题库{self.state["action_question_bank"]}、场景题库{self.state["scene_question_bank"]}、项目深挖题库{self.state["project_experience_question_bank"]}和技术题库{self.state["technology_question_bank"]}
        """).strip()
        print(f"追问:{result}")
        self.state["history"].append(result)

    @router(interview_task3)
    @listen(interview_task5)
    def interview_task4(self):
        answer = input("请回答:")
        self.state["history"].append(answer)
        result = self.agent.llm.call(f"""
        1.根据{self.state["history"]}最新的问题(列表倒数第二个)和面试者的回答{answer}，以及当前可追问次数{self.state["follow_count"]}是否大于0来决定是否需要追问，
        如果面试者对上一个问题回答得非常清晰，或者回答中有关键词可以提问，则返回单个字符'Y'，反之如果
        面试者回答得非常模糊，不能达到你的预期，则你根据当前面试节奏选择是否要追问，整个面试问答都在{self.state["history"]}里面，
        如果选择不追问，返回单个字符'N'；
        2.若当前可追问次数小于等于0，则强制选择不追问；
        3.预期输出：Y 或者 N ,不得有任何多余的输出。
        """).strip()
        if result == 'Y':
            self.state["follow_count"] -= 1
            return "interview_task5"
        elif result == 'N':
            return "interview_task2"
        else:
            return "interview_task2"

    def interview_task6(self):
        print("全部简答题回答结束")












