'''
@author: Faizan3800X-Uni

Sep 16, 2021

5:48:41 PM
'''
import bz2
import shutil
from pathlib import Path


class GUnpack:

    '''
    A simple class to help unpack compressed data.

    For now, only bz2 is supported.

    Take a look at the test/unpack_bz2.py file of this modeule for
    the intended use case.

    Last updated on: 2021-Sep-21
    '''

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool), (
            f'verbose not of the data type boolean!')

        self._vb = verbose

        return

    def unpack_bz2(self, path_to_input, path_to_output, overwrite_flag=False):

        '''
        Unpack a bz2 archive. A check is made to see if the previous unpack
        was successful or not.

        Parameters
        ----------
        path_to_input : str or Path
            Path of the input bz2 archive. Must have the string or Path
            data type. Should exist.
        path_to_ouput : str or Path
            Path of the output decompressed archive. The file may decompress
            in to a single only. Must be of the string or Path data type.
        overwrite_flag : bool
            Whether to overwrite existing results. Unsuccesful unpack results
            are overwritten regardless.
        '''

        assert isinstance(path_to_input, (str, Path)), (
            f'path_to_input not fo the data type string or Path!')

        path_to_input = Path(path_to_input)

        assert path_to_input.exists(), (
            r'Input file does not exist!')

        assert path_to_input.is_file(), f'Input is not a file!'

        assert isinstance(path_to_output, (str, Path)), (
            f'path_to_ouput is not of the string or Path data type!')

        path_to_output = Path(path_to_output)

        assert path_to_output.parents[0].exists(), (
            'Parent directory of path_to_output does not exist!')

        assert isinstance(overwrite_flag, bool), (
            f'overwrite_flag not of the boolean data type!')

        with bz2.BZ2File(path_to_input, 'rb') as f_in:

            # Used to determine if the file was unpacked correctly.
            temp_file_path = path_to_output.parents[0] / (
                f'{path_to_output.name}.tmp')

            if temp_file_path.exists():
                overwrite_flag = True

            else:
                open(temp_file_path, 'w')

            if overwrite_flag or (not path_to_output.exists()):
                with open(path_to_output, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

            temp_file_path.unlink()
        return
