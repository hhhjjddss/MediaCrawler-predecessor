# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/config/base_config.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# Basic configuration
PLATFORM = "dy"  # Platform, xhs | dy | ks | bili | wb | tieba | zhihu

# 是否使用海外版小红书 (rednote.com)
# 开启后 API 走 webapi.rednote.com，cookie 域使用 .rednote.com
XHS_INTERNATIONAL = False

KEYWORDS = "二次元男生头像"  # Keyword search configuration, separated by English commas
LOGIN_TYPE = "cookie"  # qrcode or phone or cookie
COOKIES = "__ac_nonce=06a3cc20c0017b6b54b30; __ac_signature=_02B4Z6wo00f01NkVWgQAAIDBo.yu4G-QuHTZNX6AAFx.5a; enter_pc_once=1; UIFID_TEMP=e8af8eec168e6006bb749042c72c8d2abad7941d853b8500624783ee98d61da6b1b1907410d8d90f538292ae66927733dd9a6c2c49ebb1c05fce89fc3b810f17302ed123b0c8300b7e3d8e49997774ef; x-web-secsdk-uid=327b670c-7a69-4df6-ace6-c48fd3c8d30f; s_v_web_id=verify_mqt34v9t_Ui3fz1ST_q8yk_4d8c_97K8_QzDFEN0r7op9; =douyin.com; device_web_cpu_core=12; device_web_memory_size=16; architecture=amd64; is_support_rtm_web_ts=1; hevc_supported=true; home_can_add_dy_2_desktop=%220%22; dy_swidth=1280; dy_sheight=720; fpk1=U2FsdGVkX19nKcxMkHjI1zVuWgSBrxecwge0YhA5Icqs3cBU7BZwbPmBdzv/GKepGcdyWJYj9MFrj0mgJ50IMQ==; fpk2=90daa551604269dbcdcf237b5cc700f3; strategyABtestKey=%221782366744.311%22; fg_uid=RID20260625135223DC77A88EFCBCE0826129; passport_csrf_token=8d9774a925a81d4a5105cc15369b975d; passport_csrf_token_default=8d9774a925a81d4a5105cc15369b975d; bd_ticket_guard_client_web_domain=2; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e592772606761776c7360775927582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f273d3030333132333336373d3234272927676c715a75776a716a666a69273f2763646976602778; bit_env=DZeL6R-VXelU5BcDNCfqsTxwWU3Aa3GdeWYSDfT5b7DToUE3pqHyFmJGPWWP9f51GkAbo544HaOvOymBCuWeFj3tXhxBE8qFJmMRnH_Up-grzb9xxYRGBQUQuhDQ9NFaogXP-2g3K-KzrI1BOIaYFWtecGkCTmT5bpxUqnFiZ8oHiR_bDYB5ZCbcYdEJCMFWyMNqt9isCeMb_3eNp1sxncCYP5KEhn619vkSlJK4Qm8_O4Bl-XvvSR4BDOXl_IZKkfH0JM8_zPJedx1Cq1pIPd3ttwrNYXc1mZfrkMY7MIZp0J4VLbJiqJ1h0pUR5K2LUVa2dqZgbJTyBTWjZPJoU2IVIi_5W6MeNYR7vrsMiazb4PeFrjwn6nf6PgyuJok63mHfrOAcTcqWyl7a5eUIW8ezxvJfEPcmFa-Aj9OtIw5-HmjBSh7VBm2N-t93_LY43L8XO-OVIsbNfJmyC6lyBY_7aBH_VR7U9bmGR8DFmlRNCGCuVSCYK7uJeGeu6fnp; gulu_source_res=eyJwX2luIjoiYzI2YmJhYzE0ZTUwZDg3M2I0OGE2ZmEwMGJiODE4NzA5MzQ3N2ZhODY1MmFkYmNjODJkZDcyOWQxOTJhZjhlNCJ9; passport_auth_mix_state=r8t4wck2ybz6wx82n82d3jvp2rqvxd9u3afsef5j8ystit1k; passport_assist_user=ClMa5yx8ML6JXOG_CRLbMpTgrhbYWqaFYCgxYDM0Ase_XtXXryhE0LB6HB5AjV6e1XjPHfghhgiUOQPVQ_WnKCIUVE-xLUZqe7x3CU26V4pczglPGhpKCjwAAAAAAAAAAAAAUJUhOjhv85XAL9FiH9F5g3iLLsmV4z2wLJwxjmhnVOVg4UjO1ac_l8t-iUjhr6Yg6HQQvo2VDhiJr9ZUIAEiAQNDeV4X; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=66fae67440e973647bfeea8ffbf5ea19%7C1782366763%7C5184000%7CMon%2C+24-Aug-2026+05%3A52%3A43+GMT; uid_tt=a8a1bbe5f2915f141a22b23a286d23d454156640ee9692f78905934e24943b35; uid_tt_ss=a8a1bbe5f2915f141a22b23a286d23d454156640ee9692f78905934e24943b35; sid_tt=66fae67440e973647bfeea8ffbf5ea19; sessionid=66fae67440e973647bfeea8ffbf5ea19; sessionid_ss=66fae67440e973647bfeea8ffbf5ea19; session_tlb_tag=sttt%7C5%7CZvrmdEDpc2R7_uqP-_XqGf________-5JC0ZYAOxVKS5y46K8vMn_71TIqcDY49wsMJ78PBjkus%3D; is_staff_user=false; has_biz_token=false; sid_ucp_v1=1.0.0-KGRlMzUwNDI2Zjc2ZTQwYjQwZmQ2MGM3YWRiNjViMDI2YTA2YTRjNTQKIgi5iMD-w-CAlWcQq4Tz0QYY7zEgDDCRj6i5BjgHQPQHSAQaAmhsIiA2NmZhZTY3NDQwZTk3MzY0N2JmZWVhOGZmYmY1ZWExOQ; ssid_ucp_v1=1.0.0-KGRlMzUwNDI2Zjc2ZTQwYjQwZmQ2MGM3YWRiNjViMDI2YTA2YTRjNTQKIgi5iMD-w-CAlWcQq4Tz0QYY7zEgDDCRj6i5BjgHQPQHSAQaAmhsIiA2NmZhZTY3NDQwZTk3MzY0N2JmZWVhOGZmYmY1ZWExOQ; bd_ticket_guard_web_domain=2; _bd_ticket_crypt_cookie=380d0dfb3e490f49a370cb3e733bee4a; __security_mc_1_s_sdk_sign_data_key_web_protect=f7b30745-4e04-8a6e; __security_mc_1_s_sdk_cert_key=c5cc2e93-4daf-8010; __security_mc_1_s_sdk_crypt_sdk=a869b27b-4e3c-b6f3; __security_server_data_status=1; login_time=1782366764499; publish_badge_show_info=%220%2C0%2C0%2C1782366764798%22; DiscoverFeedExposedAd=%7B%7D; UIFID=e8af8eec168e6006bb749042c72c8d2abad7941d853b8500624783ee98d61da6085173f5590885313e134113efb6dacac565b432d6ef8d7ddef7760f61db9fc49ae8b18a82d2dabd181a37cfff0e5c2519460fc1f54b4e43679d9b39c379708c5b1f5e6adfa44585ad51f66e873eb4bb31f286abe551ee6d756cc0d83e4bf328b6edb94821a4b3218d32db6e70f5bb5eb89eaf4734d3e4436c3bf6d46798c4b6; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1280%2C%5C%22screen_height%5C%22%3A720%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A16%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; SelfTabRedDotControl=%5B%5D; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRmlIcU9WVl1QWcwSXRaVHB6TDRLWWJFZkkxMUo2NmI1MXUwalNScDlMeFhvcEE1b0MwdXFQRE5PTGVmWlpZSmxwVmlLa2ZncW4wdVB5V0RsTHpwQT0iLCJiZC10aWNrZXQtZ3VhcmQtd2ViLXZlcnNpb24iOjJ9; ttwid=1%7CAwaLN9UNdJDKo3hhKAxSceqGa0p3YPhJBaAugS_Kn4U%7C1782366768%7C1e0a0b01bf6f4dde1802d1197bf809d85fcaec3c5b745a733dbc3e92f46d597c; is_dash_user=1; biz_trace_id=07b117a6; odin_tt=fd5f9ebe034110e13b76257b3dd0ccaecef3341928ddba4a23f8f559711c908b3946e9d552104c4971aeb3e22ef5557285a946b424ff0cbd64eae4c94a606070; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJGaUhxT1VZWXVBZzBJdFpUcHpMNEtZYkVmSTExSjY2YjUxdTBqU1JwOUx4WG9wQTVvQzB1cVBETk9MZWZaWllKbHBWaUtrYTJncW4wdVB5V0RsTHpwQT0iLCJ0c19zaWduIjoidHMuMi44YWFmMDkxNDY3Mzk3ZjIwMWYyYmY4MmJhYjk3OTk5OWQzZWMzMWI5N2FhYjY4OGM3OWI4YjM1ZGIzMGM3OWM3YzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJIV2VVMEtLVUNydzlzOVlLUllQVk1EZEo0a01KUldVRHRIMkErKzd0ZVBZPSIsInNlY190cyI6IiNLeGw2bXpRaGNXSlBMZUFSaXZZSWtpZW85VHRDeWNoQmhvWXVoa05hQlpIMWxraDB6bDkrVzU0UFJmQVEifQ%3D%3D"
CRAWLER_TYPE = (
    "creator"  # Crawling type, search (keyword search) | detail (post details) | creator (creator homepage data)
)
# Whether to enable IP proxy
ENABLE_IP_PROXY = False

