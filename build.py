import os
import platform
import subprocess

def build():
    system = platform.system().lower()
    
    if system == 'darwin':
        spec_file = 'CursorKeepAlive.mac.spec'
        output_dir = 'dist/mac'
    elif system == 'windows':
        spec_file = 'CursorKeepAlive.win.spec'
        output_dir = 'dist/windows'
    else:
        print(f"不支持的操作系统: {system}")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 运行 PyInstaller
    subprocess.run(['pyinstaller', spec_file, '--distpath', output_dir, '--workpath', f'build/{system}'])
    
    # 复制配置文件
    if os.path.exists('config.ini'):
        if system == 'darwin':
            os.makedirs(f'{output_dir}/CursorPro.app/Contents/MacOS', exist_ok=True)
            subprocess.run(['cp', 'config.ini', f'{output_dir}/CursorPro.app/Contents/MacOS/'])
        else:
            subprocess.run(['cp', 'config.ini', output_dir])
    
    print(f"构建完成，输出目录: {output_dir}")

if __name__ == '__main__':
    build() 