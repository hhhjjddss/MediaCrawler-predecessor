# -*- coding: utf-8 -*-
"""
媒体处理器
将图文格式的作品转换为视频
"""

import os
import subprocess
from typing import List, Optional
from tools import utils


class MediaProcessor:
    """媒体处理器"""

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self) -> Optional[str]:
        """查找 ffmpeg 路径"""
        # 常见的 ffmpeg 路径
        possible_paths = [
            "ffmpeg",
            "D:\\ffmpeg-2026-06-15-git-44d082edc8-essentials_build\\bin\\ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
        ]

        for path in possible_paths:
            try:
                subprocess.run([path, "-version"], capture_output=True, check=True)
                return path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return None

    def is_image_post(self, media_dir: str) -> bool:
        """判断是否为图文作品（有图片+音频MP4）"""
        files = os.listdir(media_dir)

        has_images = any(f.lower().endswith(('.jpg', '.jpeg', '.png')) for f in files)
        has_video = any(f.lower().endswith('.mp4') for f in files)

        if not has_images or not has_video:
            return False

        # 检查MP4是否为纯音频（无画面）
        video_path = os.path.join(media_dir, "video.mp4")
        if os.path.exists(video_path):
            return self._is_audio_only(video_path)

        return False

    def _is_audio_only(self, video_path: str) -> bool:
        """检查视频是否为纯音频（无画面）"""
        try:
            # ffprobe 与 ffmpeg 在同一目录
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe") if self.ffmpeg_path else "ffprobe"
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True)

            # 如果没有视频流，就是纯音频
            stdout = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
            return "video" not in stdout
        except:
            return False

    def get_image_files(self, media_dir: str) -> List[str]:
        """获取图片文件列表（按顺序）"""
        files = os.listdir(media_dir)
        image_files = []

        for f in sorted(files):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(os.path.join(media_dir, f))

        return image_files

    def get_audio_file(self, media_dir: str) -> Optional[str]:
        """获取音频文件"""
        video_path = os.path.join(media_dir, "video.mp4")
        if os.path.exists(video_path):
            return video_path
        return None

    def images_to_video(self, media_dir: str, output_name: str = "final_video.mp4", duration_per_image: float = 3.0) -> Optional[str]:
        """将图片和音频合并为视频"""
        if not self.ffmpeg_path:
            utils.logger.warning("[MediaProcessor] ffmpeg 未安装，无法处理图文作品")
            utils.logger.warning("[MediaProcessor] 请安装 ffmpeg: https://ffmpeg.org/download.html")
            return None

        image_files = self.get_image_files(media_dir)
        audio_file = self.get_audio_file(media_dir)

        if not image_files:
            utils.logger.warning("[MediaProcessor] 没有找到图片文件")
            return None

        output_path = os.path.join(media_dir, output_name)

        try:
            # 获取音频时长
            audio_duration = self._get_audio_duration(audio_file) if audio_file else len(image_files) * duration_per_image

            # 计算每张图片的显示时间
            duration_per_image = audio_duration / len(image_files)

            # 创建临时文件列表（使用绝对路径）
            list_file = os.path.join(media_dir, "filelist.txt")
            with open(list_file, 'w', encoding='utf-8') as f:
                for img in image_files:
                    # 使用绝对路径，避免路径问题
                    abs_path = os.path.abspath(img).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
                    f.write(f"duration {duration_per_image}\n")
                # 最后一张图片需要重复一次
                abs_path = os.path.abspath(image_files[-1]).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")

            # 构建 ffmpeg 命令（使用缩放滤镜确保图片尺寸一致）
            abs_list_file = os.path.abspath(list_file).replace('\\', '/')
            abs_output_path = os.path.abspath(output_path).replace('\\', '/')

            # 缩放滤镜：将所有图片缩放到 1280x720，保持宽高比并填充黑边
            scale_filter = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"

            if audio_file:
                # 有音频：图片+音频合成视频
                abs_audio = os.path.abspath(audio_file).replace('\\', '/')
                cmd = [
                    self.ffmpeg_path,
                    "-y",  # 覆盖输出文件
                    "-f", "concat",
                    "-safe", "0",
                    "-i", abs_list_file,
                    "-i", abs_audio,
                    "-vf", scale_filter,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    abs_output_path
                ]
            else:
                # 无音频：纯图片合成视频
                cmd = [
                    self.ffmpeg_path,
                    "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", abs_list_file,
                    "-vf", scale_filter,
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    abs_output_path
                ]

            # 执行命令
            result = subprocess.run(cmd, capture_output=True)

            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)

            if result.returncode == 0:
                utils.logger.info(f"[MediaProcessor] 视频合成成功: {output_path}")
                return output_path
            else:
                # 处理错误信息编码
                stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "未知错误"
                utils.logger.error(f"[MediaProcessor] 视频合成失败: {stderr}")
                return None

        except Exception as e:
            utils.logger.error(f"[MediaProcessor] 视频合成异常: {e}")
            return None

    def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长（秒）"""
        try:
            # ffprobe 与 ffmpeg 在同一目录
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe") if self.ffmpeg_path else "ffprobe"
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True)
            stdout = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
            return float(stdout.strip())
        except:
            return 30.0  # 默认30秒


# 全局实例
media_processor = MediaProcessor()
