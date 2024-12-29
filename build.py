import os
import platform
import subprocess


def build():
    system = platform.system().lower()
    spec_file = "CursorKeepAlive.spec"

    if system not in ["darwin", "windows"]:
        print(f"不支持的操作系统: {system}")
        return

    output_dir = f"dist/{system if system != 'darwin' else 'mac'}"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 运行 PyInstaller
    subprocess.run(
        [
            "pyinstaller",
            spec_file,
            "--distpath",
            output_dir,
            "--workpath",
            f"build/{system}",
        ]
    )

    # 复制配置文件
    if os.path.exists("config.ini.example"):
        if system == "darwin":
            subprocess.run(["cp", "config.ini.example", f"{output_dir}/config.ini"])
        else:
            subprocess.run(["cp", "config.ini.example", f"{output_dir}/config.ini"])

    print(f"构建完成，输出目录: {output_dir}")


if __name__ == "__main__":
    build()
