# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import uuid
import json
import importlib.util
from typing import Dict, Any, List
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
CREW_FILE = os.path.join(PROJECT_ROOT, "interview_crew.py")
if not os.path.exists(CREW_FILE):
    raise RuntimeError(f"interview_crew.py not found: {CREW_FILE}")
spec = importlib.util.spec_from_file_location("crew_bridge", CREW_FILE)
crew = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crew)
app = FastAPI(
    title="AI Python",
    description="API",
    version="1.0"
)
class UserInfoRequest(BaseModel):
    name: str = ""
    position: str = ""
    experience: str = ""
    skills: str = ""
    sessionId: int = 0
    interviewType: str = ""
    direction: str = ""
    questionCount: int = 15

class ChatInitRequest(BaseModel):
    post_position: str
    resume_text: str = ""

class ChatSubmitRequest(BaseModel):
    session_id: str
    answer: str

class ChatResponse(BaseModel):
    status: str
    session_id: str = ""
    message: str = ""
    is_finished: bool = False
    data: dict = {}

SESSION_STORE: Dict[str, Any] = {}

def get_session(session_id: str):
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSION_STORE[session_id]

@app.post("/api/interview/interactive/init", response_model=ChatResponse)
async def init_interactive(req: ChatInitRequest):
    try:
        from crew.interviewer import create_interviewer_agent, Flow, load_questions, filter_by_job

        session_id = str(uuid.uuid4())

        resume_text = req.resume_text
        if not resume_text or len(resume_text) < 10:
            # Fallback to local PDF if resume text not provided or too short
            try:
                import pdfplumber
                pdf_path = os.path.join(PROJECT_ROOT, "测试用简历.pdf")
                if os.path.exists(pdf_path):
                    with pdfplumber.open(pdf_path) as pdf:
                        resume_text = ""
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                resume_text += text + "\n"
                else:
                    resume_text = "AI算法工程师候选人，熟练掌握基本知识"
            except Exception as e:
                resume_text = f"简历读取失败. {str(e)}"

        agent = create_interviewer_agent(interviewee_info=resume_text, job_position=req.post_position)

        # We simulate the flow steps since we can't block on input()
        # interview_init_task1
        result1 = agent.llm.call(f"""
        1.从面试者简历信息{resume_text}中提取有效信息，并进行语义分割；
        2.根据语义分割的结果严格输出json结构化信息，不要任何解释、不要markdown、不要多余文字，只返回JSON字符串
        """)
        import re
        json_str = result1.strip()
        json_str = re.sub(r'^```json', '', json_str)
        json_str = re.sub(r'```$', '', json_str).strip()
        try:
            interviewee_info = json.loads(json_str)
        except:
            interviewee_info = {"raw": json_str}

        # interview_init_task2
        result2 = agent.llm.call(f"""
        1.根据面试者的初步信息{interviewee_info}进行暖场，并邀请面试者做自我介绍；
        2.如果初步信息里缺少项目经历和比赛经历以及相关技术栈，要委婉提醒面试者在自我介绍里补充相关信息；
        3.语言要自然贴切，能够让面试者放松下来，快速进入状态。
        """).strip()

        bank1 = filter_by_job(load_questions("action.json", "action"), req.post_position)
        bank2 = filter_by_job(load_questions("project_experience.json", "project_experience"), req.post_position)
        bank3 = filter_by_job(load_questions("scene.json", "scene"), req.post_position)
        bank4 = filter_by_job(load_questions("technology.json", "technology"), req.post_position)

        SESSION_STORE[session_id] = {
            "agent": agent,
            "interviewee_info": interviewee_info,
            "post_position": req.post_position,
            "history": [],
            "follow_count": 3,
            "used_question": [3, 3, 3, 3],
            "banks": [bank1, bank3, bank2, bank4],
            "state": "waiting_intro", # Next expected input
            "question_count": 0
        }

        return ChatResponse(status="success", session_id=session_id, message=result2)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/interactive/submit", response_model=ChatResponse)