# Number of proxy IP pools
IP_PROXY_POOL_COUNT = 2

# Proxy IP provider name
IP_PROXY_PROVIDER_NAME = "kuaidaili"  # kuaidaili | wandouhttp | static

# Static proxy configuration (used when IP_PROXY_PROVIDER_NAME is set to "static")
# Format: "http://your_home_domain:port" or "http://user:password@your_home_domain:port"
STATIC_PROXY_URL = ""

# Setting to True will not open the browser (headless browser)
# Setting False will open a browser
# If Xiaohongshu keeps scanning the code to log in but fails, open the browser and manually pass the sliding verification code.
# If Douyin keeps prompting failure, open the browser and see if mobile phone number verification appears after scanning the QR code to log in. If it does, manually go through it and try again.
HEADLESS = False

# Whether to save login status
SAVE_LOGIN_STATE = True

# ==================== CDP (Chrome DevTools Protocol) 配置 ====================
# 是否启用 CDP 模式 - 使用用户本地的 Chrome/Edge 浏览器进行爬取，具有更好的反检测能力
# 开启后，会自动检测并启动用户的 Chrome/Edge 浏览器，通过 CDP 协议进行控制
# 该方式使用真实浏览器环境，包括用户的扩展、Cookie 和设置，大幅降低被风控检测的风险
ENABLE_CDP_MODE = False

