# -*- coding: utf-8 -*-
"""
定时爬虫脚本
支持：立即爬取、每天定时、每周定时
"""

import sys
import io
import asyncio
import os
import time
import schedule
from datetime import datetime

# Force UTF-8 encoding
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import config
from tools import utils


# 要爬取的用户列表（在此填入你的目标用户主页链接）
TARGET_USERS = [
    # "https://www.douyin.com/user/xxxxxxxxx?from_tab_name=main",
    # "https://www.douyin.com/user/yyyyyyy?from_tab_name=main",
]


async def crawl_users():
    """爬取所有用户"""
    from playwright.async_api import async_playwright
    from media_platform.douyin.client import DouYinClient
    from media_platform.douyin.login import DouYinLogin
    from media_platform.douyin.new_core import NewDouyinCrawler
    from media_platform.douyin.help import parse_creator_info_from_url
    from tools.cdp_browser import CDPBrowserManager

    utils.logger.info("=" * 60)
    utils.logger.info(f"开始爬取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    utils.logger.info("=" * 60)

    # 启动浏览器
    utils.logger.info("启动浏览器...")

    async with async_playwright() as playwright:
        # 选择启动模式
        if config.ENABLE_CDP_MODE:
            utils.logger.info("使用CDP模式启动浏览器")
            cdp_manager = CDPBrowserManager()
            browser_context = await cdp_manager.launch_and_connect(
                playwright=playwright,
                playwright_proxy=None,
                user_agent=None,
                headless=config.CDP_HEADLESS,
            )
            await cdp_manager.add_stealth_script()
        else:
            utils.logger.info("使用标准模式启动浏览器")
            chromium = playwright.chromium
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=os.path.join(os.getcwd(), "browser_data", "dy_user_data_dir"),
                accept_downloads=True,
                headless=config.HEADLESS,
                viewport={"width": 1920, "height": 1080},
            )
            await browser_context.add_init_script(path="libs/stealth.min.js")

        # 创建页面
        context_page = await browser_context.new_page()
        await context_page.goto("https://www.douyin.com")

        # 创建客户端
        cookie_urls = [
            "https://douyin.com",
            "https://www.douyin.com",
            "https://creator.douyin.com",
            "https://douhot.douyin.com",
            "https://live.douyin.com",
        ]

        from tools.utils import convert_browser_context_cookies
        cookie_str, cookie_dict = await convert_browser_context_cookies(
            browser_context,
            urls=cookie_urls,
        )

        dy_client = DouYinClient(
            proxy=None,
            headers={
                "User-Agent": await context_page.evaluate("() => navigator.userAgent"),
                "Cookie": cookie_str,
                "Host": "www.douyin.com",
                "Origin": "https://www.douyin.com/",
                "Referer": "https://www.douyin.com/",
                "Content-Type": "application/json;charset=UTF-8",
            },
            playwright_page=context_page,
            cookie_dict=cookie_dict,
        )

        # 检查登录状态
        if not await dy_client.pong(browser_context=browser_context):
            utils.logger.info("需要登录...")
            login_obj = DouYinLogin(
                login_type=config.LOGIN_TYPE,
                login_phone="",
                browser_context=browser_context,
                context_page=context_page,
                cookie_str=config.COOKIES,
            )
            await login_obj.begin()
            await dy_client.update_cookies(
                browser_context=browser_context,
                urls=cookie_urls,
            )

        utils.logger.info("登录成功！开始爬取...")

        # 使用新版爬虫逻辑
        new_crawler = NewDouyinCrawler(dy_client)

        # 逐个爬取用户
        success_count = 0
        skip_count = 0
        fail_count = 0

        for creator_url in TARGET_USERS:
            try:
                creator_info_parsed = parse_creator_info_from_url(creator_url)
                user_id = creator_info_parsed.sec_user_id
                utils.logger.info(f"开始爬取用户: {creator_url[:50]}...")
                utils.logger.info(f"解析到 user_id: {user_id}")

                # 尝试获取用户信息
                creator_info = await dy_client.get_user_info(user_id)
                if not creator_info:
                    utils.logger.warning(f"用户不存在或已私密，跳过: {user_id}")
                    skip_count += 1
                    continue

                user_info = creator_info.get("user", {})
                nickname = user_info.get("nickname", "未知")

                # 检查是否私密账户
                if user_info.get("is_private", False):
                    utils.logger.warning(f"用户 {nickname} 已设置私密，跳过")
                    skip_count += 1
                    continue

                # 爬取用户
                await new_crawler.crawl_user(user_id)
                success_count += 1
                utils.logger.info(f"用户 {nickname} 爬取完成")

            except Exception as e:
                utils.logger.error(f"爬取用户失败: {creator_url[:50]}..., 错误: {str(e) if str(e) else '未知错误'}")
                fail_count += 1
                continue

        # 关闭浏览器
        utils.logger.info("关闭浏览器...")
        try:
            if config.ENABLE_CDP_MODE:
                await cdp_manager.cleanup()
            else:
                await browser_context.close()
        except Exception as e:
            utils.logger.warning(f"关闭浏览器时出错: {e}")

        # 输出统计
        utils.logger.info("=" * 60)
        utils.logger.info(f"爬取完成！")
        utils.logger.info(f"成功: {success_count} | 跳过: {skip_count} | 失败: {fail_count}")
        utils.logger.info(f"数据保存位置: {config.SAVE_DATA_PATH}/douyin/")
        utils.logger.info("=" * 60)


