import os
print(os.path.dirname(os.path.abspath(__file__)))
print(os.getcwd())

new_path=input("请输入要切换到的目录（回车跳过）：").strip()
if new_path:
    try:
        os.chdir(new_path)
        print(f"已切换到：{os.getcwd()}")
    except Exception as e:
        print(f"错误：{e}")

print(os.path.dirname(os.path.abspath(__file__)))
print(os.getcwd())