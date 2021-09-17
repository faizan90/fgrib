'''
@author: Faizan-Uni-Stuttgart

Sep 16, 2021

5:58:44 PM

'''
import os
import sys
import time
import timeit
import traceback as tb
from pathlib import Path

from fgrib import GUnpack

DEBUG_FLAG = False


def main():

    main_dir = Path(r'P:\Downloads')
    os.chdir(main_dir)

    path_to_input = Path(r'TOT_PRECIP.2D.199501.grb.bz2')
    path_to_output = path_to_input.with_suffix('')

    unpack_cls = GUnpack()

    unpack_cls.unpack_bz2(path_to_input, path_to_output)
    return


if __name__ == '__main__':
    print('#### Started on %s ####\n' % time.asctime())
    START = timeit.default_timer()

    #==========================================================================
    # When in post_mortem:
    # 1. "where" to show the stack
    # 2. "up" move the stack up to an older frame
    # 3. "down" move the stack down to a newer frame
    # 4. "interact" start an interactive interpreter
    #==========================================================================

    if DEBUG_FLAG:
        try:
            main()

        except:
            pre_stack = tb.format_stack()[:-1]

            err_tb = list(tb.TracebackException(*sys.exc_info()).format())

            lines = [err_tb[0]] + pre_stack + err_tb[2:]

            for line in lines:
                print(line, file=sys.stderr, end='')

            import pdb
            pdb.post_mortem()
    else:
        main()

    STOP = timeit.default_timer()
    print(('\n#### Done with everything on %s.\nTotal run time was'
           ' about %0.4f seconds ####' % (time.asctime(), STOP - START)))
