'''
@author: Faizan3800X-Uni

Sep 16, 2021

5:48:41 PM
'''

import bz2
import shutil
from pathlib import Path


class GUnpack:

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool)

        self._vb = verbose
        return

    def unpack_bz2(self, path_to_input, path_to_output):

        assert isinstance(path_to_input, (str, Path))

        path_to_input = Path(path_to_input)

        assert path_to_input.exists()
        assert path_to_input.is_file()

        assert isinstance(path_to_output, (str, Path))

        path_to_output = Path(path_to_output)

        assert path_to_output.parents[0].exists()

        with bz2.BZ2File(path_to_input, 'rb') as f_in:
            with open(path_to_output, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

        return