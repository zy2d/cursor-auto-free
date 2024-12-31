from Crypto.Cipher import AES
import json
import binascii


class ResponseDecryptor:
    def __init__(self, encryption_key):
        """
        初始化解密器
        :param encryption_key: 十六进制格式的密钥字符串
        """
        # 将十六进制字符串转换为字节
        self.key = binascii.unhexlify(encryption_key)

    def decrypt_response(self, encrypted_data):
        """
        解密服务器响应的数据
        :param encrypted_data: 加密的数据字符串 (格式: "iv:encrypted")
        :return: 解密后的 JSON 数据
        """
        try:
            # 分离 IV 和加密数据
            iv_hex, encrypted_text = encrypted_data.split(":")

            # 将十六进制转换为字节
            iv = binascii.unhexlify(iv_hex)
            encrypted_bytes = binascii.unhexlify(encrypted_text)

            # 创建解密器
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

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


# 使用示例
def main():
    # 这里填入与服务器相同的加密密钥（十六进制格式）
    ENCRYPTION_KEY = "f1e2d3c4b5a6978899aabbccddeeff00112233445566778899aabbccddeeff00"  # 替换为实际的密钥

    # 创建解密器实例
    decryptor = ResponseDecryptor(ENCRYPTION_KEY)

    # 模拟服务器响应
    server_response = {
        "encrypted_data": "iv_hex:encrypted_data_hex"  # 这里是服务器返回的加密数据
    }

    try:
        # 解密数据
        decrypted_data = decryptor.decrypt_response(server_response["encrypted_data"])
        print("解密后的数据:", decrypted_data)

        # 现在可以访问解密后的数据
        if decrypted_data.get("success"):
            print("操作成功!")
            # 处理其他数据...
        else:
            print("操作失败:", decrypted_data.get("message"))

    except Exception as e:
        print("错误:", str(e))
