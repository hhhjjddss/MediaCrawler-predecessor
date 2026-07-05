# -*- coding: utf-8 -*-
"""
新版抖音存储模块
按用户→作品组织数据，简化评论格式
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from tools import utils
import config


class DouyinNewStore:
    """新版抖音存储器"""

    def __init__(self):
        self.base_dir = os.path.join(config.SAVE_DATA_PATH, "douyin")
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, name: str, max_length: int = 30) -> str:
        """清理文件名，移除非法字符"""
        if not name:
            return "未知"
        # 移除非法字符
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # 截断长度
        if len(name) > max_length:
            name = name[:max_length]
        return name.strip() or "未知"

    def _format_timestamp(self, timestamp: int) -> str:
        """格式化时间戳"""
        try:
            if timestamp > 1000000000000:  # 毫秒级
                timestamp = timestamp // 1000
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "未知时间"

    def get_user_dir(self, nickname: str, unique_id: str) -> str:
        """获取用户目录"""
        user_name = self._sanitize_filename(nickname)
        user_id = unique_id or "未知ID"
        user_dir_name = f"{user_name}_{user_id}"
        user_dir = os.path.join(self.base_dir, user_dir_name)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def get_aweme_dir(self, user_dir: str, aweme_id: str, title: str, index: int) -> str:
        """获取作品目录"""
        title_clean = self._sanitize_filename(title, max_length=20)
        aweme_dir_name = f"{index:03d}_{title_clean}"
        aweme_dir = os.path.join(user_dir, aweme_dir_name)
        os.makedirs(aweme_dir, exist_ok=True)
        # 创建媒体子目录
        media_dir = os.path.join(aweme_dir, "media")
        os.makedirs(media_dir, exist_ok=True)
        return aweme_dir

    def save_desc(self, aweme_dir: str, aweme_info: Dict):
        """保存作品文案"""
        desc_file = os.path.join(aweme_dir, "desc.md")

        # 提取信息
        title = aweme_info.get("title", "")
        desc = aweme_info.get("desc", "")
        create_time = aweme_info.get("create_time", 0)
        liked_count = aweme_info.get("liked_count", "0")
        comment_count = aweme_info.get("comment_count", "0")
        share_count = aweme_info.get("share_count", "0")
        aweme_url = aweme_info.get("aweme_url", "")

        # 生成内容
        content = f"""# 📝 作品文案

## 基本信息

| 项目 | 内容 |
|-----|------|
| 标题 | {title or '无标题'} |
| 发布时间 | {self._format_timestamp(create_time)} |
| 点赞数 | {liked_count} |
| 评论数 | {comment_count} |
| 分享数 | {share_count} |
| 作品链接 | {aweme_url} |

## 文案内容

{desc or '暂无文案'}

"""
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_comments(self, aweme_dir: str, comments: List[Dict]):
        """保存评论（树形结构）"""
        if not comments:
            return

        comments_file = os.path.join(aweme_dir, "comments.md")

        # 分离一级评论和二级评论
        top_comments = []
        reply_comments = {}  # parent_id -> [replies]

        for comment in comments:
            parent_id = comment.get("parent_comment_id", "0")
            if parent_id == "0":
                top_comments.append(comment)
            else:
                if parent_id not in reply_comments:
                    reply_comments[parent_id] = []
                reply_comments[parent_id].append(comment)

        # 生成评论内容
        content = "# 💬 评论\n\n"
        content += f"共 {len(comments)} 条评论\n\n"

        for i, comment in enumerate(top_comments, 1):
            comment_id = comment.get("comment_id", "")
            text = comment.get("content", "")
            ip_location = comment.get("ip_location", "未知")
            create_time = comment.get("create_time", 0)
            nickname = comment.get("nickname", "匿名用户")

            # 一级评论
            content += f"## {i}. {nickname}\n\n"
            content += f"- 📍 **{ip_location}** | {self._format_timestamp(create_time)}\n"
            content += f"  > {text}\n\n"

            # 二级评论（回复）
            replies = reply_comments.get(comment_id, [])
            for reply in replies:
                reply_text = reply.get("content", "")
                reply_ip = reply.get("ip_location", "未知")
                reply_time = reply.get("create_time", 0)
                reply_nickname = reply.get("nickname", "匿名用户")

                content += f"  - 📍 **{reply_ip}** | {self._format_timestamp(reply_time)} | 回复 @{nickname}\n"
                content += f"    > {reply_text}\n\n"

        with open(comments_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_aweme_summary(self, user_dir: str, aweme_list: List[Dict]):
        """保存作品汇总"""
        summary_file = os.path.join(user_dir, "README.md")

        content = "# 📋 作品列表\n\n"
        content += f"共 {len(aweme_list)} 个作品\n\n"
        content += "| 序号 | 标题 | 发布时间 | 点赞 | 评论 | 目录 |\n"
        content += "|-----|------|---------|------|------|------|\n"

        for i, aweme in enumerate(aweme_list, 1):
            title = aweme.get("title", "无标题")
            create_time = aweme.get("create_time", 0)
            liked_count = aweme.get("liked_count", "0")
            comment_count = aweme.get("comment_count", "0")
            title_clean = self._sanitize_filename(title, max_length=20)

            content += f"| {i:03d} | {title[:20]} | {self._format_timestamp(create_time)} | {liked_count} | {comment_count} | {i:03d}_{title_clean} |\n"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_user_info(self, user_dir: str, user_info: Dict):
        """保存用户信息"""
        info_file = os.path.join(user_dir, "user_info.md")

        nickname = user_info.get("nickname", "未知")
        unique_id = user_info.get("unique_id", "未知")
        ip_location = user_info.get("ip_location", "未知")
        follows = user_info.get("follows", 0)
        fans = user_info.get("fans", 0)
        interaction = user_info.get("interaction", 0)
        videos_count = user_info.get("videos_count", 0)
        desc = user_info.get("desc", "")

        content = f"""# 👤 用户信息

## 基本资料

| 项目 | 内容 |
|-----|------|
| 昵称 | **{nickname}** |
| 抖音号 | {unique_id} |
| IP属地 | {ip_location} |
| 关注 | {follows:,} |
| 粉丝 | {fans:,} |
| 获赞 | {interaction:,} |
| 作品数 | {videos_count:,} |

## 个人简介

{desc or '暂无简介'}

"""
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_media_path(self, aweme_dir: str, filename: str) -> str:
        """获取媒体文件路径"""
        media_dir = os.path.join(aweme_dir, "media")
        os.makedirs(media_dir, exist_ok=True)
        return os.path.join(media_dir, filename)
