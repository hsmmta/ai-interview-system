from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import sys
import json
import random
import time
import psutil
import uvicorn
import judge_answers
import os
import uuid

app = FastAPI(title="Python 模拟面试系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    qid: str
    code: str
    action: str
    used_time: float = 0

# 全局共享（面试官设置）
current_question = {}
coding_status = {
    "submitted": False,
    "timeout": False,
    "finished": False,
    "user_code": "",
    "start_time": 0,
    "cost_seconds": 0
}

# ---------------------- 题目设置（面试官用） ----------------------
@app.post("/set_question")
def set_question(data: dict):
    global current_question, coding_status
    current_question = data.get("question", {})
    coding_status = {
        "submitted": False,
        "timeout": False,
        "finished": False,
        "user_code": "",
        "start_time": time.time(),
        "cost_seconds": 0
    }
    return {"status": "ok", "msg": "题目已下发，状态重置"}

@app.get("/get_current_question")
def get_current_question():
    return current_question

@app.get("/get_coding_status")
def get_coding_status():
    return coding_status

# ---------------------- 状态 ----------------------
@app.post("/reset_coding_status")
def reset_coding_status():
    global coding_status
    coding_status = {
        "submitted": False,
        "timeout": False,
        "finished": False,
        "user_code": "",
        "start_time": time.time(),
        "cost_seconds": 0
    }
    return {"status": "reset"}

@app.post("/user_submit")
def user_submit(req: CodeRequest):
    global coding_status
    now = time.time()
    coding_status["submitted"] = True
    coding_status["finished"] = True
    coding_status["user_code"] = req.code
    coding_status["cost_seconds"] = round(now - coding_status["start_time"], 1)
    return {"status": "submitted"}

@app.post("/user_timeout")
def user_timeout():
    global coding_status
    now = time.time()
    coding_status["timeout"] = True
    coding_status["finished"] = True
    coding_status["cost_seconds"] = round(now - coding_status["start_time"], 1)
    return {"status": "timeout"}

# ---------------------- 判题 ----------------------
def get_ans_func(qid):
    return getattr(judge_answers, f"ans_{qid}", None)

def generate_test_cases(qid, count=10):
    func = get_ans_func(qid)
    cases = []
    if not func:
        return cases
    if qid == "0001":
        for _ in range(count):
            n = random.randint(2,10)
            nums = [random.randint(-50,50) for _ in range(n)]
            i,j = random.sample(range(n),2)
            target = nums[i]+nums[j]
            cases.append({"input":[nums,target],"expect":func(nums,target)})
    elif qid == "0002":
        for _ in range(count):
            arr = [random.randint(-50,50) for _ in range(random.randint(0,12))]
            cases.append({"input":[arr],"expect":func(arr)})
    elif qid == "0003":
        for _ in range(count):
            nums1 = sorted([random.randint(-10,20) for _ in range(random.randint(1,6))])
            nums2 = sorted([random.randint(-10,20) for _ in range(random.randint(1,6))])
            cases.append({"input":[nums1,nums2],"expect":func(nums1,nums2)})
    elif qid == "0004":
        for n in random.sample([1,2,3,4,5,6,7,8,9,10],count):
            cases.append({"input":[n],"expect":func(n)})
    elif qid == "0005":
        for _ in range(count):
            arr = [random.randint(-20,20) for _ in range(random.randint(3,12))]
            cases.append({"input":[arr],"expect":func(arr)})
    elif qid == "0006":
        samples = ["abcabcbb","bbbbb","pwwkew","a","au","abba","dvdf","tmmzuxt"]
        for s in samples[:count]:
            cases.append({"input":[s],"expect":func(s)})
    elif qid == "0007":
        samples = [[-1,0,1,2,-1,-4],[],[0,0,0],[1,2,3],[-2,0,1,1,2]]
        for nums in samples[:count]:
            cases.append({"input":[nums],"expect":func(nums)})
    elif qid == "0010":
        samples = [([1,3],[2]),([1,2],[3,4]),([],[1]),([2],[])]
        for a,b in samples[:count]:
            cases.append({"input":[a,b],"expect":func(a,b)})
    elif qid == "0011":
        samples = [("aa","a"),("aa","a*"),("ab",".*"),("aab","c*a*b")]
        for s,p in samples:
            cases.append({"input":[s,p],"expect":func(s,p)})
    elif qid == "0012":
        samples = [")()())","(()","","()()","((()))","())()()"]
        for s in samples:
            cases.append({"input":[s],"expect":func(s)})
    return cases

def run_code_safe(code: str, qid: str):
    uid = str(uuid.uuid4())
    user_file = f"user_{uid}.py"
    judge_file = f"judge_{uid}.py"
    try:
        with open(user_file, "w", encoding="utf-8") as f:
            f.write(code)
        cases = generate_test_cases(qid, 10)
        if not cases:
            return {"error": "无效题目ID"}

        judge_code = f'''
import json, time
import sys
sys.path.insert(0, ".")
from {user_file[:-3]} import solution
cases = {json.dumps(cases)}
start = time.time()
result = []
for idx, case in enumerate(cases):
    try:
        args = case["input"]
        exp = case["expect"]
        out = solution(*args)
        result.append({{"case":idx+1,"input":args,"your_output":out,"expect":exp,"passed":out==exp}})
    except Exception as e:
        result.append({{"case":idx+1,"error":str(e),"passed":False}})
end = time.time()
print(json.dumps({{"result":result,"exec_time":round(end-start,3)}}))
'''
        with open(judge_file, "w", encoding="utf-8") as f:
            f.write(judge_code)

        process = subprocess.Popen(
            [sys.executable, judge_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        max_mem = 0
        try:
            p = psutil.Process(process.pid)
            for _ in range(20):
                max_mem = max(max_mem, p.memory_info().rss // 1024)
                time.sleep(0.05)
        except:
            pass

        try:
            out, err = process.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "执行超时（8秒）"}

        if err:
            return {"error": err.strip()}
        data = json.loads(out.strip())
        data["memory"] = max_mem
        return data
    except Exception as e:
        return {"error": str(e)}
    finally:
        for f in [user_file, judge_file]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

@app.post("/api/code")
def api_code(req: CodeRequest):
    if not req.qid:
        return {"error": "缺少题目ID"}
    return run_code_safe(req.code, req.qid)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)