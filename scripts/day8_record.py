# 从 Python 标准库 collections 中导入 Counter
# Counter 是“计数器”工具，可以自动统计元素出现的次数
#
# 例如：
# Counter(["a", "b", "a"])
# 结果：
# {"a": 2, "b": 1}
from collections import Counter

# 导入 math 数学库
# 后面会用到：
# - math.exp()  -> e 的指数运算
# - math.log()  -> 对数运算
import math


# =========================
# 1. 准备示例文本
# =========================

# 参考文本（Reference）
# 通常表示“标准答案”
#
# split() 的作用：
# 按空格切分字符串
#
# 例如：
# "a b c".split()
# -> ["a", "b", "c"]
#
# 所以这里：
# ref =
# ["the", "cat", "is", "on", "the", "mat"]
ref = "the cat is on the mat".split()

# 候选文本（Candidate）
# 通常表示“模型生成结果”
cand = "the cat sat on the mat".split()


# =========================
# 2. 生成 n-gram
# =========================


def ngrams(tokens, n):
    """
    生成 n-gram（连续 n 个 token 的片段）

    参数：
    - tokens: 分词后的列表
    - n: n-gram 的 n

    返回：
    一个列表，每个元素是 tuple（元组）

    例子：

    tokens =
    ["the", "cat", "is", "on"]

    n = 2

    返回：
    [
        ("the", "cat"),
        ("cat", "is"),
        ("is", "on")
    ]
    """

    # range(len(tokens) - n + 1)
    # 的作用是控制滑动窗口不要越界
    #
    # 例如：
    # len(tokens)=4
    # n=2
    #
    # range(4 - 2 + 1)
    # -> range(3)
    # -> 0,1,2
    #
    # 即：
    # tokens[0:2]
    # tokens[1:3]
    # tokens[2:4]

    return [
        # tuple(...) 把列表转换成元组
        #
        # 为什么用 tuple？
        #
        # 因为：
        # list 不能作为 Counter/dict 的 key
        # tuple 可以
        #
        # 例如：
        # ["the", "cat"] ❌
        # ("the", "cat") ✅
        tuple(tokens[i : i + n])
        # i 是滑动窗口起点
        for i in range(len(tokens) - n + 1)
    ]


# =========================
# 3. 计算 ROUGE-N
# =========================


def rouge_n(ref, cand, n):
    """
    计算 ROUGE-N（Recall 口径）

    ROUGE 的核心思想：
    看参考答案中的 n-gram
    有多少被候选文本覆盖到了

    公式：

    overlap / reference_total
    """

    # 统计参考文本中的 n-gram 出现次数
    #
    # 例如：
    # Counter([
    #   ("the","cat"),
    #   ("cat","is")
    # ])
    #
    # ->
    # {
    #   ("the","cat"):1,
    #   ("cat","is"):1
    # }
    ref_c = Counter(ngrams(ref, n))

    # 统计候选文本中的 n-gram 次数
    cand_c = Counter(ngrams(cand, n))

    # 计算重叠数量（overlap）
    #
    # ref_c.items() 会返回：
    # (key, value)
    #
    # 即：
    # (ngram, count)
    #
    # 例如：
    # (("the","cat"), 1)
    #
    # k = ngram
    # v = count
    overlap = sum(
        # min(v, cand_c[k])
        #
        # 取两边最小值
        #
        # 这是 ROUGE/BLEU 常见做法
        #
        # 防止重复计数
        #
        # 例如：
        # ref 中有 3 次
        # cand 中有 1 次
        #
        # 那最多只能算匹配 1 次
        min(v, cand_c[k])
        # 遍历参考文本中的所有 n-gram
        for k, v in ref_c.items()
    )

    # sum(ref_c.values())
    #
    # 统计 reference 中
    # 一共有多少个 n-gram
    #
    # overlap / total
    #
    # 即 Recall
    return overlap / sum(ref_c.values())


# =========================
# 4. 计算 LCS
# =========================


def lcs_len(a, b):
    """
    计算最长公共子序列（LCS）长度

    LCS = Longest Common Subsequence

    注意：
    “子序列”不要求连续
    但顺序必须一致

    例如：

    a = [A,B,C,D]
    b = [A,X,C,D]

    LCS = [A,C,D]
    长度 = 3

    这里使用：
    动态规划（Dynamic Programming）
    """

    # m = a 的长度
    # n = b 的长度
    m, n = len(a), len(b)

    # 创建二维 DP 表
    #
    # 大小：
    # (m+1) 行
    # (n+1) 列
    #
    # 初始值全为 0
    #
    # 例如：
    # dp[3][4]
    #
    # 表示：
    # a 前 3 个元素
    # 和
    # b 前 4 个元素
    #
    # 的 LCS 长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 遍历 a
    #
    # range(1, m+1)
    # 从 1 开始
    #
    # 因为第 0 行/列用于边界初始化
    for i in range(1, m + 1):
        # 遍历 b
        for j in range(1, n + 1):
            # 如果当前位置字符相同
            #
            # a[i-1]
            # b[j-1]
            #
            # 因为：
            # dp 从 1 开始
            # 但数组从 0 开始
            if a[i - 1] == b[j - 1]:
                # 左上角 + 1
                #
                # 表示：
                # 找到了新的公共元素
                dp[i][j] = dp[i - 1][j - 1] + 1

            else:
                # 如果不同
                #
                # 就看：
                # - 去掉 a 当前元素
                # - 去掉 b 当前元素
                #
                # 哪个 LCS 更长
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 最终结果：
    # 右下角
    return dp[m][n]


