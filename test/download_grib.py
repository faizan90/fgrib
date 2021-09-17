'''
@author: Faizan-Uni-Stuttgart

Sep 17, 2021

9:00:56 AM

'''
import os
import sys
import time
import timeit
import traceback as tb
from pathlib import Path

from fgrib import GDownload

DEBUG_FLAG = False


def main():

    main_dir = Path(r'P:\Downloads')
    os.chdir(main_dir)

    grib_url = r'https://opendata.dwd.de/climate_environment/REA/COSMO_REA6/hourly/2D/TOT_PRECIP/'

    ext = '.bz2'

    overwrite_flag = False

    out_dir = main_dir
    #==========================================================================

    out_dir.mkdir(exist_ok=True)

    down_cls = GDownload()

    grib_names = down_cls.get_all_names(grib_url, ext)

    print(grib_names[:3])

    for name in grib_names[:3]:
        down_cls.download_file(grib_url, name, main_dir, overwrite_flag)

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
