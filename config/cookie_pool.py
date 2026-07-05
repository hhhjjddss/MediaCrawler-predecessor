# -*- coding: utf-8 -*-
"""
Cookie 池配置 - 多账号轮换
当某个账号被拉黑时，自动切换到下一个账号
"""

# Cookie 池配置
# 格式：[("账号名称", "Cookie字符串"), ...]
COOKIE_POOL = [
    ("账号1", "这里填写第一个账号的Cookie"),
    ("账号2", "这里填写第二个账号的Cookie"),
    ("账号3", "这里填写第三个账号的Cookie"),
    # 可以继续添加更多账号...
]

# 当前使用的 Cookie 索引（自动管理，无需手动修改）
CURRENT_COOKIE_INDEX = 0

# Cookie 失效检测关键词（当响应中包含这些关键词时，认为 Cookie 失效）
COOKIE_INVALID_KEYWORDS = [
    "登录",
    "请先登录",
    "未登录",
    "login",
    "unauthorized",
]

# Cookie 失效后的重试次数
MAX_COOKIE_RETRY = 3

# 是否启用 Cookie 轮换
ENABLE_COOKIE_ROTATION = True
