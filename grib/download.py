'''
@author: Faizan3800X-Uni

Sep 17, 2021

8:32:59 AM
'''
import os
from pathlib import Path
from fnmatch import fnmatch

import requests
from bs4 import BeautifulSoup as bs


class GDownload:

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool)

        self._vb = True

        return

    def get_all_names(self, url, ext):

        assert isinstance(url, str)
        assert len(url)
        assert url[-1] == '/'

        assert isinstance(ext, str)
        assert len(ext)

        soup = bs(requests.get(url).text, features='html.parser')

        patt = f'*{ext}'

        names = []
        for href in soup.find_all('a'):
            name = href['href']

            if not fnmatch(name, patt):
                continue

            names.append(name)

        return names

    def download_file(self, url, name, download_dir, overwrite_flag=False):

        assert isinstance(url, str)
        assert len(url)
        assert url[-1] == '/'

        assert isinstance(name, str)
        assert len(name)

        assert isinstance(download_dir, (str, Path))

        download_dir = Path(download_dir)

        assert download_dir.exists()
        assert download_dir.is_dir()

        assert isinstance(overwrite_flag, bool)

        out_file_path = download_dir / name

        # Used to determine if the file was download and written to
        # completely.
        temp_file_path = download_dir / f'{name}.tmp'
#

        if temp_file_path.exists():
            overwrite_flag = True

        else:
            open(temp_file_path, 'w')

        if overwrite_flag or (not out_file_path.exists()):
            req_cont = requests.get(f'{url}{name}', allow_redirects=True)
            open(out_file_path, 'wb').write(req_cont.content)

        os.remove(temp_file_path)
        return
