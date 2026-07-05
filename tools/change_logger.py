# -*- coding: utf-8 -*-
"""
数据变化记录器（修复版）
记录每次爬取的数据变化，生成 MD 格式的日志文件
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, List
from tools import utils
import config


class ChangeLogger:
    """数据变化记录器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.log_file = os.path.join(data_dir, "crawl_log.md")
        self.history_file = os.path.join(data_dir, "history_data.json")
        self.backup_file = os.path.join(data_dir, "history_data.json.bak")
        self._ensure_dir()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_history(self) -> Dict:
        """加载历史数据（带备份恢复）"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                utils.logger.warning(f"[ChangeLogger] 主文件读取失败: {e}")

                # 尝试从备份恢复
                if os.path.exists(self.backup_file):
                    try:
                        with open(self.backup_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        utils.logger.info("[ChangeLogger] 已从备份恢复")
                        return data
                    except:
                        pass

                # 备份也损坏，返回空数据
                utils.logger.error("[ChangeLogger] 历史数据已损坏，重置为空")
                return {}
        return {}

    def _save_history(self, data: Dict):
        """保存历史数据（先备份再写入）"""
        try:
            # 先备份当前文件
            if os.path.exists(self.history_file):
                shutil.copy2(self.history_file, self.backup_file)

            # 写入新数据
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            utils.logger.error(f"[ChangeLogger] 保存历史数据失败: {e}")

            # 恢复备份
            if os.path.exists(self.backup_file):
                try:
                    shutil.copy2(self.backup_file, self.history_file)
                    utils.logger.info("[ChangeLogger] 已从备份恢复")
                except:
                    pass

    def _safe_int(self, value) -> int:
        """安全转换为整数"""
        if value is None:
            return 0
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            # 移除逗号和其他非数字字符
            cleaned = value.replace(',', '').replace(' ', '')
            try:
                return int(cleaned)
            except ValueError:
                return 0
        return 0

    def _compare_and_log(self, user_id: str, new_data: Dict) -> List[str]:
        """对比数据变化并生成日志"""
        history = self._load_history()
        changes = []

        # 获取历史数据
        old_data = history.get(user_id, {})

        # 对比字段
        compare_fields = {
            'nickname': ('昵称', False),
            'ip_location': ('IP属地', False),
            'follows': ('关注', True),
            'fans': ('粉丝', True),
            'interaction': ('获赞', True),
            'videos_count': ('视频数', True),
            'desc': ('简介', False)
        }

        for field, (label, is_numeric) in compare_fields.items():
            old_val = old_data.get(field)
            new_val = new_data.get(field)

            if is_numeric:
                # 数值类型，统一转为整数对比
                old_num = self._safe_int(old_val)
                new_num = self._safe_int(new_val)

                if old_val is None:
                    # 首次记录
                    changes.append(f"**{label}**: {new_num:,}")
                elif old_num != new_num:
                    # 值变化
                    diff = new_num - old_num
                    if diff > 0:
                        changes.append(f"**{label}**: {old_num:,} → {new_num:,} (+{diff:,})")
                    else:
                        changes.append(f"**{label}**: {old_num:,} → {new_num:,} ({diff:,})")
            else:
                # 字符串类型
                if old_val is None:
                    changes.append(f"**{label}**: {new_val}")
                elif old_val != new_val:
                    changes.append(f"**{label}**: {old_val} → {new_val}")

        # 保存新数据
        history[user_id] = new_data
        self._save_history(history)

        return changes

    def log_crawl(self, user_id: str, user_info: Dict, video_count: int = 0, comment_count: int = 0):
        """记录一次爬取"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now.strftime("%Y年%m月%d日 %H:%M")

        # 准备数据（统一类型）
        crawl_data = {
            'nickname': user_info.get('nickname', '未知'),
            'ip_location': user_info.get('ip_location', '未知'),
            'follows': self._safe_int(user_info.get('follows', 0)),
            'fans': self._safe_int(user_info.get('fans', 0)),
            'interaction': self._safe_int(user_info.get('interaction', 0)),
            'videos_count': self._safe_int(user_info.get('videos_count', 0)),
            'unique_id': user_info.get('unique_id', ''),
            'desc': user_info.get('desc', ''),
            'last_crawl': timestamp
        }

        # 对比变化
        changes = self._compare_and_log(user_id, crawl_data)

        # 生成日志内容
        log_content = self._generate_log_content(
            date_str=date_str,
            user_id=user_id,
            user_info=crawl_data,
            changes=changes,
            video_count=video_count,
            comment_count=comment_count
        )

        # 写入日志文件
        self._write_log(log_content)

        utils.logger.info(f"[ChangeLogger] 日志已记录: {self.log_file}")

        return changes

    def _generate_log_content(self, date_str: str, user_id: str, user_info: Dict,
                            changes: List[str], video_count: int, comment_count: int) -> str:
        """生成日志内容"""
        # 使用抖音号（unique_id）显示
        display_id = user_info.get('unique_id', user_id)
        if not display_id:
            display_id = user_id[:20] + "..."

        # 获取去重统计
        dedup_info = ""
        try:
            from tools.dedup_manager import DedupManager
            dedup_dir = os.path.join(config.SAVE_DATA_PATH, "douyin")
            dedup_manager = DedupManager(dedup_dir)
            dedup_stats = dedup_manager.get_stats()
            dedup_info = f"- 📊 累计去重: 视频 {dedup_stats['video_count']} | 评论 {dedup_stats['comment_count']}"
        except:
            pass

        content = f"""
---

## 📅 {date_str}

### 👤 用户信息

| 项目 | 数据 |
|-----|------|
| 抖音号 | `{display_id}` |
| 昵称 | **{user_info.get('nickname', '未知')}** |
| IP属地 | {user_info.get('ip_location', '未知')} |
| 关注 | {user_info.get('follows', 0):,} |
| 粉丝 | {user_info.get('fans', 0):,} |
| 获赞 | {user_info.get('interaction', 0):,} |
| 视频数 | {user_info.get('videos_count', 0):,} |

### 📝 本次爬取数据

- 🎬 获取视频数: **{video_count}**
- 💬 获取评论数: **{comment_count}**
{dedup_info}

### 📊 数据变化

"""
        if changes:
            for change in changes:
                content += f"- {change}\n"
        else:
            content += "- 无变化（首次记录或数据相同）\n"

        content += f"""
### 📋 简介

{user_info.get('desc', '暂无简介')}

"""
        return content

    def _write_log(self, content: str):
        """写入日志文件"""
        try:
            # 如果文件不存在，创建并添加标题
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("# 📊 抖音用户数据变化记录\n\n")
                    f.write("> 自动记录每次爬取的数据变化\n\n")
                    f.write("---\n")

            # 追加内容
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            utils.logger.error(f"[ChangeLogger] 写入日志失败: {e}")

    def cleanup_old_logs(self, keep_days: int = 30):
        """清理旧日志（保留最近N天）"""
        try:
            if not os.path.exists(self.log_file):
                return

            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按日期分隔
            sections = content.split('\n---\n')

            # 只保留标题和最近N天的内容
            header = sections[0] if sections else ""
            recent_sections = []

            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)

            for section in sections[1:]:
                # 尝试解析日期
                try:
                    date_line = [l for l in section.split('\n') if '📅' in l]
                    if date_line:
                        # 提取日期字符串 "2026年06月25日 11:00"
                        date_str = date_line[0].split('📅')[-1].strip()
                        section_date = datetime.strptime(date_str, "%Y年%m月%d日 %H:%M")
                        if section_date.timestamp() > cutoff_date:
                            recent_sections.append(section)
                except:
                    recent_sections.append(section)

            # 重写文件
            new_content = header + '\n---\n'.join(recent_sections)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            utils.logger.info(f"[ChangeLogger] 已清理旧日志，保留最近 {keep_days} 天")

        except Exception as e:
            utils.logger.warning(f"[ChangeLogger] 清理日志失败: {e}")

    def get_summary(self) -> str:
        """获取数据摘要"""
        history = self._load_history()
        if not history:
            return "暂无历史数据"

        summary = "# 📊 数据摘要\n\n"
        for user_id, data in history.items():
            summary += f"## {data.get('nickname', '未知')}\n"
            summary += f"- 最后爬取: {data.get('last_crawl', '未知')}\n"
            summary += f"- 粉丝: {self._safe_int(data.get('fans', 0)):,}\n"
            summary += f"- 获赞: {self._safe_int(data.get('interaction', 0)):,}\n"
            summary += f"- 视频数: {self._safe_int(data.get('videos_count', 0)):,}\n\n"

        return summary