def run_crawler():
    """运行爬虫（同步包装）"""
    asyncio.run(crawl_users())


def main():
    """主函数"""
    print("=" * 60)
    print("抖音定时爬虫")
    print("=" * 60)
    print("\n请选择爬取模式：")
    print("1. 立即爬取")
    print("2. 每天 00:00 爬取")
    print("3. 每周一 00:00 爬取")
    print("4. 自定义时间")
    print("0. 退出")

    choice = input("\n请输入选择 (0-4): ").strip()

    if choice == "1":
        print("\n立即开始爬取...")
        run_crawler()

    elif choice == "2":
        print("\n已设置每天 00:00 自动爬取")
        print("按 Ctrl+C 停止\n")
        schedule.every().day.at("00:00").do(run_crawler)

        # 立即运行一次
        run_now = input("是否立即运行一次？(y/n): ").strip().lower()
        if run_now == 'y':
            run_crawler()

        while True:
            schedule.run_pending()
            time.sleep(60)

    elif choice == "3":
        print("\n已设置每周一 00:00 自动爬取")
        print("按 Ctrl+C 停止\n")
        schedule.every().monday.at("00:00").do(run_crawler)

        # 立即运行一次
        run_now = input("是否立即运行一次？(y/n): ").strip().lower()
        if run_now == 'y':
            run_crawler()

        while True:
            schedule.run_pending()
            time.sleep(60)

    elif choice == "4":
        print("\n自定义时间设置")
        print("格式示例：")
        print("  - 每天 08:30: 08:30")
        print("  - 每周一 09:00: monday:09:00")
        print("  - 每小时整点: every_hour")

        time_str = input("\n请输入时间: ").strip()

        if ":" in time_str and len(time_str.split(":")) == 2:
            # 每天定时
            print(f"\n已设置每天 {time_str} 自动爬取")
            print("按 Ctrl+C 停止\n")
            schedule.every().day.at(time_str).do(run_crawler)
        elif time_str.startswith("monday:"):
            # 每周一
            t = time_str.split(":")[1] + ":" + time_str.split(":")[2]
            print(f"\n已设置每周一 {t} 自动爬取")
            print("按 Ctrl+C 停止\n")
            schedule.every().monday.at(t).do(run_crawler)
        elif time_str == "every_hour":
            print("\n已设置每小时自动爬取")
            print("按 Ctrl+C 停止\n")
            schedule.every().hour.do(run_crawler)
        else:
            print("时间格式错误！")
            return

        # 立即运行一次
        run_now = input("是否立即运行一次？(y/n): ").strip().lower()
        if run_now == 'y':
            run_crawler()

        while True:
            schedule.run_pending()
            time.sleep(60)

    elif choice == "0":
        print("退出")
        return

    else:
        print("无效选择！")


if __name__ == "__main__":
    main()
