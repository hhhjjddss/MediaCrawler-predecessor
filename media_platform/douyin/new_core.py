# -*- coding: utf-8 -*-
"""
新版抖音爬虫核心
按用户→作品组织数据
"""

import asyncio
import os
from typing import Dict, List, Optional

import config
from store.douyin.new_store import DouyinNewStore
from tools import utils
from tools.dedup_manager import DedupManager
from tools.change_logger import ChangeLogger

from .client import DouYinClient
from .exception import DataFetchError


class NewDouyinCrawler:
    """新版抖音爬虫"""

    def __init__(self, dy_client: DouYinClient):
        self.dy_client = dy_client
        self.new_store = DouyinNewStore()
        self.dedup_manager = DedupManager(os.path.join(config.SAVE_DATA_PATH, "douyin"))
        self.change_logger = ChangeLogger(os.path.join(config.SAVE_DATA_PATH, "douyin"))

    async def crawl_user(self, user_id: str):
        """爬取单个用户的所有作品"""
        utils.logger.info(f"[NewDouyinCrawler] 开始爬取用户: {user_id}")

        # 1. 获取用户信息
        creator_info = await self.dy_client.get_user_info(user_id)
        if not creator_info:
            utils.logger.error(f"[NewDouyinCrawler] 获取用户信息失败: {user_id}")
            return

        user_info = creator_info.get("user", {})
        nickname = user_info.get("nickname", "未知")
        unique_id = user_info.get("unique_id", "")

        # 2. 创建用户目录
        user_dir = self.new_store.get_user_dir(nickname, unique_id)

        # 3. 保存用户信息
        user_data = {
            "nickname": nickname,
            "unique_id": unique_id,
            "ip_location": user_info.get("ip_location", ""),
            "follows": user_info.get("following_count", 0),
            "fans": user_info.get("max_follower_count", 0),
            "interaction": user_info.get("total_favorited", 0),
            "videos_count": user_info.get("aweme_count", 0),
            "desc": user_info.get("signature", ""),
        }
        self.new_store.save_user_info(user_dir, user_data)

        # 4. 获取所有作品
        all_video_list = await self.dy_client.get_all_user_aweme_posts(
            sec_user_id=user_id,
            callback=None  # 不使用回调，直接返回列表
        )

        if not all_video_list:
            utils.logger.warning(f"[NewDouyinCrawler] 用户没有作品: {nickname}")
            return

        utils.logger.info(f"[NewDouyinCrawler] 用户 {nickname} 共有 {len(all_video_list)} 个作品")

        # 5. 逐个处理作品
        aweme_summary = []
        total_comment_count = 0  # 统计总评论数

        for i, video_item in enumerate(all_video_list, 1):
            aweme_id = video_item.get("aweme_id")
            if not aweme_id:
                continue

            # 去重检查
            if config.ENABLE_DEDUP and self.dedup_manager.is_video_duplicate(aweme_id):
                utils.logger.info(f"[NewDouyinCrawler] 作品已存在，跳过: {aweme_id}")
                continue

            # 获取作品详情
            try:
                aweme_detail = await self.dy_client.get_video_by_id(aweme_id)
                if not aweme_detail:
                    continue

                # 处理作品（包含下载媒体和爬取评论）
                comment_count = await self._process_aweme(user_dir, aweme_detail, i, nickname)
                total_comment_count += comment_count
                aweme_summary.append(aweme_detail)

                # 添加到去重记录
                if config.ENABLE_DEDUP:
                    self.dedup_manager.add_video_id(aweme_id)

                # 延时
                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

            except Exception as e:
                utils.logger.error(f"[NewDouyinCrawler] 处理作品失败: {aweme_id}, 错误: {e}")
                continue

        # 6. 保存作品汇总
        self.new_store.save_aweme_summary(user_dir, aweme_summary)

        # 7. 更新日志（传入实际评论数）
        self._update_log(user_id, user_data, len(aweme_summary), total_comment_count)

        # 8. 保存去重记录
        if config.ENABLE_DEDUP:
            self.dedup_manager.save_and_update()

        utils.logger.info(f"[NewDouyinCrawler] 用户 {nickname} 爬取完成")

    async def _process_aweme(self, user_dir: str, aweme_detail: Dict, index: int, nickname: str):
        """处理单个作品"""
        aweme_id = aweme_detail.get("aweme_id")
        title = aweme_detail.get("desc", "")[:30] or "无标题"

        # 创建作品目录
        aweme_dir = self.new_store.get_aweme_dir(user_dir, aweme_id, title, index)

        # 保存文案
        aweme_info = {
            "title": title,
            "desc": aweme_detail.get("desc", ""),
            "create_time": aweme_detail.get("create_time", 0),
            "liked_count": str(aweme_detail.get("statistics", {}).get("digg_count", 0)),
            "comment_count": str(aweme_detail.get("statistics", {}).get("comment_count", 0)),
            "share_count": str(aweme_detail.get("statistics", {}).get("share_count", 0)),
            "aweme_url": f"https://www.douyin.com/video/{aweme_id}",
        }
        self.new_store.save_desc(aweme_dir, aweme_info)

        # 下载媒体
        await self._download_media(aweme_dir, aweme_detail)

        # 处理图文作品（转换为视频）
        await self._process_image_post(aweme_dir)

        # 爬取评论
        comment_count = 0
        if config.ENABLE_GET_COMMENTS:
            comment_count = await self._crawl_comments(aweme_dir, aweme_id, nickname)

        utils.logger.info(f"[NewDouyinCrawler] 作品 {index} 处理完成: {title}")

        return comment_count

    async def _download_media(self, aweme_dir: str, aweme_detail: Dict):
        """下载媒体文件"""
        try:
            # 下载视频
            video_url = self._extract_video_url(aweme_detail)
            if video_url:
                video_path = self.new_store.get_media_path(aweme_dir, "video.mp4")
                content = await self.dy_client.get_aweme_media(video_url)
                if content:
                    with open(video_path, 'wb') as f:
                        f.write(content)
                    utils.logger.info(f"[NewDouyinCrawler] 视频下载完成")

            # 下载图片
            images = self._extract_images(aweme_detail)
            for i, img_url in enumerate(images, 1):
                img_path = self.new_store.get_media_path(aweme_dir, f"{i:03d}.jpeg")
                content = await self.dy_client.get_aweme_media(img_url)
                if content:
                    with open(img_path, 'wb') as f:
                        f.write(content)

        except Exception as e:
            utils.logger.warning(f"[NewDouyinCrawler] 媒体下载失败: {e}")

    def _extract_video_url(self, aweme_detail: Dict) -> Optional[str]:
        """提取视频URL"""
        try:
            video = aweme_detail.get("video", {})
            play_addr = video.get("play_addr", {})
            url_list = play_addr.get("url_list", [])
            return url_list[0] if url_list else None
        except:
            return None

    def _extract_images(self, aweme_detail: Dict) -> List[str]:
        """提取图片URL列表"""
        images = []
        try:
            images_list = aweme_detail.get("images", [])
            for img in images_list:
                url_list = img.get("url_list", [])
                if url_list:
                    images.append(url_list[-1])
        except:
            pass
        return images

    async def _process_image_post(self, aweme_dir: str):
        """处理图文作品，转换为视频"""
        try:
            from tools.media_processor import media_processor

            media_dir = os.path.join(aweme_dir, "media")
            if not os.path.exists(media_dir):
                return

            # 检查是否为图文作品
            if media_processor.is_image_post(media_dir):
                utils.logger.info(f"[NewDouyinCrawler] 检测到图文作品，开始转换为视频...")

                # 转换为视频
                video_path = media_processor.images_to_video(media_dir)
                if video_path:
                    utils.logger.info(f"[NewDouyinCrawler] 图文作品转换成功: {video_path}")
                else:
                    utils.logger.warning(f"[NewDouyinCrawler] 图文作品转换失败")

        except Exception as e:
            utils.logger.warning(f"[NewDouyinCrawler] 处理图文作品失败: {e}")

    async def _crawl_comments(self, aweme_dir: str, aweme_id: str, nickname: str):
        """爬取作品评论"""
        try:
            # 收集评论
            comments = []

            async def comment_callback(aweme_id: str, comment_list: List[Dict]):
                for comment in comment_list:
                    comment_data = {
                        "comment_id": comment.get("cid"),
                        "content": comment.get("text"),
                        "ip_location": comment.get("ip_label", "未知"),
                        "create_time": comment.get("create_time", 0),
                        "nickname": comment.get("user", {}).get("nickname", "匿名用户"),
                        "parent_comment_id": comment.get("reply_id", "0"),
                    }
                    comments.append(comment_data)

                    # 去重
                    if config.ENABLE_DEDUP:
                        self.dedup_manager.add_comment_id(comment_data["comment_id"])

            # 调用API获取评论
            await self.dy_client.get_aweme_all_comments(
                aweme_id=aweme_id,
                crawl_interval=config.CRAWLER_MAX_SLEEP_SEC,
                is_fetch_sub_comments=config.ENABLE_GET_SUB_COMMENTS,
                callback=comment_callback,
                max_count=config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES,
            )

            # 保存评论
            if comments:
                self.new_store.save_comments(aweme_dir, comments)
                utils.logger.info(f"[NewDouyinCrawler] 保存评论 {len(comments)} 条")

            return len(comments)

        except Exception as e:
            utils.logger.warning(f"[NewDouyinCrawler] 爬取评论失败: {e}")
            return 0

    def _update_log(self, user_id: str, user_info: Dict, video_count: int, comment_count: int):
        """更新爬取日志"""
        try:
            self.change_logger.log_crawl(
                user_id=user_id,
                user_info=user_info,
                video_count=video_count,
                comment_count=comment_count
            )
        except Exception as e:
            utils.logger.warning(f"[NewDouyinCrawler] 更新日志失败: {e}")
