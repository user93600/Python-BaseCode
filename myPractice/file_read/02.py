import os

"""2.递归遍历，手动控制深度"""
def scandir_recursive(path,depth=0):
    with os.scandir(path) as entries:
        for entry in entries:
            print("  " * depth+f"{'[目录]'if entry.is_dir()else '[文件]'}{entry.name}")
            #递归子目录，可加条件限制最大深度
            if entry.is_dir() and not entry.name.startswith('.'):#跳过隐藏目录
                scandir_recursive(entry.path,depth+1)

print("\n=== os.scandir() 手动递归遍历（全目录树）===")
scandir_recursive(".")