import os
import csv
from datetime import datetime

def get_file_info(folder_path):
    file_list=[]
    for root,dirs,files in os.walk(folder_path):
        for file in files:
            full_path=os.path.join(root,file)
            try:
                size=os.path.getsize(full_path)
                ctime_timestamp=os.path.getctime(full_path)
                ctime_str=datetime.fromtimestamp(ctime_timestamp).strftime('%Y-%m-%D %H:%M:%S')
                file_info={
                    'file_path':full_path,
                    'file_name':file,
                    'file_size':size,
                    'file_ctime':ctime_str
                }
                file_list.append(file_info)
            except Exception as e:
                print(f"无法读取文件{full_path},错误{e}")
    return file_list

def save_to_csv(file_list,output_csv):
    fieldnames=['file_path','file_name','file_size','file_ctime']
    with open(output_csv,'w',newline='',encoding='utf-8-sig') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(file_list)
    print(f"文件信息已保存至：{output_csv}")

def print_all_file(file_list):
    for info in file_list:
        name=info['file_name']
        size=info['file_size']
        print(f"文件名：{name}  |  大小：{size} 字节")


def main():
    folder=input("请输入目标文件夹路径：").strip()
    folder=folder.strip('"').strip("'")

    if not os.path.isdir(folder):
        print("错误：输入的路径不是一个有效的文件夹！")
        return
    
    print(f"正在扫描文件夹：{folder}...")
    file_info_list=get_file_info(folder)
    print(f"共找到{len(file_info_list)}个文件。")
    print_all_file(file_info_list)

    if file_info_list:
        file_save_path=os.path.dirname(__file__)
        name=input("请输入csv文件名：")+"_file_info.csv"
        csv_save_path=os.path.join(file_save_path,name)
        save_to_csv(file_info_list,csv_save_path)
    else:
        print("没有找到任何文件，未生成csv文件。")

if __name__ == "__main__":
    main()