# -*- coding: utf-8 -*-
"""
新版抖音爬虫入口
按用户→作品组织数据
"""

import sys
import io
import asyncio
import os

# Force UTF-8 encoding
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import config
from tools import utils


async def main():
    """主函数"""
    utils.logger.info("=" * 60)
    utils.logger.info("新版抖音爬虫启动")
    utils.logger.info("=" * 60)

    # 检查配置
    if not config.DY_CREATOR_ID_LIST:
        utils.logger.error("未配置要爬取的用户，请在 config/dy_config.py 中设置 DY_CREATOR_ID_LIST")
        return

    from playwright.async_api import async_playwright
    from media_platform.douyin.client import DouYinClient
    from media_platform.douyin.login import DouYinLogin
    from media_platform.douyin.new_core import NewDouyinCrawler
    from media_platform.douyin.help import parse_creator_info_from_url
    from tools.cdp_browser import CDPBrowserManager

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

        for creator_url in config.DY_CREATOR_ID_LIST:
            try:
                creator_info_parsed = parse_creator_info_from_url(creator_url)
                user_id = creator_info_parsed.sec_user_id
                utils.logger.info(f"开始爬取用户: {creator_url}")

                # 使用新版爬虫爬取
                await new_crawler.crawl_user(user_id)

            except Exception as e:
                utils.logger.error(f"爬取用户失败: {creator_url}, 错误: {e}")
                continue

        utils.logger.info("=" * 60)
        utils.logger.info("爬取完成！")
        utils.logger.info(f"数据保存位置: {config.SAVE_DATA_PATH}/douyin/")
        utils.logger.info("=" * 60)

        # 关闭浏览器
        if config.ENABLE_CDP_MODE:
            await cdp_manager.cleanup()
        else:
            await browser_context.close()


if __name__ == "__main__":
    asyncio.run(main())
