from enum import Enum
from pathlib import Path
import subprocess
import os

class OutputFormat(Enum):
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"
    TXT = "txt"
    AZW3 = "azw3"
    LRF = "lrf"
    OEB = "oeb"
    PDB = "pdb"
    RTF = "rtf"

def find_format(target_format):
    format_lookup = {format_name.value: format_name for format_name in OutputFormat}
    member = format_lookup.get(target_format)
    if not member:
        member = OutputFormat.EPUB
    return member

def is_valid_format(format):
    return format in [item.value for item in OutputFormat]

def convert_format(original_path, target_format):
    if not os.path.isfile(original_path):
        print(f"{original_path} 不是有效的檔案 放棄轉檔")
        return 0, None
    
    target_format = target_format.lower()
    if not is_valid_format(target_format):
        print(f"{target_format} 不是有效的檔案格式 放棄轉檔")
        return 0, None
    
    if target_format=="epub":
        print("已經是epub檔案 不須轉檔[內部出錯]")
        return 0, None

    path = Path(original_path)
    file_extension = path.suffix.lower()

    if file_extension!=".epub":
        print("輸入檔案只允許為epub檔[內部出錯]")
        return 0, None
    
    output_path = path.parent / path.stem
    output_path = output_path.with_suffix(f".{target_format}")

    CREATE_NO_WINDOW = 0x08000000
    print(f"正在測試轉檔工具......")
    try:
        subprocess.run(
            ["ebook-convert"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW
        )
        print(f"轉檔工具測試成功")
    except:
        print("轉檔工具測試失敗")
        print("可能")
        print("1.未安裝calibre [https://calibre-ebook.com/download]")
        print("2.calibre ebook-convert.exe 的資料夾不在環境變數中")
        print("若無法解決此問題 輸出檔案格式選擇 epub")
        return 0, None

    print(f"正在轉成{target_format}檔案格式......")
    
    try:
        
        subprocess.run(
            ["ebook-convert", original_path, output_path], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW
        )
        print(f"轉檔成功 路徑【{output_path}】")
        return 1, output_path
    except Exception as e:
        print(f"{original_path} 到 {output_path} 轉檔失敗")
        print(f"error {e}")
        return 0, None