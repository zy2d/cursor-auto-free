import os

from license_manager import LicenseManager

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

import re
import time
import random
from cursor_auth_manager import CursorAuthManager
import os
import sys
import logging
from browser_utils import BrowserManager
from get_veri_code import EmailVerificationHandler

# 在文件开头设置日志
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cursor_keep_alive.log", encoding="utf-8"),
    ],
)


def handle_turnstile(tab):
    """处理 Turnstile 验证"""
    print("准备处理验证")
    try:
        while True:
            try:
                challengeCheck = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challengeCheck:
                    print("验证框加载完成")
                    time.sleep(random.uniform(1, 3))
                    challengeCheck.click()
                    print("验证按钮已点击，等待验证完成...")
                    time.sleep(2)
                    return True
            except:
                pass

            if tab.ele("@name=password"):
                print("无需验证")
                break
            if tab.ele("@data-index=0"):
                print("无需验证")
                break
            if tab.ele("Account Settings"):
                print("无需验证")
                break

            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(e)
        print("跳过验证")
        return False


def delete_account(browser, tab):
    """删除账户流程"""
    print("\n开始删除账户...")

    try:
        if tab.ele("@name=email"):
            tab.ele("@name=email").input(account)
            print("输入账号")
            time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"输入账号失败: {str(e)}")

    try:
        if tab.ele("Continue"):
            tab.ele("Continue").click()
            print("点击Continue")
    except Exception as e:
        print(f"点击Continue失败: {str(e)}")

    handle_turnstile(tab)
    time.sleep(5)

    try:
        if tab.ele("@name=password"):
            tab.ele("@name=password").input(password)
            print("输入密码")
            time.sleep(random.uniform(1, 3))

    except Exception as e:
        print("输入密码失败")

    sign_in_button = tab.ele(
        "xpath:/html/body/div[1]/div/div/div[2]/div/form/div/button"
    )
    try:
        if sign_in_button:
            sign_in_button.click(by_js=True)
            print("点击Sign in")
    except Exception as e:
        print(f"点击Sign in失败: {str(e)}")

    handle_turnstile(tab)

    # 处理验证码
    while True:
        try:
            if tab.ele("Invalid email or password"):
                print("Invalid email or password")
                return False
            if tab.ele("Account Settings"):
                break
            if tab.ele("@data-index=0"):
                code = email_handler.get_verification_code(account)

                if code:
                    print("获取验证码成功：", code)
                else:
                    print("获取验证码失败，程序退出")
                    return False

                i = 0
                for digit in code:
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                    i += 1
                break
        except Exception as e:
            print(e)

    handle_turnstile(tab)
    time.sleep(5)
    tab.get(settings_url)
    print("进入设置页面")

    try:
        if tab.ele("@class=mt-1"):
            tab.ele("@class=mt-1").click()
            print("点击Adavance")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"点击Adavance失败: {str(e)}")

    try:
        if tab.ele("Delete Account"):
            tab.ele("Delete Account").click()
            print("点击Delete Account")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"点击Delete Account失败: {str(e)}")

    try:
        if tab.ele("tag:input"):
            tab.actions.click("tag:input").type("delete")
            print("输入delete")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"输入delete失败: {str(e)}")

    delete_button = tab.ele(
        "xpath:/html/body/main/div/div/div/div/div/div[1]/div[2]/div[3]/div[2]/div/div/div[2]/button[2]"
    )
    try:
        if delete_button:
            print("点击Delete")
            delete_button.click()
            time.sleep(5)
            # tab.get_screenshot('delete_account.png')
            # print("删除账户截图")
            return True
    except Exception as e:
        print(f"点击Delete失败: {str(e)}")
        return False


def get_cursor_session_token(tab, max_attempts=3, retry_interval=2):
    """
    获取Cursor会话token，带有重试机制
    :param tab: 浏览器标签页
    :param max_attempts: 最大尝试次数
    :param retry_interval: 重试间隔(秒)
    :return: session token 或 None
    """
    print("开始获取cookie")
    attempts = 0

    while attempts < max_attempts:
        try:
            cookies = tab.cookies()
            for cookie in cookies:
                if cookie.get("name") == "WorkosCursorSessionToken":
                    return cookie["value"].split("%3A%3A")[1]

            attempts += 1
            if attempts < max_attempts:
                print(
                    f"第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试..."
                )
                time.sleep(retry_interval)
            else:
                print(f"已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败")

        except Exception as e:
            print(f"获取cookie失败: {str(e)}")
            attempts += 1
            if attempts < max_attempts:
                print(f"将在 {retry_interval} 秒后重试...")
                time.sleep(retry_interval)

    return None