# CDP 调试端口，用于与浏览器通信
# 如果端口被占用，系统会自动尝试下一个可用端口
CDP_DEBUG_PORT = 9222

# 自定义浏览器路径（可选）
# 如果为空，系统会自动检测 Chrome/Edge 的安装路径
# Windows 示例: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# macOS 示例: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CUSTOM_BROWSER_PATH = ""

# 是否在 CDP 模式下启用无头模式
# 注意：即使设置为 True，某些反检测功能在无头模式下可能无法正常工作
CDP_HEADLESS = False

# 浏览器启动超时时间（秒）
BROWSER_LAUNCH_TIMEOUT = 60

# 是否连接用户已打开的浏览器，而不是启动新的浏览器
# 开启后，程序会连接一个已经启用了远程调试的浏览器
# 用户需要在 Chrome 中开启远程调试：chrome://inspect/#remote-debugging
# 或者使用命令行参数启动 Chrome：--remote-debugging-port=9222
# 这种方式反检测效果最好，因为直接使用用户真实浏览器的所有 Cookie、扩展和浏览历史
CDP_CONNECT_EXISTING = False

# 程序结束时是否自动关闭浏览器
# 设置为 False 可以保持浏览器运行，方便调试
AUTO_CLOSE_BROWSER = True

# Data saving type option configuration, supports: csv, db, json, jsonl, sqlite, excel, postgres. It is best to save to DB, with deduplication function.
SAVE_DATA_OPTION = "jsonl"  # csv or db or json or jsonl or sqlite or excel or postgres

# Data saving path, if not specified by default, it will be saved to the data folder.
SAVE_DATA_PATH = "D:/github/MediaCrawler/data"

# Browser file configuration cached by the user's browser
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

# The number of pages to start crawling starts from the first page by default
START_PAGE = 1

# Control the number of crawled videos/posts
CRAWLER_MAX_NOTES_COUNT = 30

# Controlling the number of concurrent crawlers
MAX_CONCURRENCY_NUM = 1

# Whether to enable crawling media mode (including image or video resources), crawling media is not enabled by default
ENABLE_GET_MEIDAS = True

# Whether to enable comment crawling mode. Comment crawling is enabled by default.
ENABLE_GET_COMMENTS = True

# Control the number of crawled first-level comments (single video/post)
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 999999  # 设置为大数以获取所有评论

# Whether to enable the mode of crawling second-level comments. By default, crawling of second-level comments is not enabled.
# If the old version of the project uses db, you need to refer to schema/tables.sql line 287 to add table fields.
ENABLE_GET_SUB_COMMENTS = True

# ==================== 去重配置 ====================
# 是否启用去重功能（避免重复爬取相同数据）
ENABLE_DEDUP = True

# 去重记录文件保存路径（默认在 data 目录下）
DEDUP_RECORDS_FILE = "dedup_records.json"

# word cloud related
# Whether to enable generating comment word clouds
ENABLE_GET_WORDCLOUD = False
# Custom words and their groups
# Add rule: xx:yy where xx is a custom-added phrase, and yy is the group name to which the phrase xx is assigned.
CUSTOM_WORDS = {
    "零几": "年份",  # Recognize "zero points" as a whole
    "高频词": "专业术语",  # Example custom words
}

# Deactivate (disabled) word file path
STOP_WORDS_FILE = "./docs/hit_stopwords.txt"

# Chinese font file path
FONT_PATH = "./docs/STZHONGS.TTF"

# Crawl interval
CRAWLER_MAX_SLEEP_SEC = 8

# 是否禁用 SSL 证书验证。仅在使用企业代理、Burp Suite、mitmproxy 等会注入自签名证书的中间人代理时设为 True。
# 警告：禁用 SSL 验证将使所有流量暴露于中间人攻击风险，请勿在生产环境中开启。
DISABLE_SSL_VERIFY = False

from .bilibili_config import *
from .xhs_config import *
from .dy_config import *
from .ks_config import *
from .weibo_config import *
from .tieba_config import *
from .zhihu_config import *
