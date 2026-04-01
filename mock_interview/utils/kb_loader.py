import json
from pathlib import Path


def load_questions(file_name="action.json", name="action"):
    base_dir = Path(__file__).parent.parent
    kb_path = base_dir / "library" / "question_library" / file_name

    if not kb_path.exists():
        print(f"题库文件不存在: {kb_path}")
        return None

    try:
        with open(kb_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None
    except OSError as e:
        print(f"文件读取错误: {e}")
        return None

    return data.get(name, [])


def load_knowledge(file_name="ai_algorithm_engineer", name="exam_point.json"):
    base_dir = Path(__file__).parent.parent
    kb_path = base_dir / "library" / "knowledge_library" / file_name / name

    if not kb_path.exists():
        print(f"题库文件不存在: {kb_path}")
        return None

    try:
        with open(kb_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None
    except OSError as e:
        print(f"文件读取错误: {e}")
        return None

    return data["knowledge_base"]["knowledge"]


def filter_by_job(questions, job_name="AI算法工程师"):
    def match(post):
        if isinstance(post, list):
            return job_name in post or "通用" in post
        return post in (job_name, "通用")
    return [q for q in questions if match(q.get("applicable_post"))]


if __name__ == "__main__":
    data = load_knowledge("ai_algorithm_engineer", "exam_point.json")
    print(data)