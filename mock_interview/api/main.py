# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import interview_crew as crew

# 初始化FastAPI应用
app = FastAPI(
    title="AI Python模拟面试系统",
    description="提供Python技术面试问题生成、交互式问答、能力评估的API服务",
    version="1.0"
)

# 定义请求体模型
class UserInfoRequest(BaseModel):
    name: str = ""
    position: str = ""
    experience: str = ""
    skills: str = ""

class InteractiveInitRequest(BaseModel):
    post_position: str = ""
    resume_text: str = ""

class InteractiveSubmitRequest(BaseModel):
    session_id: str
    answer: str

# 定义响应模型
class BaseResponse(BaseModel):
    status: str  # success/error
    message: str  # 提示信息
    data: dict = {}  # 业务数据
    is_finished: bool = False  # 额外给submit接口用的标志
    session_id: str = ""

# 全局内存字典，用于保持会话状态
SESSIONS = {}

# 接口1：非交互式生成面试结果（仅供测试使用）
@app.post("/api/interview/generate", response_model=BaseResponse)
async def generate_interview_result(request: UserInfoRequest):
    try:
        # 拼接用户信息字符串
        user_info = f"姓名：{request.name}，应聘岗位：{request.position}，工作经验：{request.experience}，熟悉{request.skills}"
        # 调用crew.py中的run_interview_flow函数（修复后）
        result = crew.run_interview_flow(user_info)
        return BaseResponse(
            status="success",
            message="面试结果生成成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"生成失败：{str(e)}",
                "data": {}
            }
        )


# 接口2：交互式面试初始化（实际使用）
@app.post("/api/interview/interactive/init", response_model=BaseResponse)
async def init_interactive_interview(request: InteractiveInitRequest):
    try:
        user_info = f"应聘岗位：{request.post_position}，简历内容：{request.resume_text}"
        # 先生成问题（调用crew.py的核心函数）
        base_result = crew.run_interview_flow(user_info)
        # 提取核心问题（调用crew.py的extract_core_questions函数）
        core_questions = crew.extract_core_questions(base_result.get("interview_questions", ""))

        import uuid
        new_session_id = str(uuid.uuid4())

        # 调用大模型生成开场白和暖场
        prompt = f"你是资深面试官，面对候选人（背景：{user_info}），请给出一句亲切的暖场白，并礼貌地邀请他做个自我介绍。只要一句话，不要有多余解释。"
        warm_up_message = crew.call_deepseek(prompt, fallback="你好，欢迎参加今天的面试，不要紧张。能先简单地做一个自我介绍吗？")

        # 记录会话初始状态
        SESSIONS[new_session_id] = {
            "core_questions": core_questions,
            "current_q_idx": -1,  # -1 代表还在寒暄自我介绍阶段
            "follow_up_count": 0, # 当前追问次数
            "history": [{"role": "interviewer", "content": warm_up_message}]
        }

        return BaseResponse(
            status="success",
            message=warm_up_message,
            session_id=new_session_id,
            data={
                "core_questions": core_questions,
                "full_questions": base_result.get("interview_questions", "")
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"初始化失败：{str(e)}",
                "data": {}
            }
        )


# 新增接口：提交用户回答并获取下一题
@app.post("/api/interview/interactive/submit", response_model=BaseResponse)
async def submit_answer(request: InteractiveSubmitRequest):
    try:
        session_data = SESSIONS.get(request.session_id)
        if not session_data:
            raise ValueError("未找到对应的面试会话状态，请刷新重试！")

        # 记录用户回答
        session_data["history"].append({"role": "user", "content": request.answer})

        # 如果是自我介绍阶段，结束自我介绍，直接进入第一大题
        if session_data["current_q_idx"] == -1:
            session_data["current_q_idx"] = 0
            session_data["follow_up_count"] = 0

            if len(session_data["core_questions"]) > 0:
                next_msg = f"好的，感谢你的自我介绍！下面我们正式开始。第一道题：{session_data['core_questions'][0]}"
            else:
                next_msg = "好的，感谢。那么你能详述一下你的项目经历吗？"

            session_data["history"].append({"role": "interviewer", "content": next_msg})
            return BaseResponse(
                status="success",
                message=next_msg,
                is_finished=False,
                data={"current_q_idx": session_data["current_q_idx"], "follow_up_count": session_data["follow_up_count"]}
            )

        else:
            # 如果在正常题目阶段，根据当前追问次数决定追问还是进入下一题
            # 最多追问 3 次
            if session_data["follow_up_count"] < 3:
                session_data["follow_up_count"] += 1

                # 动态生成追问
                history_text = "\n".join([f"{item['role']}: {item['content']}" for item in session_data["history"][-3:]])
                prompt = f"""
你是面试官。针对你刚提的问题和候选人的回答进行追问（当前是第 {session_data["follow_up_count"]} 次追问）。
对话上下文：
{history_text}

要求：
1. 深入候选人回答的细节，提出一个具体的追问。
2. 如果候选人回答不知道、含糊或错误，可以适当施加压力或抛出提示后再追问。
3. 严格保持口语化，不要解释，只返回追问的话语。
"""
                next_msg = crew.call_deepseek(prompt, fallback="能针对这块内容的底层原理或踩过的坑，再详细说一说吗？")
                next_msg = "[追问] " + next_msg # 为了让侧边栏状态更明显
                session_data["history"].append({"role": "interviewer", "content": next_msg})
                return BaseResponse(
                    status="success",
                    message=next_msg,
                    is_finished=False,
                    data={"current_q_idx": session_data["current_q_idx"], "follow_up_count": session_data["follow_up_count"]}
                )

            else:
                # 进入下一个核心大题
                session_data["current_q_idx"] += 1
                session_data["follow_up_count"] = 0

                if session_data["current_q_idx"] < len(session_data["core_questions"]):
                    # 还有题目
                    next_msg = f"好的，关于这块我们先聊到这。下一道大题：{session_data['core_questions'][session_data['current_q_idx']]}"
                    session_data["history"].append({"role": "interviewer", "content": next_msg})
                    return BaseResponse(
                        status="success",
                        message=next_msg,
                        is_finished=False,
                        data={"current_q_idx": session_data["current_q_idx"], "follow_up_count": session_data["follow_up_count"]}
                    )
                else:
                    # 所有问题问完
                    return BaseResponse(
                        status="success",
                        message="面试已全部结束，请点击左侧“进入编程测试”完成剩余环节。",
                        is_finished=True,
                        data={"current_q_idx": session_data["current_q_idx"], "follow_up_count": session_data["follow_up_count"]}
                    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"提交出错：{str(e)}",
                "data": {}
            }
        )