async def submit_interactive(req: ChatSubmitRequest):
    try:
        session = get_session(req.session_id)
        agent = session["agent"]
        state = session["state"]

        if state == "waiting_intro":
            # interview_init_task3
            result = agent.llm.call(f"""
            1.根据面试者的自我介绍{req.answer}进一步补全{session["interviewee_info"]}
            2.严格输出json结构化信息，只返回JSON字符串
            """).strip()
            import re
            json_str = result.strip()
            json_str = re.sub(r'^```json', '', json_str)
            json_str = re.sub(r'```$', '', json_str).strip()
            try:
                session["interviewee_info"] = json.loads(json_str)
            except:
                pass

            session["state"] = "asking_question"
            # Proceed to ask first question immediately
            return await generate_next_question(req.session_id)

        elif state == "asking_question" or state == "following_up":
            # record answer
            session["history"].append(req.answer)

            # decide follow up
            result = agent.llm.call(f"""
            根据最新问题及回答{req.answer}决定是否追问。如果清晰有关键词且次数>0，返回'Y'，模糊或节奏需要换题或次数<=0则'N'。只返回Y或N。
            当前剩余追问次数：{session['follow_count']}
            """).strip()

            if result == 'Y' and session["follow_count"] > 0:
                session["follow_count"] -= 1
                # interview_task5
                follow_q = agent.llm.call(f"""
                根据最新回答{session['history']}进行追问，结合题库或自己出题。
                """).strip()
                session["history"].append(follow_q)
                session["state"] = "following_up"
                return ChatResponse(status="success", session_id=req.session_id, message=follow_q)
            else:
                # Next main question
                return await generate_next_question(req.session_id)
        else:
            return ChatResponse(status="error", message="Unknown state")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

async def generate_next_question(session_id: str):
    session = get_session(session_id)
    agent = session["agent"]
    used = session["used_question"]

    if not any(x > 0 for x in used):
        session["state"] = "finished"
        return ChatResponse(status="success", session_id=session_id, message="全部简答题回答结束", is_finished=True)

    result = agent.llm.call(f"剩余题数={used} (行为,场景,项目深挖,技术)。返回其中一个不为0的类型名，只能返回'行为题'/'场景题'/'项目深挖题'/'技术题'之一。").strip()

    if result == "行为题" and used[0] > 0: used[0] -= 1
    elif result == "场景题" and used[1] > 0: used[1] -= 1
    elif result == "项目深挖题" and used[2] > 0: used[2] -= 1
    elif result == "技术题" and used[3] > 0: used[3] -= 1
    else:
        for i in range(4):
            if used[i] > 0:
                used[i] -= 1
                break

    chose = result
    q = agent.llm.call(f"""
    从{chose}题库中，结合信息{session['interviewee_info']}出一道难度适中、语义连贯的题。不许与历史{session['history']}重复。
    """).strip()

    session["history"].append(q)
    session["follow_count"] = 3
    session["state"] = "asking_question"
    session["question_count"] += 1

    return ChatResponse(status="success", session_id=session_id, message=f"第{session['question_count']}道题: " + q)

@app.post("/api/interview/interactive/evaluate", response_model=ChatResponse)
async def evaluate_interactive(req: dict):
    try:
        session_id = req.get("session_id")
        session = get_session(session_id)
        post_position = session["post_position"]
        from crew.appraiser import create_evaluator_agent, create_evaluation_task
        from crew.educator import create_mentor_agent, create_mentor_task
        from crewai import Crew
        from utils.kb_loader import load_knowledge

        file_name = "ai_algorithm_engineer" if post_position == "AI算法工程师" else "ai_data_dev"
        data1 = load_knowledge(file_name, "exam_point.json") or []
        data2 = load_knowledge(file_name, "tech_stack.json") or []
        data3 = load_knowledge("common", "tech_stack.json") or []
        kb_full = list(data1) + list(data2) + list(data3)

        evaluate_agent = create_evaluator_agent(post_position)
        eval_task = create_evaluation_task(agent=evaluate_agent, interview_content=str(session["history"]), interviewee_info=str(session["interviewee_info"]), knowledge_base=str(kb_full), post_type=post_position)

        crew1 = Crew(agents=[evaluate_agent], tasks=[eval_task])
        report = str(crew1.kickoff())

        mentor_agent = create_mentor_agent(post_position)
        mentor_task = create_mentor_task(agent=mentor_agent, evaluation_report=report, post_type=post_position)
        crew2 = Crew(agents=[mentor_agent], tasks=[mentor_task])
        training_program = str(crew2.kickoff())

        return ChatResponse(status="success", session_id=session_id, data={
            "report": report,
            "training_program": training_program,
            "interviewee_info": session["interviewee_info"],
            "history": session["history"]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/generate")
async def generate_interview_result(request: UserInfoRequest):
    try:
        user_info = f"姓名：{request.name}，应聘岗位：{request.position}，工作经验：{request.experience}，技能：{request.skills}"
        result = crew.run_interview_flow(request.position)

        with open("generation_debug.log", "w", encoding="utf-8") as f:
            f.write(f"Result: {result}\n")

        return {
            "status": "success",
            "message": "生成结果成功",
            "data": result,
            "questions": crew.extract_core_questions(result.get("interview_questions", ""))
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        with open("generation_error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
            f.write(f"\nRequest: {request}\n")
        raise HTTPException(status_code=500, detail={"status": "error", "message": f"生成失败：{str(e)}", "data": {}})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8010, reload=True, log_level="info")
