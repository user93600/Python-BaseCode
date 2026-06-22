import os
path=input("请输入完整的文件路径：").strip().strip('"').strip("'")

dir_part,file_part=os.path.split(path)
print(f"目录:{dir_part}")
print(f"文件名：{file_part}")

name_only,ext=os.path.splitext(file_part)

new_name=name_only+'_new'+ext
new_path=os.path.join(dir_part,new_name)
print(f"新路径：{new_path}")