def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新Cursor的认证信息的便捷函数
    """
    auth_manager = CursorAuthManager()
    return auth_manager.update_auth(email, access_token, refresh_token)


def sign_up_account(browser, tab):
    print("\n开始注册新账户...")
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            print("已打开注册页面")
            tab.actions.click("@name=first_name").input(first_name)
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=last_name").input(last_name)
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=email").input(account)
            print("输入邮箱")
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@type=submit")
            print("点击注册按钮")

    except Exception as e:
        print("打开注册页面失败")
        return False

    handle_turnstile(tab)

    try:
        if tab.ele("@name=password"):
            tab.ele("@name=password").input(password)
            print("输入密码")
            time.sleep(random.uniform(1, 3))

            tab.ele("@type=submit").click()
            print("点击Continue按钮")

    except Exception as e:
        print("输入密码失败")
        return False

    time.sleep(random.uniform(1, 3))
    if tab.ele("This email is not available."):
        print("This email is not available.")
        return False

    handle_turnstile(tab)

    while True:
        try:
            if tab.ele("Account Settings"):
                break
            if tab.ele("@data-index=0"):
                code = email_handler.get_verification_code(account)
                if not code:
                    return False

                i = 0
                for digit in code:
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                    i += 1
                break
        except Exception as e:
            print(e)

    handle_turnstile(tab)
    time.sleep(8)
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
            print("可用上限: " + total_usage)
    except Exception as e:
        print("获取可用上限失败")
    # tab.get_screenshot("sign_up_success.png")
    # print("注册账户截图")
    print("注册完成")
    print("Cursor 账号： " + account)
    print("       密码： " + password)
    time.sleep(5)
    return True


def cleanup_temp_files():
    """清理临时文件和缓存"""
    try:
        temp_dirs = [
            os.path.join(os.getcwd(), "__pycache__"),
            os.path.join(os.getcwd(), "build"),
        ]

        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                import shutil

                shutil.rmtree(dir_path)
    except Exception as e:
        logging.warning(f"清理临时文件失败: {str(e)}")


class EmailGenerator:
    def __init__(
        self,
        domain="mailto.plus",
        password="".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                k=12,
            )
        ),
        first_name="yuyan",
        last_name="peng",
    ):
        self.domain = domain
        self.default_password = password
        self.default_first_name = first_name
        self.default_last_name = last_name

    def generate_email(self, length=8):
        """生成随机邮箱地址"""
        random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
        timestamp = str(int(time.time()))[-6:]  # 使用时间戳后6位
        return f"{random_str}{timestamp}@{self.domain}"

    def get_account_info(self):
        """获取完整的账号信息"""
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }


if __name__ == "__main__":
    browser_manager = None
    try:
        license_manager = LicenseManager()

        # 验证许可证
        is_valid, message = license_manager.verify_license()
        if not is_valid:
            print(f"许可证验证失败: {message}")
            # 提示用户激活
            license_key = input("请输入激活码: ")
            success, activate_message = license_manager.activate_license(license_key)
            if not success:
                print(f"激活失败: {activate_message}")
                sys.exit(1)
            print("激活成功！")

        # 初始化浏览器
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()

        # 初始化邮箱验证处理器
        email_handler = EmailVerificationHandler(browser)

        # 固定的 URL 配置
        login_url = "https://authenticator.cursor.sh"
        sign_up_url = "https://authenticator.cursor.sh/sign-up"
        settings_url = "https://www.cursor.com/settings"
        mail_url = "https://tempmail.plus"

        # 生成随机邮箱
        email_generator = EmailGenerator()
        account = email_generator.generate_email()
        password = email_generator.default_password
        first_name = email_generator.default_first_name
        last_name = email_generator.default_last_name

        auto_update_cursor_auth = True

        tab = browser.latest_tab
        tab.run_js("try { turnstile.reset() } catch(e) { }")

        tab.get(login_url)

        if sign_up_account(browser, tab):
            token = get_cursor_session_token(tab)
            if token:
                update_cursor_auth(
                    email=account, access_token=token, refresh_token=token
                )
            else:
                print("账户注册失败")

        print("脚本执行完毕")

    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        import traceback

        logging.error(traceback.format_exc())
    finally:
        if browser_manager:
            browser_manager.quit()
        input("\n按回车键退出...")
