import os

def scan_with_filter(root_path):
    with os.scandir(root_path) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name.startswith('.'):
                continue
            if entry.is_file() and entry.name.endswith('.py'):
                mtime=entry.stat().st_mtime
                size=entry.stat().st_size
                print(f"[文件]{entry.name}|修改时间：{mtime}|大小:{size}")
                

            if entry.is_dir():
                print(f"[目录]{entry.name}")
                scan_with_filter(entry.path)

scan_with_filter('.')