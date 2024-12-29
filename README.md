

# Cursor Pro 自动化工具使用说明

## 功能介绍
本工具可以自动化完成 Cursor Pro 账号的删除和重新注册流程，支持自动验证码处理和本地认证更新。


## 重要提示
**1.确保你有一个chrome浏览器；**

**2.随机邮箱尽量自己命名，比如你的名字叫彭于晏，那你的邮箱名就是 pengyuyan@mailto.plus，如果你感觉很多人跟你同名，那你就加点字母**

**3.有一个稳定的网络连接。尽量是国外的节点。**



## 使用前准备


1. 配置文件设置
在与应用相同目录下创建 `config.ini` 文件：
```ini
[Account]
email = your_email@tempmail.plus    # 必须使用 tempmail.plus 的邮箱
password = your_password            # 设置登录密码
first_name = your_first_name        # 英文名
last_name = your_last_name          # 英文姓
```

2. 确保文件结构：
```
应用目录/
├── CursorPro.app (Mac) 或 CursorPro.exe (Windows)
├── config.ini
└── turnstilePatch/    # 验证插件目录
```

## 运行方法

### Mac 版本
1. 打开终端，进入应用所在目录
2. 运行命令：授权文件可以执行
```bash
chmod +x ./CursorPro
```
3. 运行程序：
   - 在终端中运行：
```bash
./CursorPro
```
   - 或直接在访达（Finder）中双击运行

### Windows 版本
直接双击运行 `CursorPro.exe`

## 使用注意事项

1. 运行环境要求：
   - 稳定的网络连接
   - 足够的系统权限

2. 使用过程中：
   - 请勿手动关闭浏览器窗口
   - 等待程序自动完成所有操作
   - 看到"脚本执行完毕"提示后再关闭程序

3. 重要提示：
   - 确保 config.ini 配置正确
   - 邮箱必须是 tempmail.plus 的临时邮箱
   - 运行过程中请勿操作鼠标和键盘

## 常见问题解决

1. 提示"配置文件不存在"：
   - 检查 config.ini 是否在正确位置
   - 确保配置文件格式正确

2. 程序运行过程中卡住：
   - 检查网络连接
   - 重启程序重试
   - 你的邮箱可能是一个无效邮箱


## 免责声明
本工具仅供学习研究使用，请遵守相关服务条款。使用本工具产生的任何后果由使用者自行承担。