# 接口3：提交用户回答，生成实时评估
@app.post("/api/interview/interactive/evaluate", response_model=BaseResponse)
async def evaluate_user_answers(request: dict):
    try:
        session_id = request.get("session_id")
        user_info = request.get("user_info")
        user_answers = request.get("user_answers")
        coding_results = request.get("coding_results", {})

        formatted_history = []
        if session_id and session_id in SESSIONS:
            session_data = SESSIONS[session_id]
            formatted_history = session_data.get("history", [])
        else:
            if not user_info or not user_answers:
                raise ValueError("缺少 session_id 或完整的用户信息和回答数据")
            if isinstance(user_answers, dict):
                for k, v in user_answers.items():
                    formatted_history.append({"role": "interviewer", "content": v.get("question", "")})
                    formatted_history.append({"role": "user", "content": v.get("answer", "")})
            elif isinstance(user_answers, list):
                formatted_history = user_answers

        # 将结构化的对话历史转为文本格式，以便输入给大模型
        history_text = ""
        for msg in formatted_history:
            role_name = "面试官" if msg.get("role") == "interviewer" else "候选人"
            history_text += f"{role_name}: {msg.get('content')}\n"

        coding_text = ""
        for q_id, code_ans in coding_results.items():
            coding_text += f"编程题 {q_id} 回答:\n{code_ans}\n"

        eval_prompt = f"""
        你是资深Python技术面试官，也是岗位的综合能力评估师。
        请基于以下信息对候选人的全程表现（包括问答和编程题）进行专业评估：
        1. 候选人背景：{user_info}
        2. 问答环节记录：\n{history_text}
        3. 编程环节记录：\n{coding_text}

        评估要求：
        - 逐题点评：针对主要面试问题和编程题，点评其准确性、完整性、深度和解决思路。
        - 整体评分：给出各能力维度（如核心软素质、专业技术等）的得分（满分10分），并给出能力竞争力评级（如S/A/B/C/D）。
        - 改进建议：针对发现的不足（如代码风格、架构思考、基础知识盲区），给出具体可落地的短期和长期改进培养方案。

        输出格式要求：
        【评分结果】
        核心软素质模块：
        - 问题解决能力：X.X分
        - 沟通与团队协作能力：X.X分
        - 抗压能力：X.X分
        - 时间管理能力：X.X分
        - 自主学习能力：X.X分
        - 自我认知与职业规划能力：X.X分
        专业技术模块：
        - 数据结构：X.X分
        - 算法设计：X.X分
        - 计算机基础：X.X分
        - 编程语言核心：X.X分
        - 数据库与缓存：X.X分
        - 工程实践与运维：X.X分
        【综合评价】
        竞争力等级：S/A/B/C/D
        （具体的评语）
        【短板分析】
        （具体的短板分析）
        【培养方案】
        （短期和长期的改进培养方案）
        """

        realtime_evaluation = crew.call_deepseek(
            eval_prompt,
            fallback="评估服务发生异常，未能返回完整的打分报告，请稍后再试或检查日志。"
        )

        return BaseResponse(
            status="success",
            message="实时评估生成成功",
            data={
                "realtime_evaluation": realtime_evaluation,
                "history": formatted_history
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"评估失败：{str(e)}",
                "data": {}
            }
        )


# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 热重载
        log_level="info"
    )