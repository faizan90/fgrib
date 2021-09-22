'''
@author: Faizan3800X-Uni

Sep 17, 2021

8:32:59 AM
'''
from pathlib import Path
from fnmatch import fnmatch

import requests
from bs4 import BeautifulSoup as bs

from ..misc import print_sl, print_el


class GDownload:

    '''
    Simple facilities to list and download files from a website.

    1. List all files with a given extension for a given URL.
    2. Download a given file at a given URL.

    The URLs are supposed to have simple listings of files. I think it won't
    work on those fancy websites where files are shown inside widgets or
    something.

    Take a look at the test/download_grib.py file of this modeule for
    the intended use case.

    Last updated on: 2021-Sep-22
    '''

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool), (
            f'verbose not of the data type boolean!')

        self._vb = True

        return

    def get_all_names(self, url, ext):

        '''
        Get names of all files at a given URL with a specified extenion as
        a list. An AssertionError is raised if no files are found at the end.

        Parameters
        ----------
        url : str
            The URL at which to look for files. Must be a string and end with
            a "/".
        ext : str
            The extension/ending that the file names should have.

        Returns
        -------
        List of all the names.
        '''

        if self._vb:
            print_sl()

            print('Getting all file names...')

        assert isinstance(url, str), f'url not of the string data type!'

        assert len(url), f'Empty url!'

        assert url[-1] == '/', f'url not ending with a "/"!'

        assert isinstance(ext, str), f'ext not of the data type string!'

        assert len(ext), f'Empty ext!'

        if self._vb:
            print(f'URL: {url}')
            print(f'File extension: {ext}')

        soup = bs(requests.get(url).text, features='html.parser')

        patt = f'*{ext}'

        names = []
        for href in soup.find_all('a'):
            name = href['href']

            if not fnmatch(name, patt):
                continue

            names.append(name)

        if self._vb:
            print(f'Found {len(names)} files.')

        assert len(names), (
            f'Could not find any names with the extension {ext} at {url}!')

        if self._vb:
            print_el()

        return names

    def download_file(self, url, name, download_dir, overwrite_flag=False):

        '''
        Download a file from a given URL with a check to see if the previous
        attempts to download, if any, were successful. It could happen
        that a file was partially download. If so, it is redownloaded.
        This is done by having a temporary file created before download
        and deleted afterwards if the download was successful.

        Parameters
        ----------
        url : str
            The url where the file exists. This should not include the file
            name. Should be of the string data type and end with a "/".
        name : str
            The name of the file to download. Should be of the string data
            type. An error is raised by the requests module if the file
            is not found.
        download_dir : str or Path
            Local location of the directory inside which to save the file.
            Can be of string or Path data type. Should exist.
        overwrite_flag : bool
            Whether to overwrite the file or not if it exists. If False and
            the file does exist then no it is not downloaded.
            If the file download was unsuccessful the last time then it
            is overwritten regardless.
        '''

        if self._vb:
            print_sl()

            print('Downloading file...')

        assert isinstance(url, str), f'url not of the data type string!'

        assert len(url), f'Empty url string!'

        assert url[-1] == '/', f'url not ending with a "/"!'

        assert isinstance(name, str), 'name not of the data type string!'

        assert len(name), 'Empty name string!'

        assert isinstance(download_dir, (str, Path)), (
            f'download_dir not of the data type string or Path!')

        download_dir = Path(download_dir)

        assert download_dir.exists(), f'download_dir does not exist!'

        assert download_dir.is_dir(), f'download_dir is not a directory!'

        assert isinstance(overwrite_flag, bool), (
            f'overwrite_flag not of the boolean data type!')

        out_file_path = download_dir / name

        if self._vb:
            print(f'URL: {url}')
            print(f'File name: {name}')
            print(f'Output path: {out_file_path}')

        # Used to determine if the file was downloaded and written to
        # completely.
        temp_file_path = download_dir / f'{name}.tmp'

        if temp_file_path.exists():
            overwrite_flag = True

            print(
                f'INFO: Previous attempt to download the file seems '
                f'to have been unsuccessful. Overwriting the previous file.')

        else:
            open(temp_file_path, 'w')

        if overwrite_flag or (not out_file_path.exists()):
            if self._vb:
                print(f'Downloading...')

            req_cont = requests.get(f'{url}{name}', allow_redirects=True)
            open(out_file_path, 'wb').write(req_cont.content)

        else:
            if self._vb:
                print('Not downloading.')

        temp_file_path.unlink()

        if self._vb:
            print_el()

        return
