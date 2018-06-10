#!/usr/bin/env python3
from time import time

from requests_futures.sessions import FuturesSession
import logging
import pathlib
import requests
from bs4 import BeautifulSoup
import os
from random import choice

logging.basicConfig(level=logging.INFO)

def main():

    try:
        total_rfc = get_rfc_total()
        logging.info(f'Current total of published RFC\'s: {total_rfc}')
        check_folder_exists()
        folder = os.path.join(pathlib.Path.home(), 'code/test/RFC')
        os.chdir(folder)
        logging.info(f'changed dir to: {folder}')
        start = time()
        iterate_over_rfcs(total_rfc)
        end = time()
        logging.info(f'This took: {end - start} to run!')

    except OSError:
        raise

    except KeyboardInterrupt:
        print('User exited using CTRL-C')

    finally:
        logging.info(f'Total number RFC text files: {len(os.listdir())}')
        cur_dir = pathlib.Path(__file__).parent
        logging.info(f'changed dir to: {cur_dir}')

def random_header():
    desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
    return {'User-Agent': choice(desktop_agents), 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

def iterate_over_rfcs(total_rfc):
    """Iterate over all possible RFC numbers on the IEEE webpage and then
    write them individually to files with a separate folder."""
    session = FuturesSession(max_workers=10)

    for num in range(1, total_rfc):
        url = f"https://www.rfc-editor.org/rfc/rfc{num}.txt"
        future = session.get(url, headers=random_header())
        resp = future.result()
        if resp.status_code == 200:
            text = resp.text
            check_exists(num, text)

        else:
            print(f"RFC {num:04d} DOES NOT EXIST")



def create_files(num, text, filename):
    """Function that creates text files from the RFC website.

    :argument num: takes the RFC number as part of the filename
    :argument text: writes the response text from the webpage into the file.
    :argument filename: takes filename from :func: check_exists
    """
    with open(filename, 'w') as fout:
        fout.write(text)
        print(f"RFC {num:04d} downloaded!")


def check_exists(num, text):
    """Checks whether the file is already in the folder, only downloading a
    copy if it does not exist."""

    filename = f'RFC-{num:04d}.txt'
    lst = [file for file in os.listdir()]
    if filename not in lst:
        create_files(num, text)

def get_rfc_total():
    url = 'https://www.rfc-editor.org/rfc-index.html'
    resp = requests.get(url)
    text = resp.text
    soup = BeautifulSoup(text, 'html.parser')
    tables = soup.find_all('table')
    rfc_table = tables[2].find_all('tr')
    print(len(tables))
    return len(rfc_table)


def check_folder_exists():
    """Create the folder that stores all the RFC files if it does not exist."""
    folder = os.path.join(pathlib.Path.home(), 'code/test/RFC')
    try:
        if not os.path.exists(folder):
            logging.info('Folder doesn\'t exist...')
            os.makedirs(folder)
            logging.info(f'Folder: {folder} created!')
        else:
            logging.info(f'{folder} already exists.')
    except OSError:
        raise

if __name__ == '__main__':
    main()