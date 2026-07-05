# -*- coding: utf-8 -*-
"""
去重管理器
使用 JSON 文件记录已爬取的数据，避免重复爬取
"""

import json
import os
from typing import Set, List, Dict, Optional
from tools import utils


class DedupManager:
    """去重管理器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.dedup_file = os.path.join(data_dir, "dedup_records.json")
        self.records = self._load_records()

    def _load_records(self) -> Dict:
        """加载去重记录"""
        if os.path.exists(self.dedup_file):
            try:
                with open(self.dedup_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                utils.logger.warning(f"[DedupManager] 加载去重记录失败: {e}")
        return {
            "video_ids": [],      # 已爬取的视频ID
            "comment_ids": [],    # 已爬取的评论ID
            "user_ids": [],       # 已爬取的用户ID
            "last_update": ""     # 最后更新时间
        }

    def _save_records(self):
        """保存去重记录"""
        try:
            from datetime import datetime
            self.records["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.dedup_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            utils.logger.error(f"[DedupManager] 保存去重记录失败: {e}")

    def is_video_duplicate(self, video_id: str) -> bool:
        """检查视频是否重复"""
        return video_id in self.records["video_ids"]

    def is_comment_duplicate(self, comment_id: str) -> bool:
        """检查评论是否重复"""
        return comment_id in self.records["comment_ids"]

    def is_user_duplicate(self, user_id: str) -> bool:
        """检查用户是否重复"""
        return user_id in self.records["user_ids"]

    def add_video_id(self, video_id: str):
        """添加视频ID到记录"""
        if video_id not in self.records["video_ids"]:
            self.records["video_ids"].append(video_id)

    def add_comment_id(self, comment_id: str):
        """添加评论ID到记录"""
        if comment_id not in self.records["comment_ids"]:
            self.records["comment_ids"].append(comment_id)

    def add_user_id(self, user_id: str):
        """添加用户ID到记录"""
        if user_id not in self.records["user_ids"]:
            self.records["user_ids"].append(user_id)

    def filter_new_videos(self, video_list: List[Dict]) -> List[Dict]:
        """过滤出新的视频"""
        new_videos = []
        for video in video_list:
            video_id = video.get("aweme_id")
            if video_id and not self.is_video_duplicate(video_id):
                new_videos.append(video)
        return new_videos

    def filter_new_comments(self, comment_list: List[Dict]) -> List[Dict]:
        """过滤出新的评论"""
        new_comments = []
        for comment in comment_list:
            comment_id = comment.get("cid")
            if comment_id and not self.is_comment_duplicate(comment_id):
                new_comments.append(comment)
        return new_comments

    def save_and_update(self):
        """保存并更新记录"""
        self._save_records()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "video_count": len(self.records["video_ids"]),
            "comment_count": len(self.records["comment_ids"]),
            "user_count": len(self.records["user_ids"]),
            "last_update": self.records.get("last_update", "未知")
        }

    def clear_records(self, record_type: str = "all"):
        """清除记录"""
        if record_type == "all":
            self.records = {
                "video_ids": [],
                "comment_ids": [],
                "user_ids": [],
                "last_update": ""
            }
        elif record_type == "video":
            self.records["video_ids"] = []
        elif record_type == "comment":
            self.records["comment_ids"] = []
        elif record_type == "user":
            self.records["user_ids"] = []

        self._save_records()
        utils.logger.info(f"[DedupManager] 已清除 {record_type} 记录")
