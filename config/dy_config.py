# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/config/dy_config.py
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

# Douyin platform configuration
PUBLISH_TIME_TYPE = 0

# Specify DY video URL list (supports multiple formats)
# Supported formats:
# 1. Full video URL: "https://www.douyin.com/video/7525538910311632128"
# 2. URL with modal_id: "https://www.douyin.com/user/xxx?modal_id=7525538910311632128"
# 3. The search page has modal_id: "https://www.douyin.com/root/search/python?modal_id=7525538910311632128"
# 4. Short link: "https://v.douyin.com/drIPtQ_WPWY/"
# 5. Pure video ID: "7280854932641664319"
DY_SPECIFIED_ID_LIST = [
    # 在这里填入要爬取的视频链接或ID
    # 支持的格式:
    # 1. 完整视频链接: "https://www.douyin.com/video/7525538910311632128"
    # 2. 短链接: "https://v.douyin.com/xxxxx/"
    # 3. 纯视频ID: "7280854932641664319"
    # "https://www.douyin.com/video/xxxxxxxxx",
]

# Specify DY creator URL list (supports full URL or sec_user_id)
# Supported formats:
# 1. Complete creator homepage URL: "https://www.douyin.com/user/xxxxxxxxx?from_tab_name=main"
# 2. sec_user_id: "MS4wLjABAAAAxxxxxxxxx"
DY_CREATOR_ID_LIST = [
    # 在这里填入要爬取的用户主页链接
    # "https://www.douyin.com/user/xxxxxxxxx?from_tab_name=main",
]