# =========================
# 5. BLEU clipped precision
# =========================


def clipped_precision(ref, cand, n):
    """
    计算 BLEU 的 clipped precision

    precision 的意思：

    cand 生成出来的 n-gram
    有多少是真的对的
    """

    # 统计 reference n-gram
    ref_c = Counter(ngrams(ref, n))

    # 统计 candidate n-gram
    cand_c = Counter(ngrams(cand, n))

    # 计算 overlap
    overlap = sum(
        # clipped
        #
        # 取最小值
        #
        # 防止 candidate 疯狂重复刷分
        min(v, ref_c[k])
        # 注意：
        # BLEU 是遍历 cand
        #
        # 因为 BLEU 是 precision
        #
        # “生成出来的东西里
        # 有多少是对的”
        for k, v in cand_c.items()
    )

    # overlap / candidate_total
    #
    # precision
    return overlap / sum(cand_c.values())


# =========================
# 6. 计算 BLEU
# =========================


def bleu(ref, cand, max_n):
    """
    计算 BLEU

    max_n:
    使用到几元 n-gram

    例如：
    max_n=2
    -> BLEU-2
    """

    # 计算每个 n 的 precision
    #
    # 例如：
    # [p1, p2]
    #
    # 即：
    # unigram precision
    # bigram precision
    ps = [clipped_precision(ref, cand, i) for i in range(1, max_n + 1)]

    # 每个 n 的权重
    #
    # BLEU 默认均匀权重
    #
    # 例如：
    # BLEU-2
    #
    # -> [0.5, 0.5]
    weights = [1 / max_n] * max_n

    # c = candidate 长度
    # r = reference 长度
    c, r = len(cand), len(ref)

    # brevity penalty（长度惩罚）
    #
    # 如果 cand 太短
    # BLEU 会惩罚
    #
    # 防止：
    # 只生成几个高频词骗高分
    #
    # 当 c > r:
    # bp = 1
    #
    # 否则：
    # bp = e^(1-r/c)
    bp = 1 if c > r else math.exp(1 - r / c)

    # BLEU 最终公式：
    #
    # BP * exp(Σ w*log(p))
    #
    # 为什么取 log？
    #
    # 因为：
    # 多个概率连乘
    # 容易数值下溢
    #
    # log 后：
    # 连乘 -> 连加
    #
    # 更稳定
    return bp * math.exp(
        # zip(weights, ps)
        #
        # 把：
        # [0.5,0.5]
        # [0.8,0.6]
        #
        # 组合成：
        # (0.5,0.8)
        # (0.5,0.6)
        sum(w * math.log(p) for w, p in zip(weights, ps))
    )


# =========================
# 7. 计算 ROUGE
# =========================

# ROUGE-1
r1 = rouge_n(ref, cand, 1)

# ROUGE-2
r2 = rouge_n(ref, cand, 2)


# =========================
# 8. 计算 ROUGE-L
# =========================

# 最长公共子序列长度
l = lcs_len(cand, ref)

# Recall
#
# LCS / reference_length
rl_r = l / len(ref)

# Precision
#
# LCS / candidate_length
rl_p = l / len(cand)

# F1
#
# Precision 和 Recall 的调和平均
rl_f1 = 2 * rl_r * rl_p / (rl_r + rl_p)


# =========================
# 9. 计算 BLEU
# =========================

# BLEU-1
b1 = bleu(ref, cand, 1)

# BLEU-2
b2 = bleu(ref, cand, 2)


# =========================
# 10. Accuracy 示例
# =========================

# 真实标签
y_true = [1, 0, 1, 1, 0, 0, 1, 0]

# 模型预测标签
y_pred = [1, 1, 1, 1, 0, 0, 0, 0]

# 计算 Accuracy
#
# zip(y_true, y_pred)
#
# 会得到：
# (1,1)
# (0,1)
# ...
#
# a == b
#
# True -> 1
# False -> 0
#
# int(True)=1
# int(False)=0
#
# 最后求和得到：
# 正确数量
acc = sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(y_true)


# =========================
# 11. Win Rate 示例
# =========================

# W = win
# L = lose
# T = tie
W, L, T = 6, 3, 1

# 不计平局
win_rate = W / (W + L)

# 平局按 0.5 算
win_rate_tie05 = (W + 0.5 * T) / (W + L + T)


# =========================
# 12. 输出结果
# =========================

# :.4f
#
# 表示：
# 保留 4 位小数

print(f"ROUGE-1={r1:.4f}")

print(f"ROUGE-2={r2:.4f}")

print(f"ROUGE-L(R/P/F1)={rl_r:.4f}/{rl_p:.4f}/{rl_f1:.4f}")

print(f"BLEU-1={b1:.4f}")

print(f"BLEU-2={b2:.4f}")

print(f"Accuracy={acc:.4f}")

print(f"WinRate={win_rate:.4f}")

print(f"WinRate(tie0.5)={win_rate_tie05:.4f}")
