from DrissionPage import ChromiumOptions, Chromium
import random
import time

def handle_turnstile(tab):
    """处理 Turnstile 验证"""
    print("准备处理验证")
    try:
        while True:              
            if tab.ele('@id=email-input', timeout=2):
                print("无需验证 - 邮箱输入框已加载")
                return True
                
            if tab.ele('@id=password', timeout=2):
                print("无需验证 - 密码输入框已加载")
                return True
            
            try:
                challenge_element = (tab.ele("@name=cf-turnstile-response", timeout=2)
                                    .parent()
                                    .shadow_root
                                    .ele("tag:iframe")
                                    .ele("tag:body")
                                    .sr("tag:input"))
                                    
                if challenge_element:
                    print("验证框加载完成")
                    time.sleep(random.uniform(1, 3))
                    challenge_element.click()
                    print("验证按钮已点击，等待验证完成...")
                    time.sleep(2)
                    return True
            except:
                pass
                
            time.sleep(2)
            
    except Exception as e:
        print(f"验证处理出错: {str(e)}")
        print('跳过验证')
        return False

account = 'your_chatgpt_account'
password = 'your_chatgpt_password'

co = ChromiumOptions()
co.add_extension("turnstilePatch") 
# co.headless()
co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36')
co.set_pref('credentials_enable_service', False)
co.set_argument('--hide-crash-restore-bubble') 
co.auto_port()

browser = Chromium(co)
tab = browser.latest_tab
tab.run_js("try { turnstile.reset() } catch(e) { }")

print("\n步骤1: 开始访问网站...")

tab.get('https://chatgpt.com')
print('等待页面加载...')

print("\n步骤2: 开始登录...")
for _ in range(5):
    try:
        if tab.ele('xpath:/html/body/div[1]/div[1]/main/div[1]/div[1]/div/div[1]/div/div[3]/div/button[1]'):
            signin_btn = tab.ele('xpath:/html/body/div[1]/div[1]/main/div[1]/div[1]/div/div[1]/div/div[3]/div/button[1]')
            print("找到黑色登录按钮:", signin_btn.text)
            break
        if tab.ele('@data-testid=login-button'):
            signin_btn = tab.ele('@data-testid=login-button')
            print("找到蓝色登录按钮:", signin_btn.text)
            break
        if tab.ele("@name=cf-turnstile-response"):
            print('加载页面时出现CF验证, IP 质量太差, 请更换 IP 重新尝试!')
            browser.quit()
            exit()  
        time.sleep(3)  
    except Exception as e:
        print(f"处理登录按钮时出错: {str(e)}")

for _ in range(5):
    try:
        if signin_btn:
            signin_btn.click()
            print("点击登录按钮")
            break
    except Exception as e:
        print(f"处理登录按钮时出错: {str(e)}")
    time.sleep(3)
else:
    print("尝试点击登录按钮失败，程序退出")
    exit()

handle_turnstile(tab)
    
print("\n步骤3: 输入邮箱...")
for _ in range(5):
    try:
        if tab.ele('@id=email-input'):
            tab.actions.click('@id=email-input').type(account)
            time.sleep(0.5)
            tab.ele('@class=continue-btn').click()
            print("输入邮箱并点击继续")
            break
    except Exception as e:
        print(f"加载邮箱输入框时出错: {str(e)}")
    time.sleep(3)
else:
    print("尝试加载邮箱输入框失败，程序退出")
    browser.quit()
    exit()

handle_turnstile(tab)

print("\n步骤4: 输入密码...")
for _ in range(5):
    try:
        if tab.ele('@id=password'):
            print("密码输入框加载完成")
            tab.actions.click('@id=password').input(password)
            time.sleep(2)
            tab.ele('@type=submit').click('js')
            # tab.actions.click('@type=submit')
            print("输入密码并JS点击登录")
            break
    except Exception as e:
        print(f"输入密码时出错: {str(e)}")
    time.sleep(3)
else:
    print("尝试加载密码输入框失败，程序退出")
    browser.quit()
    exit()

for _ in range(5):
    try:
        if tab.ele('有什么可以帮忙的？'):
            print('登录成功！')
            break
        if tab.ele('重新发送电子邮件'): 
            print('提示需要邮箱验证码，脚本终止，请手动获取')
            exit()                                      
    except Exception as e:
        print(f"登录可能遇到问题: {str(e)}")
    time.sleep(3)
else:
    print("登录失败，程序退出")
    browser.quit()
    exit()

time.sleep(random.uniform(1,2))
print('\n',"步骤5: 获取access_token...")
browser.new_tab('https://chatgpt.com/api/auth/session')
tab = browser.latest_tab
time.sleep(1)
response_json = tab.json
if response_json and 'accessToken' in response_json:
    access_token = response_json['accessToken']
    print('\n',"请复制保存你的access_token:",'\n')
    print(access_token)
else:
    print("错误:未找到access token")

# input("\n按Enter键关闭浏览器...")
browser.quit()
  
