import os
from typing import Any, Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

app = FastAPI(title="AI Assistant Bridge", version="2.0.0")


class GenerateQuestionsRequest(BaseModel):
    session_id: str
    recruit_type: str = Field(..., description="campus or social")
    direction: str
    question_count: int = Field(15, ge=1, le=50)
    keywords: Optional[List[str]] = None


class QuestionItem(BaseModel):
    id: int
    type: str
    question: str


class GenerateQuestionsResponse(BaseModel):
    session_id: str
    questions: List[QuestionItem]


class EvaluateRequest(BaseModel):
    session_id: str
    questions: List[QuestionItem]
    answers: List[str]
    extra_context: Optional[Dict[str, Any]] = None


class QuestionEvaluation(BaseModel):
    id: int
    score: int
    max_score: int
    comment: str
    reference_answer: str


class EvaluateResponse(BaseModel):
    session_id: str
    total_score: int
    max_total_score: int
    overall_comment: str
    details: List[QuestionEvaluation]


class MockInterviewHttpAdapter:
    def __init__(self) -> None:
        self.enabled = os.getenv("USE_CREWAI", "false").lower() == "true"
        self.base_url = os.getenv("MOCK_INTERVIEW_BASE_URL", "http://127.0.0.1:8010").rstrip("/")
        self.timeout_sec = int(os.getenv("MOCK_INTERVIEW_TIMEOUT_SEC", "60"))

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "mode": "http",
            "base_url": self.base_url,
            "timeout_sec": self.timeout_sec,
        }

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, json=payload, timeout=self.timeout_sec)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected response type from {url}")
        return data

    def generate_questions(self, req: GenerateQuestionsRequest) -> List[QuestionItem]:
        if not self.enabled:
            raise RuntimeError("USE_CREWAI is false")

        # Adapt your website fields -> mock_interview UserInfoRequest
        position = req.direction
        experience = "校招" if req.recruit_type.lower() == "campus" else "社招"
        skills = "、".join(req.keywords or [req.direction])

        data = self._post(
            "/api/interview/interactive/init",
            {
                "name": "候选人",
                "position": position,
                "experience": experience,
                "skills": skills,
            },
        )

        # Expect shape: {status,message,data:{core_questions:[...],full_questions:"..."}}
        payload = data.get("data", {}) if isinstance(data.get("data", {}), dict) else {}
        core_questions = payload.get("core_questions", [])

        if not isinstance(core_questions, list) or not core_questions:
            raise RuntimeError("mock_interview returned empty core_questions")

        # Build fixed count, 10 short + 5 coding style
        target = min(max(req.question_count, 1), 50)
        selected = core_questions[:target]
        result: List[QuestionItem] = []
        for i, q in enumerate(selected, start=1):
            q_type = "short_answer" if i <= 10 else "coding"
            result.append(QuestionItem(id=i, type=q_type, question=str(q)))
        return result

    def evaluate(self, req: EvaluateRequest) -> EvaluateResponse:
        if not self.enabled:
            raise RuntimeError("USE_CREWAI is false")
        if len(req.questions) != len(req.answers):
            raise HTTPException(status_code=400, detail="questions 与 answers 数量不一致")

        user_answers = {}
        for q, a in zip(req.questions, req.answers):
            user_answers[f"Q{q.id}"] = {"question": q.question, "answer": a}

        data = self._post(
            "/api/interview/interactive/evaluate",
            {
                "user_info": req.extra_context or {"source": "java-jsp-web"},
                "user_answers": user_answers,
            },
        )

        payload = data.get("data", {}) if isinstance(data.get("data", {}), dict) else {}
        evaluation_text = str(payload.get("realtime_evaluation", "")).strip()

        details: List[QuestionEvaluation] = []
        total = 0
        for q, ans in zip(req.questions, req.answers):
            score = min(10, max(1, len(ans.strip()) // 30)) if ans.strip() else 0
            total += score
            details.append(
                QuestionEvaluation(
                    id=q.id,
                    score=score,
                    max_score=10,
                    comment="已结合答题内容生成点评，请查看整体评价。",
                    reference_answer="参考答案由AI端生成（当前接口返回文本评价）。",
                )
            )

        return EvaluateResponse(
            session_id=req.session_id,
            total_score=total,
            max_total_score=len(req.questions) * 10,
            overall_comment=evaluation_text if evaluation_text else "已完成评分，请继续复盘。",
            details=details,
        )


adapter = MockInterviewHttpAdapter()


def mock_generate(req: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    questions: List[QuestionItem] = []
    for i in range(1, req.question_count + 1):
        q_type = "short_answer" if i <= 10 else "coding"
        questions.append(
            QuestionItem(
                id=i,
                type=q_type,
                question=f"[{req.direction}] 第{i}题（{q_type}）：请回答与{req.recruit_type}招聘相关的问题。",
            )
        )
    return GenerateQuestionsResponse(session_id=req.session_id, questions=questions)


def mock_evaluate(req: EvaluateRequest) -> EvaluateResponse:
    if len(req.questions) != len(req.answers):
        raise HTTPException(status_code=400, detail="questions 与 answers 数量不一致")

    details: List[QuestionEvaluation] = []
    total = 0
    for q, ans in zip(req.questions, req.answers):
        score = min(10, max(1, len(ans.strip()) // 20)) if ans.strip() else 0
        total += score
        details.append(
            QuestionEvaluation(
                id=q.id,
                score=score,
                max_score=10,
                comment="回答结构基本完整，建议补充边界条件与优化思路。",
                reference_answer=f"这是第{q.id}题的参考要点示例（后续由AI生成）。",
            )
        )

    return EvaluateResponse(
        session_id=req.session_id,
        total_score=total,
        max_total_score=len(req.questions) * 10,
        overall_comment="整体基础尚可，建议加强项目细节表达和编码规范。",
        details=details,
    )


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "adapter_status": adapter.status()}


@app.post("/api/v1/questions/generate", response_model=GenerateQuestionsResponse)
def generate_questions(req: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    try:
        questions = adapter.generate_questions(req)
        return GenerateQuestionsResponse(session_id=req.session_id, questions=questions)
    except Exception:
        return mock_generate(req)


@app.post("/api/v1/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    if len(req.questions) != len(req.answers):
        raise HTTPException(status_code=400, detail="questions 与 answers 数量不一致")
    try:
        return adapter.evaluate(req)
    except Exception:
        return mock_evaluate(req)
