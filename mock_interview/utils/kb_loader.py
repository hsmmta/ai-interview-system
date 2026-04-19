import json
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
frontend_env = Path(__file__).parent.parent.parent / "frontend" / ".env"
if frontend_env.exists():
    load_dotenv(dotenv_path=frontend_env)

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
    """
    Fetch knowledge base from Neo4j instead of local JSON files.
    Map file_name (e.g., ai_algorithm_engineer) to Job title in Neo4j.
    """
    neo4j_uri = os.getenv("VITE_NEO4J_URI") or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("VITE_NEO4J_USER") or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("VITE_NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD", "111111")

    # Map file name to job name for Neo4j query
    job_map = {
        "ai_algorithm_engineer": "AI算法工程师",
        "ai_data_dev": "AI数据开发工程师",
        "common": "通用"
    }
    job_title = job_map.get(file_name, file_name)

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    knowledge_list = []

    try:
        with driver.session() as session:
            # Match Tech connected to the Job, and optional Questions connected to the Tech
            query = """
            MATCH (j:Job {name: $job_title})<-[:REQUIRE]-(t:Tech)
            OPTIONAL MATCH (t)<-[:TESTS]-(q:Question)
            RETURN t.name AS tech, collect(q.content) AS questions
            """
            result = session.run(query, job_title=job_title)

            for record in result:
                tech = record["tech"]
                questions = record["questions"]

                knowledge_point = {
                    "theme": tech,
                    "example_questions": questions if questions else []
                }
                knowledge_list.append(knowledge_point)

    except Exception as e:
        print(f"Neo4j 查询错误: {e}")
    finally:
        driver.close()

    return knowledge_list


def filter_by_job(questions, job_name="AI算法工程师"):
    def match(post):
        if isinstance(post, list):
            return job_name in post or "通用" in post
        return post in (job_name, "通用")
    return [q for q in questions if match(q.get("applicable_post"))]


if __name__ == "__main__":
    data = load_knowledge("ai_algorithm_engineer", "exam_point.json")
    print(data)