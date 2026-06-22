import os

# os.walk() 自动递归遍历整个目录树，返回(root,dirs,flies)
print("\n=== os.walk() 自动递归遍历（全目录树）===")
for root,dirs,files in os.walk('.'):
    #root当前遍历的目录路径
    #dirs:root下的子目录名列表
    #files:root下的文件名列表
    print(f"当前目录：{root}")
    for d in dirs:
        print(f"    [目录]{d}")
    for f in files:
        print(f"    [文件]{f}")