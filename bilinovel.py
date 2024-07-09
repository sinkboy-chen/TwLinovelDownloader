import argparse
from Editer import Editer
import os
import shutil
from utils import *
from translate import translate_epub_with_path
from output_format import convert_format

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='config')
    parser.add_argument('--book_no', default='0000', type=str)
    parser.add_argument('--volume_no', default='1', type=int)
    parser.add_argument('--no_input', default=False, type=bool)
    args = parser.parse_args()
    return args


def query_chaps(book_no):
    print('未輸入卷號，將取得書籍目錄資訊......')
    editer = Editer(root_path='./out', book_no=book_no)
    print('*******************************')
    print(editer.title, editer.author)
    print('*******************************')
    editer.get_chap_list()
    print('*******************************')
    print('請輸入所需的卷號進行下載（多卷可以用英文逗號分隔或直接使用連字符，詳情請參閱說明）')

temp_path = ''

def delete_tmp():
    print(temp_path)
    if os.path.exists(temp_path): 
        shutil.rmtree(temp_path)

def download_single_volume(root_path,
                           book_no,
                           volume_no,
                           is_gui=False,
                           hang_signal=None,
                           progressring_signal=None,
                           cover_signal=None,
                           edit_line_hang=None,
                           to_simplified_chinese=False,
                           confirm_no_img=False,
                           output_file_type="epub"):
    editer = Editer(root_path=root_path, book_no=book_no, volume_no=volume_no, confirm_no_img=confirm_no_img)
    print('正在獲取書籍資訊....')
    success = editer.get_index_url()
    if not success:
        print('書籍資訊取得失敗')
        return
    print(editer.title + '-' + editer.volume['book_name'], editer.author)
    print('****************************')
    temp_path = editer.temp_path
    if not editer.is_buffer():
        editer.check_volume(is_gui=is_gui, signal=hang_signal, editline=edit_line_hang)
        print('正在下載文本....')
        print('*********************') 
        editer.get_text()
        print('*********************')
        editer.buffer()
    else:
        print('偵測到文字文件，直接下載插圖')
        editer.buffer()
    

    print('正在下載插圖.....................................')
    editer.get_image(is_gui=is_gui, signal=progressring_signal)
    
    print('正在編輯元數據....')
    editer.get_cover(is_gui=is_gui, signal=cover_signal)
    editer.get_toc()
    editer.get_content()
    editer.get_epub_head()

    print('正在生成 epub ....')
    epub_file = editer.get_epub()
    print(f'生成成功 路徑【{epub_file}】')

    translate_success = -1
    convert_success = -1

    if to_simplified_chinese:
        translate_success, epub_new_file = translate_epub_with_path(epub_file)
        if translate_success:
            os.remove(epub_file)
            epub_file = epub_new_file
        else:
            print("翻譯失敗")

    if output_file_type.lower()!="epub":
        convert_success, epub_new_file = convert_format(epub_file, output_file_type)
        if convert_success:
            os.remove(epub_file)
            epub_file = epub_new_file
        else:
            print("轉檔失敗")

    if translate_success!=0 and convert_success!=0:
        print(f"生成成功！ 電子書路徑【{epub_file}】")
    else:
        print(f"轉檔或翻譯失敗~ 電子書路徑【{epub_file}】")

def downloader_router(root_path,
                      book_no,
                      volume_no,
                      is_gui=False, 
                      hang_signal=None,
                      progressring_signal=None,
                      cover_signal=None,
                      edit_line_hang=None,
                      to_simplified_chinese=False,
                      confirm_no_img=False,
                      output_file_type="epub"):
    is_multi_chap = False
    if len(book_no)==0:
        print('請檢查輸入是否完整正確！')
        return
    elif volume_no == '':
        query_chaps(book_no)
        return 
    elif volume_no.isdigit():
        volume_no = int(volume_no)
        if volume_no<=0:
            print('請檢查輸入是否完整正確！') 
            return
    elif "-" in volume_no:
        start, end = map(str, volume_no.split("-"))
        if start.isdigit() and end.isdigit() and int(start)>0 and int(start)<int(end):
            volume_no_list = list(range(int(start), int(end) + 1))
            is_multi_chap = True
        else:
            print('請檢查輸入是否完整正確！')
            return
    elif "," in volume_no:
        volume_no_list = [num for num in volume_no.split(",")]
        if all([num.isdigit() for num in volume_no_list]):
            volume_no_list = [int(num) for num in volume_no_list] 
            is_multi_chap = True
        else:
            print('請檢查輸入是否完整正確！')
            return
    else:
            print('請檢查輸入是否完整正確！')
            return
    if is_multi_chap:
        for volume_no in volume_no_list:
            download_single_volume(root_path, book_no, volume_no, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang, to_simplified_chinese, confirm_no_img, output_file_type)
        print('所有下載任務都已經完成！')
    else:
        download_single_volume(root_path, book_no, volume_no, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang, to_simplified_chinese, confirm_no_img, output_file_type)
    
if __name__=='__main__':
    args = parse_args()
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    if args.no_input:
        downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
    else:
        while True:
            args.book_no = input('請輸入書籍號碼：')
            args.volume_no = input('請輸入卷號(查看目錄資訊不輸入直接按enter，下載多卷請使用逗號分隔或連字符-)：')
            downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
            # args.book_no = '3800'
            # args.volume_no = '1'
            # downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
            # exit(0)
    
        

    

    
    
