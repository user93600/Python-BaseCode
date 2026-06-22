import os
import csv
from datetime import datetime

folder=input("请输入目标文件夹路径：").strip()
output=input("请输入保存的csv文件名：").strip()

with open(output,newline='',encoding="utf-8-sig") as f:
    writer=csv.writer(f)
    writer.writerow