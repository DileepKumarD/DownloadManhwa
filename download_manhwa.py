from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from PyPDF2 import PdfFileMerger, PdfFileReader

from bs4 import BeautifulSoup
import requests
import img2pdf
import shutil
import os

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

get_chapter_timeout = 150
get_image_timeout = 200
verification_https = True
thread_count = 10
try_count = 2

check_for_cdn_in_image_link = True
merge_and_create_single_pdf_file = True

download_path = '/Users/Dileep/Downloads/'

MANHWA_CLUB = 'manhwa.club'
MANHWA18_NET = 'manhwa18.net'

manhwa_websites = {
    MANHWA_CLUB: {
        'base_url': 'https://manhwa.club/manhwa/{}/chapter-{}',
        'image_src': 'data-src',
        'image_format': 'jpg',
    },
    MANHWA18_NET : {
        'base_url' : 'https://manhwa18.net/read-{}-chapter-{}.html',
        'image_src': 'data-original',
        'image_format': 'jpg',
    },
}

manhwa_list = [
    {
        'manhwa_name': 'what-do-you-take-me-for',
        'starting_chapter': 1,
        'ending_chapter': 77,
        'manhwa_download_name': 'what-do-you-take-me-for'
    },
    {
        'manhwa_name' : 'family-tree-raw',
        'starting_chapter' : 16,
        'ending_chapter' : 32,
        'manhwa_download_name': 'family-tree-raw'
    },
]

executor = None

def init():
    global executor
    executor = ThreadPoolExecutor(thread_count)

    global try_count
    if try_count is None or try_count <= 0:
        try_count = 1

    global download_path
    if not is_file_already_present(download_path):
        download_path = os.path.curdir
        download_path = os.path.join(download_path, "DownloadedFiles")
        create_directory(download_path)
        download_path = download_path

def finish():
    executor.shutdown(wait=True)

def create_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def is_file_already_present(file):
    if os.path.exists(file):
        return True
    else:
        return False

def remove_file(file):
    if os.path.exists(file):
        os.remove(file)
        print('Removed file: {}'.format(file))

def merge_and_create_single_pdf(download_manhwa_dir, manhwa):
    starting_chapter = manhwa['starting_chapter']
    ending_chapter = manhwa['ending_chapter']
    manhwa_download_name = manhwa['manhwa_download_name']

    merged_file_name = os.path.join(download_manhwa_dir, '{}-from-chapter-{}-{}.pdf'.format(str(manhwa_download_name),
                                                                                           str(starting_chapter).zfill(3),
                                                                                           str(ending_chapter).zfill(3)))

    if starting_chapter == ending_chapter:
        raise Exception("Couldn't find multiple downloaded chapters to merge")

    if not is_file_already_present(merged_file_name):
        file_list = list()
        for file in os.listdir(download_manhwa_dir):
            if file.endswith(".pdf") and (file.find('from-chapter') == -1) and (file.find('with-error') == -1):
                chapter_num = int(file.rpartition('-')[2].replace('.pdf',''))
                if chapter_num < starting_chapter or chapter_num > ending_chapter:
                    continue

                file_path = os.path.join(download_manhwa_dir, file)
                file_list.append(file_path)

        file_list.sort()

        if len(file_list) != (ending_chapter-starting_chapter+1):
            raise Exception("All chapters in the specified range are not downloaded for file: " + merged_file_name)

        merged_object = PdfFileMerger()

        for file in file_list:
            merged_object.append(PdfFileReader(file, 'rb'))

        merged_object.write(merged_file_name)

    return merged_file_name

def save_to_pdf(pdf_file, images_list):
    with open(pdf_file, "wb") as file:
        file.write(img2pdf.convert(images_list))
        print('Saved pdf: {}'.format(str(pdf_file)))

def cleanup_after_successful_download(files_list, dir_list):
    try:
        for file in files_list:
            remove_file(file)
        for dir_name in dir_list:
            shutil.rmtree(dir_name)
    except:
        print("Failed while cleaningup temp files after succesful download")

def download_image(url, image_file):
    if not is_file_already_present(image_file):
        response = requests.get(url, verify = verification_https, timeout = get_image_timeout, allow_redirects = False)
        with open(image_file, 'wb') as file:
            file.write(response.content)

    print('Saved image: {}'.format(str(image_file)))
    return image_file

