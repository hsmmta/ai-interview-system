def solution(nums, target):
    dic = {}
    for i, val in enumerate(nums):
        if target - val in dic:
            return [dic[target - val], i]
        dic[val] = i
    return []