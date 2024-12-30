import requests
import json
import os
import platform
import uuid
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
import base64


class LicenseManager:
    def __init__(self):
        self.license_file = os.path.join(
            os.getenv("APPDATA"), "CursorPro", "license.json"
        )
        self.activation_url = (
            "https://your-activation-server.com/activate"  # 替换为您的激活服务器地址
        )
        self.verify_url = (
            "https://your-activation-server.com/verify"  # 替换为您的验证服务器地址
        )
        self.key = b"Kj8nP9x2Qs5mY7vR4wL1hC3fA6tD0iB8"
        self.fernet = Fernet(base64.b64encode(self.key))

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

            # 准备激活数据
            activation_data = {
                "license_key": license_key,
                "machine_code": machine_code,
                "activation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # 发送激活请求
            response = requests.post(
                self.activation_url, json=activation_data, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # 保存许可证信息
                    license_data = {
                        "license_key": license_key,
                        "machine_code": machine_code,
                        "activation_date": activation_data["activation_date"],
                        "expiry_date": result.get("expiry_date"),
                        "is_activated": True,
                    }

                    self._save_license(license_data)
                    return True, "激活成功！"
                else:
                    return False, result.get("message", "激活失败")
            else:
                return False, "服务器连接失败"

        except Exception as e:
            return False, f"激活过程出错: {str(e)}"

    def verify_license(self):
        """验证许可证"""
        try:
            if not os.path.exists(self.license_file):
                return False, "未找到许可证文件"

            license_data = self._load_license()
            if not license_data:
                return False, "许可证文件无效"

            # 验证机器码
            current_machine = self.get_hardware_info()
            if current_machine != license_data.get("machine_code"):
                return False, "硬件信息不匹配"

            # 在线验证
            verify_data = {
                "license_key": license_data.get("license_key"),
                "machine_code": current_machine,
            }

            response = requests.post(self.verify_url, json=verify_data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, "许可证有效"
                return False, result.get("message", "许可证无效")

            # 如果在线验证失败，使用本地数据
            expiry_date = datetime.strptime(license_data["expiry_date"], "%Y-%m-%d")
            if datetime.now() > expiry_date:
                return False, "许可证已过期"

            return True, "许可证有效"

        except Exception as e:
            return False, f"验证过程出错: {str(e)}"

    def _save_license(self, license_data):
        """加密保存许可证数据"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            encrypted_data = self.fernet.encrypt(json.dumps(license_data).encode())
            with open(self.license_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"保存许可证出错: {e}")

    def _load_license(self):
        """加密读取许可证数据"""
        try:
            with open(self.license_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"读取许可证出错: {e}")
            return None
