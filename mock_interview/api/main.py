from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import importlib.util

# 项目根目录: .../mock_interview
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 强制加载根目录 crew.py，避免导入到 crew/ 包
CREW_FILE = os.path.join(PROJECT_ROOT, "crew.py")
if not os.path.exists(CREW_FILE):
    raise RuntimeError(f"crew.py not found: {CREW_FILE}")

spec = importlib.util.spec_from_file_location("crew_bridge", CREW_FILE)
if spec is None or spec.loader is None:
    raise RuntimeError("Failed to create module spec for crew.py")

crew = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crew)

# 启动即自检，便于快速定位
if not hasattr(crew, "run_interview_flow"):
    raise RuntimeError(
        f"Loaded module from {CREW_FILE}, but run_interview_flow not found. "
        f"Available attrs: {[x for x in dir(crew) if x.startswith('run_') or x.startswith('extract_')][:20]}"
    )

app = FastAPI(
    title="AI Python模拟面试系统",
    description="提供面试题生成、交互问答、评分评估接口",
    version="1.0"
)


class UserInfoRequest(BaseModel):
    name: str
    position: str
    experience: str
    skills: str


class BaseResponse(BaseModel):
    status: str
    message: str
    data: dict = {}


@app.get("/health")
async def health():
    return {
        "ok": True,
        "project_root": PROJECT_ROOT,
        "crew_file": CREW_FILE,
        "has_run_interview_flow": hasattr(crew, "run_interview_flow"),
        "has_extract_core_questions": hasattr(crew, "extract_core_questions"),
    }


@app.post("/api/interview/generate", response_model=BaseResponse)
async def generate_interview_result(request: UserInfoRequest):
    try:
        user_info = (
            f"姓名：{request.name}，"
            f"应聘岗位：{request.position}，"
            f"工作经验：{request.experience}，"
            f"技能：{request.skills}"
        )
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


@app.post("/api/interview/interactive/init", response_model=BaseResponse)
async def init_interactive_interview(request: UserInfoRequest):
    try:
        user_info = (
            f"姓名：{request.name}，"
            f"应聘岗位：{request.position}，"
            f"工作经验：{request.experience}，"
            f"技能：{request.skills}"
        )
        base_result = crew.run_interview_flow(user_info)
        core_questions = crew.extract_core_questions(base_result["interview_questions"])

        return BaseResponse(
            status="success",
            message="交互式面试初始化成功",
            data={
                "core_questions": core_questions,
                "full_questions": base_result["interview_questions"]
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


@app.post("/api/interview/interactive/evaluate", response_model=BaseResponse)
async def evaluate_user_answers(request: dict):
    try:
        user_info = request.get("user_info")
        user_answers = request.get("user_answers")

        if not user_info or not user_answers:
            raise ValueError("缺少用户信息或回答数据")

        eval_prompt = f"""
你是资深Python技术面试官，请基于以下信息对候选人的回答进行专业评估：
1. 候选人背景：{user_info}
2. 面试问题及回答：{user_answers}
3. 评估要求：
   - 逐题点评：每题从准确性、完整性、深度三个维度评分（0-10）
   - 整体评分：总分（0-100）和能力等级（初级/中级/待提升）
   - 改进建议：给出具体改进方向和学习建议
"""
        realtime_evaluation = crew.call_deepseek(
            eval_prompt,
            fallback="""
【实时评估结果】
1. 逐题点评：回答基础正确，但深度和实战案例不足。
2. 整体评分：70分，能力等级：初级。
3. 改进建议：加强项目实践与原理深挖。
"""
        )

        return BaseResponse(
            status="success",
            message="实时评估生成成功",
            data={"realtime_evaluation": realtime_evaluation}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"评估失败：{str(e)}",
                "data": {}
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8010, reload=True, log_level="info")