def download_chapter(website, manhwa_name, chapter, download_manhwa_dir, manhwa_download_name):
    base_url = website['base_url']
    image_src = website['image_src']
    image_format = website['image_format']

    url = base_url.format(manhwa_name, chapter)
    chapter_name = '{}-{}'.format(str(manhwa_download_name), str(chapter).zfill(3))

    pdf_file = os.path.join(download_manhwa_dir, '{}.pdf'.format(chapter_name))

    if is_file_already_present(pdf_file):
        return True

    print("Downloading Chapter: {}, url: {}".format(chapter_name, url))

    try:
        temp_download_manhwa_dir = os.path.join(download_manhwa_dir, 'temp')
        download_manhwa_chapter_dir = os.path.join(temp_download_manhwa_dir, 'Chapter-{}'.format(str(chapter)))
        create_directory(download_manhwa_chapter_dir)

        html_dir = os.path.join(download_manhwa_chapter_dir, 'html')
        create_directory(html_dir)

        html_file = os.path.join(html_dir, '{}.html'.format(chapter_name))

        if is_file_already_present(html_file):
            with open(html_file, 'r') as file:
                data = file.read()
        else:
            response = requests.get(url, verify = verification_https, timeout = get_chapter_timeout, allow_redirects = True)
            data = response.text
            with open(html_file, "wb") as file:
                file.write(response.content)

        soup = BeautifulSoup(data, 'lxml')

        images_dir = os.path.join(download_manhwa_chapter_dir, 'images')
        create_directory(images_dir)

        task_list = dict()

        images_list = list()
        image_num = 1
        with_error = False
        for images in soup.find_all('img'):
            image_url = images.get(image_src)

            if image_url is not None:
                if check_for_cdn_in_image_link and image_url.find('cdn') == -1:
                    continue

                image_url = image_url.strip()
                try:
                    print("Image No: {}, url: {}".format(image_num, str(image_url)))

                    image_name = '{}-{}.{}'.format(chapter_name, str(image_num), str(image_format))

                    image_file = os.path.join(images_dir, image_name)

                    task_list[image_num] = executor.submit(download_image, image_url, image_file)

                    image_num += 1
                except Exception as e:
                    with_error = True
                    print("Failed to download image of manhwa: {}, img no: {}, img url: {}, error: {}".format(chapter_name,
                                                                                                     str(image_num),
                                                                                                     str(image_url),
                                                                                                     str(e)))
        for task in range(1, image_num):
            try:
                result = task_list[task].result()
                images_list.append(str(result))
            except Exception as e:
                with_error = True
                print("Failed to download image of manhwa: {}, img no: {}, error: {}".format(chapter_name,
                                                                                      str(task),
                                                                                      str(e)))

        if image_num == 1:
            remove_file(html_file)
            raise Exception("No images found for the chapter, may be due to bad url")

        pdf_file_with_error = os.path.join(download_manhwa_dir, '{}-with-error.pdf'.format(chapter_name))
        if with_error:
            pdf_file = pdf_file_with_error

        try:
            save_to_pdf(pdf_file, images_list)
            if not with_error:
                cleanup_after_successful_download([pdf_file_with_error], [temp_download_manhwa_dir])
                return True
            else:
                return False
        except Exception as e:
            print("Failed to save images as pdf of manhwa: {}, error: {}", chapter_name, str(e))
            raise e

    except Exception as e:
        print("Failed to download chapter of manhwa: {}, error: {}".format(chapter_name,
                                                                str(e)))
        return False

def download_all_chapters(website, manhwa, download_manhwa_dir):
    manhwa_name = manhwa['manhwa_name']
    starting_chapter = manhwa['starting_chapter']
    ending_chapter = manhwa['ending_chapter']
    manhwa_download_name = manhwa['manhwa_download_name']

    for chapter in range(starting_chapter, ending_chapter + 1):
        print("Chapter No: " + str(chapter))

        start_time = datetime.now()
        for retry_count in range(0, try_count):
            download_successful = download_chapter(website, manhwa_name, chapter, download_manhwa_dir, manhwa_download_name)
            if download_successful:
                end_time = datetime.now()
                print("Downloaded Manhwa Chapter: {}-{}, time_taken: {} sec".format(str(manhwa_download_name), str(chapter), str(
                    (end_time - start_time).seconds)))
                break

def download_all_manhwas_from_website(website, manhwa_list):
    init()

    for manhwa in manhwa_list:
        try:
            download_manhwa_dir = os.path.join(download_path, manhwa['manhwa_download_name'])
            create_directory(download_manhwa_dir)
            download_all_chapters(website, manhwa, download_manhwa_dir)
            try:
                if merge_and_create_single_pdf_file:
                    merged_file_name = merge_and_create_single_pdf(download_manhwa_dir, manhwa)
                    print("Merged downloaded chapters into single pdf file: " + merged_file_name)
            except Exception as e:
                print("Failed to merge downloaded pdf files into one single pdf, error: " + str(e))
        except Exception as e:
            print("Failed to download manhwa: {}, error: {}", str(manhwa), str(e))

    print("Download of all manhwa completed")

    finish()

download_all_manhwas_from_website(manhwa_websites[MANHWA_CLUB], manhwa_list)

# download_all_manhwas_from_website(manhwa_websites[MANHWA18_NET], manhwa_list)