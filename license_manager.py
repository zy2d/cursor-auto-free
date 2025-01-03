import requests
import json
import os
import platform
import uuid
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import time
from Crypto.Cipher import AES
import binascii


class LicenseManager:
    def __init__(self):
        # 根据不同操作系统获取适当的配置目录
        if platform.system() == "Windows":
            config_dir = os.getenv("APPDATA")
        elif platform.system() == "Darwin":  # macOS
            config_dir = os.path.expanduser("~/Library/Application Support")
        else:  # Linux 和其他类 Unix 系统
            config_dir = os.path.expanduser("~/.config")

        self.license_file = os.path.join(config_dir, "CursorPro", "license.json")
        # self.activation_url = "http://cursor.chengazhen.me/activate"
        # self.verify_url = "http://cursor.chengazhen.me/verify"
        self.activation_url = "http://119.8.35.41:3004/activate"
        self.verify_url = "http://119.8.35.41:3004/verify"
        self.key = b"Kj8nP9x2Qs5mY7vR4wL1hC3fA6tD0iB8"
        self.encryption_key = b"f1e2d3c4b5a6978899aabbccddeeff00112233445566778899aabbccddeeff00"  # 与服务器端相同的密钥

    def encrypt(self, text):
        """使用AES-256-CBC加密"""
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.key[:16]),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()

        # 添加PKCS7填充
        length = 16 - (len(text) % 16)
        text += bytes([length]) * length

        encrypted = encryptor.update(text) + encryptor.finalize()
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_text):
        """使用AES-256-CBC解密"""
        encrypted = base64.b64decode(encrypted_text)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.key[:16]),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()

        decrypted = decryptor.update(encrypted) + decryptor.finalize()

        # 移除PKCS7填充
        padding_length = decrypted[-1]
        return decrypted[:-padding_length]

    def get_hardware_info(self):
        """获取硬件信息作为机器码"""
        system_info = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

        # 获取MAC地址
        mac = ":".join(
            [
                "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                for elements in range(0, 2 * 6, 2)
            ][::-1]
        )
        system_info["mac"] = mac

        # 生成机器码
        machine_code = hashlib.md5(json.dumps(system_info).encode()).hexdigest()
        return machine_code

    def activate_license(self, license_key):
        """在线激活许可证"""
        try:
            machine_code = self.get_hardware_info()
            activation_data = {
                "license_key": license_key,
                "machine_code": machine_code,
                "activation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            try:
                response = requests.post(
                    self.activation_url, json=activation_data, timeout=10
                )
                if response.status_code == 200:
                    try:
                        encrypted_response = response.json()
                        result = self.decrypt_response(
                            encrypted_response["encrypted_data"]
                        )
                        if result.get("code") == 0:
                            license_data = {
                                "license_key": license_key,
                                "machine_code": machine_code,
                                "activation_date": activation_data["activation_date"],
                                "expiry_date": result.get("data").get("expiry_date"),
                                "is_active": True,
                            }
                            self._save_license(license_data)
                            return True, "激活成功！"
                        else:
                            error_msg = result.get("message", "激活失败")
                            return False, error_msg
                    except Exception as e:
                        return False, f"解密响应失败: {str(e)}"

                else:
                    return False, f"服务器响应错误: HTTP {response.status_code}"

            except requests.exceptions.ConnectionError:
                return False, "无法连接到激活服务器，请检查网络连接"
            except requests.exceptions.Timeout:
                return False, "服务器响应超时"
            except Exception as e:
                return False, f"激活请求失败: {str(e)}"

        except Exception as e:
            return False, f"激活过程出错: {str(e)}"

    def decrypt_response(self, encrypted_data):
        """解密服务器响应的数据"""
        try:
            # 分离 IV 和加密数据
            iv_hex, encrypted_text = encrypted_data.split(":")

            # 将十六进制转换为字节
            iv = binascii.unhexlify(iv_hex)
            encrypted_bytes = binascii.unhexlify(encrypted_text)

            # 创建解密器
            cipher = AES.new(binascii.unhexlify(self.encryption_key), AES.MODE_CBC, iv)

            # 解密数据
            decrypted_bytes = cipher.decrypt(encrypted_bytes)

            # 移除填充
            padding_length = decrypted_bytes[-1]
            decrypted_data = decrypted_bytes[:-padding_length]

            # 转换为字符串并解析 JSON
            decrypted_str = decrypted_data.decode("utf-8")
            return json.loads(decrypted_str)

        except Exception as e:
            raise Exception(f"解密失败: {str(e)}")

    def verify_license(self):
        """验证许可证"""
        try:
            if not os.path.exists(self.license_file):
                return False, "未找到许可证文件"

            license_data = self._load_license()
            if not license_data:
                return False, "许可证文件无效"

            current_machine = self.get_hardware_info()
            if current_machine != license_data.get("machine_code"):
                return False, "硬件信息不匹配"

            verify_data = {
                "license_key": license_data.get("license_key"),
                "machine_code": current_machine,
            }

            try:
                response = requests.post(self.verify_url, json=verify_data, timeout=30)
                time.sleep(2)

                if response.status_code == 200:
                    try:
                        encrypted_response = response.json()
                        result = self.decrypt_response(
                            encrypted_response["encrypted_data"]
                        )
                        if result.get("code") == 0:
                            return True, "许可证有效"
                        return False, result.get("message", "许可证无效")
                    except Exception as e:
                        return False, f"解密响应失败: {str(e)}"

                return False, f"服务器响应错误: HTTP {response.status_code}"

            except requests.exceptions.ConnectionError:
                return False, "无法连接到验证服务器，请检查网络连接"
            except requests.exceptions.Timeout:
                return False, "服务器响应超时"
            except Exception as e:
                return False, f"验证请求失败: {str(e)}"

        except Exception as e:
            return False, f"验证过程出错: {str(e)}"

    def _save_license(self, license_data):
        """加密保存许可证数据"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            encrypted_data = self.encrypt(json.dumps(license_data).encode())
            with open(self.license_file, "w") as f:
                f.write(encrypted_data)
        except Exception as e:
            pass

    def _load_license(self):
        """加密读取许可证数据"""
        try:
            with open(self.license_file, "r") as f:
                encrypted_data = f.read()
            decrypted_data = self.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return None
