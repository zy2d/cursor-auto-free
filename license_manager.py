import json
import os


class LicenseManager:
    def __init__(self):
        self.license_file = os.path.join(
            os.getenv("APPDATA"), "CursorPro", "license.json"
        )
        self.max_uses = 10  # 最大使用次数

    def check_license(self):
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)

            if not os.path.exists(self.license_file):
                # 首次运行，创建许可文件
                license_data = {"use_count": 0, "is_activated": False}
                with open(self.license_file, "w") as f:
                    json.dump(license_data, f)
                return True

            # 读取许可信息
            with open(self.license_file, "r") as f:
                license_data = json.load(f)

            if license_data.get("is_activated"):
                return True

            # 检查使用次数
            use_count = license_data.get("use_count", 0)
            if use_count >= self.max_uses:
                return False

            # 增加使用次数并保存
            license_data["use_count"] = use_count + 1
            with open(self.license_file, "w") as f:
                json.dump(license_data, f)

            return True

        except Exception as e:
            print(f"License check error: {e}")
            return False
