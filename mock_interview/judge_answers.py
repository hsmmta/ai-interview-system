# JTR_WSTZ
# @Time : 2026/4/6 15:28
# @Author :无题
# @Version: 未知
# @IDE:未知
# @Project : mock_interview

# ==============================
# 编程题标准答案集合
# 与 coding_bank.json 题目一一对应
# ==============================

# 0001 两数之和
def ans_0001(nums, target):
    dic = {}
    for i, val in enumerate(nums):
        if target - val in dic:
            return [dic[target - val], i]
        dic[val] = i
    return []


# 0002 反转列表
def ans_0002(arr):
    return arr[::-1]


# 0003 合并两个有序数组
def ans_0003(nums1, nums2):
    merged = sorted(nums1 + nums2)
    return merged


# 0004 爬楼梯
def ans_0004(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b


# 0005 最大子数组和（Kadane算法）
def ans_0005(nums):
    cur = max_sub = nums[0]
    for num in nums[1:]:
        cur = max(num, cur + num)
        max_sub = max(max_sub, cur)
    return max_sub


# 0006 无重复字符的最长子串
def ans_0006(s):
    char_map = {}
    left = 0
    max_len = 0
    for right, c in enumerate(s):
        if c in char_map and char_map[c] >= left:
            left = char_map[c] + 1
        char_map[c] = right
        max_len = max(max_len, right - left + 1)
    return max_len


# 0007 三数之和
def ans_0007(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        l, r = i+1, n-1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s == 0:
                res.append([nums[i], nums[l], nums[r]])
                while l < r and nums[l] == nums[l+1]:
                    l += 1
                while l < r and nums[r] == nums[r-1]:
                    r -= 1
                l += 1
                r -= 1
            elif s < 0:
                l += 1
            else:
                r -= 1
    return res


# 0008 二叉树中序遍历
def ans_0008(root):
    res = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)
        res.append(node.val)
        inorder(node.right)
    inorder(root)
    return res


# 0009 合并K个升序链表
def ans_0009(lists):
    import heapq
    dummy = ListNode(0)
    cur = dummy
    heap = []
    for idx, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, idx, node))
    while heap:
        val, idx, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))
    return dummy.next


# 0010 寻找两个正序数组的中位数
def ans_0010(nums1, nums2):
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2 == 1:
        return float(merged[n//2])
    else:
        return (merged[n//2 - 1] + merged[n//2]) / 2.0


# 0011 正则表达式匹配
def ans_0011(s: str, p: str) -> bool:
    dp = [[False]*(len(p)+1) for _ in range(len(s)+1)]
    dp[0][0] = True
    for j in range(1, len(p)+1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-2]
    for i in range(1, len(s)+1):
        for j in range(1, len(p)+1):
            if p[j-1] == '.' or p[j-1] == s[i-1]:
                dp[i][j] = dp[i-1][j-1]
            elif p[j-1] == '*':
                dp[i][j] = dp[i][j-2]
                if p[j-2] == '.' or p[j-2] == s[i-1]:
                    dp[i][j] |= dp[i-1][j]
    return dp[len(s)][len(p)]


# 0012 最长有效括号
def ans_0012(s):
    stack = [-1]
    max_len = 0
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                max_len = max(max_len, i - stack[-1])
    return max_len


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right