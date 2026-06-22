import os

"""1.单层遍历，扫描当前目录"""
print("===os.scandir()单层遍历（当前目录）===")
#scandir (返回迭代器),自动关闭资源
with os.scandir('.') as entries:
    for entry in entries:
        #entry 是 DirEntry 对象，自带缓存属性
        if entry.is_dir():
            print(f"[目录]{entry.name}->完整路径：{entry.path}")
        elif entry.is_file():
            print(f"[文件]{entry.naem}->完整路径：{entry.path}")