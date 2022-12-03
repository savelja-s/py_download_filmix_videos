import os
import sys
from urllib.error import URLError
from urllib.parse import urlparse
import wget
import requests

# def bar_custom(current, total, width=80):
#     print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))
default_save_dir = os.path.join(os.getcwd(), 'serials')


def download_wget(file_link: str):
    if not validate_url(file_link):
        raise RuntimeError(f'NOT VALID url={file_link}')
    [serial_name, file_name] = parse_file_name(file_link)
    dir_path = create_dirs(serial_name, file_name)
    print(f'SERIAL_NAME:{serial_name},FILE NAME:{file_name}')
    print(f'DIR:{dir_path}')
    file_path = os.path.join(dir_path, file_name)
    if os.path.isfile(file_path):
        print(f'File exists:{file_path}')
        # @TODO remove old files endWith `.tmp` and startWith `{file_name}`
        return None
    try:
        data = wget.download(file_link, out=file_path)
    except URLError as e:
        raise RuntimeError(f'BAD download={file_link} and save={file_path}')
    return data


def get_origin_url():
    if len(sys.argv) <= 1:
        return None
    page_url = sys.argv[1]
    if page_url.startswith('https://'):
        return page_url
    return None


def get_save_dir():
    if len(sys.argv) <= 2:
        return None
    dir_for_save = sys.argv[2]
    if dir_for_save.startswith('/'):
        return dir_for_save
    else:
        return os.path.join(os.getcwd(), dir_for_save)


# def video_content(url_to_video: str):
#     try:
#         response = requests.get(url_to_video, stream=True)
#         if response.status_code == 200:
#             response.raw.decode_content = True
#             return response.raw.read()
#     except requests.exceptions.RequestException as e:
#         print(e)
#     return None


def parse_file_name(file_link: str):
    array_path = urlparse(file_link).path.split('/')
    if len(array_path) <= 4:
        raise RuntimeError(f'BAD parse={file_link},result={array_path}')
    return [array_path[3], array_path[4]]


def create_dirs(serial_dir: str, videofile_name: str) -> str:
    serial_array = serial_dir.split('.')
    season = videofile_name.split('.')[0].split('e')[0]
    print(f'fileNAME:{season}')
    serial_name = ''
    translate_name = ''
    t_s = False
    for w in serial_array:
        if t_s:
            translate_name = f'{translate_name}.{w}'
        else:
            serial_name = f'{serial_name}.{w}'
        if w.isnumeric():
            t_s = True
    dir_path = os.path.join(default_save_dir, serial_name.lstrip('.'), translate_name.lstrip('.'), season)
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    return dir_path


def validate_url(link: str) -> bool:
    return requests.head(link).status_code == 200


def next_video(link: str):
    [serial_name, file_name] = parse_file_name(link)
    s = file_name[1:3]
    e = file_name[4:6]
    next_link = link.replace(f'e{e}', f'e{str(int(e) + 1).zfill(2)}')
    if requests.head(next_link).status_code == 200:
        print(f'NEXT URL {next_link}')
        return next_link
    print(f'BAD next page={next_link}')
    next_link = link.replace(f'e{e}', f'e{str(1).zfill(2)}')
    next_link = next_link.replace(f's{s}', f's{str(int(s) + 1).zfill(2)}')
    if requests.head(next_link).status_code == 200:
        print(f'NEXT URL {next_link}')
        return next_link
    print(f'BAD next page={next_link}')
    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = get_origin_url()
    save_dir = get_save_dir()
    if save_dir:
        default_save_dir = save_dir
    if not url or not validate_url(url):
        print('Need set valid url')
        exit()
    print(f'First page {url}')
    video = download_wget(url)
    print(f'DONE {video}')
    [serial_name, file_name] = parse_file_name(url)
    next_video_url = next_video(url)
    while next_video_url:
        video = download_wget(next_video_url)
        if video:
            print(f'DONE {video}')
        next_video_url = next_video(next_video_url)
    print(f'Serial download {serial_name}')
