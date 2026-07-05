# -*- coding: utf-8 -*-
"""
爬取完成后，将图片从 MediaCrawler 的 data 目录移动到对应的分类文件夹
用法: python move_images.py
"""
import json
import os
import shutil
import glob

# 小红书头像文件夹路径
XHS_BASE = r"C:\Users\LD\Desktop\winxin_photo\xiaohongshu"
# MediaCrawler 数据目录
DATA_DIR = r"C:\Users\LD\Desktop\winxin_photo\avatar_raw\MediaCrawler\data"
IMAGES_DIR = os.path.join(DATA_DIR, "xhs", "images")

# 关键词到文件夹名的映射: "古风头像" -> "古风"
KEYWORD_MAP = {
    "古风头像": "古风",
    "可爱头像": "可爱",
    "搞笑头像": "搞笑",
    "暗黑系头像": "暗黑系",
    "简约头像": "简约",
    "萌宠头像": "萌宠",
    "风景头像": "风景",
    "ins风格头像": "ins风格",
    "二次元头像": "二次元",
    "欧美风头像": "欧美风",
    "复古头像": "复古",
    "酷帅头像": "酷帅",
    "伤感头像": "伤感",
}


def find_jsonl_file():
    """查找最新的 JSONL 数据文件"""
    jsonl_files = glob.glob(os.path.join(DATA_DIR, "**", "*.jsonl"), recursive=True)
    if not jsonl_files:
        print("[X] No JSONL data file found")
        return None
    # 按修改时间排序，取最新的
    jsonl_files.sort(key=os.path.getmtime, reverse=True)
    print(f"[>] Data file: {jsonl_files[0]}")
    return jsonl_files[0]


def build_note_keyword_map(jsonl_path):
    """从 JSONL 文件中读取 note_id -> keyword 的映射"""
    note_keyword_map = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                note_id = data.get("note_id") or data.get("noteId") or data.get("id")
                keyword = data.get("source_keyword") or data.get("keyword") or data.get("search_keyword") or ""
                if note_id:
                    note_keyword_map[str(note_id)] = keyword
            except json.JSONDecodeError:
                continue
    print(f"[>] Total {len(note_keyword_map)} notes")
    return note_keyword_map


def move_images(note_keyword_map):
    """根据关键词将图片移动到对应文件夹"""
    if not os.path.exists(IMAGES_DIR):
        print(f"[X] Image directory not found: {IMAGES_DIR}")
        return

    moved_count = 0
    skipped_count = 0

    for note_id_dir in os.listdir(IMAGES_DIR):
        note_dir_path = os.path.join(IMAGES_DIR, note_id_dir)
        if not os.path.isdir(note_dir_path):
            continue

        keyword = note_keyword_map.get(note_id_dir, "")
        # 尝试匹配关键词到文件夹
        folder_name = KEYWORD_MAP.get(keyword)

        if not folder_name:
            # 尝试模糊匹配：去掉"头像"后缀
            for kw, fn in KEYWORD_MAP.items():
                if kw.replace("头像", "") in keyword or keyword in kw:
                    folder_name = fn
                    break

        if not folder_name:
            skipped_count += 1
            continue

        # 目标文件夹
        target_dir = os.path.join(XHS_BASE, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        # 移动图片
        for img_file in os.listdir(note_dir_path):
            src = os.path.join(note_dir_path, img_file)
            if not os.path.isfile(src):
                continue
            # 用 note_id 作为文件名前缀避免重名
            name, ext = os.path.splitext(img_file)
            new_name = f"{note_id_dir}_{name}{ext}"
            dst = os.path.join(target_dir, new_name)
            # 避免覆盖
            if os.path.exists(dst):
                base, extension = os.path.splitext(new_name)
                counter = 1
                while os.path.exists(dst):
                    dst = os.path.join(target_dir, f"{base}_{counter}{extension}")
                    counter += 1
            shutil.move(src, dst)
            moved_count += 1

    print(f"\n[OK] Done! Moved {moved_count} images, skipped {skipped_count} unmatched notes")


def main():
    print("=" * 50)
    print("  XHS Avatar Image Distributor")
    print("=" * 50)

    jsonl_path = find_jsonl_file()
    if not jsonl_path:
        return

    note_keyword_map = build_note_keyword_map(jsonl_path)
    if not note_keyword_map:
        print("[X] No note data found")
        return

    move_images(note_keyword_map)

    # 显示各文件夹图片数量
    print("\n[>] Folder stats:")
    for folder in KEYWORD_MAP.values():
        folder_path = os.path.join(XHS_BASE, folder)
        if os.path.exists(folder_path):
            count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            print(f"  {folder}: {count} 张")


if __name__ == "__main__":
    main()
