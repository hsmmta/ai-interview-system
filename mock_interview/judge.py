
import json, time
from user_code import solution

cases = [{"input": [[-1, 24], 23], "expect": [0, 1]}, {"input": [[14, -19, -30, 39, 7, 13, 27, 47, -9, -8], -39], "expect": [2, 8]}, {"input": [[-13, 12, -44], -1], "expect": [0, 1]}, {"input": [[2, -3, 13, 5, -18, 32, -48, -21, -25], -35], "expect": [2, 6]}, {"input": [[-28, 2, 17], 19], "expect": [1, 2]}, {"input": [[3, -8, 20, -8, -28, 40, -20, 25, 0, -7], -35], "expect": [4, 9]}, {"input": [[5, 39, -5, -5, 9, -4, -15, -35], 34], "expect": [1, 2]}, {"input": [[-47, -37, -18, 7, -28], -84], "expect": [0, 1]}, {"input": [[18, 2, -14, -26, -30, -50], -12], "expect": [1, 2]}, {"input": [[-18, -40], -58], "expect": [0, 1]}]
start = time.time()
result = []

for idx, case in enumerate(cases):
    try:
        args = case["input"]
        exp = case["expect"]
        out = solution(*args)
        result.append({
            "case": idx+1,
            "input": args,
            "your_output": out,
            "expect": exp,
            "passed": out == exp
        })
    except Exception as e:
        result.append({
            "case": idx+1,
            "error": str(e),
            "passed": False
        })

end = time.time()
print(json.dumps({
    "result": result,
    "exec_time": round(end-start, 3)
}))
