'''
@author: Faizan-Uni-Stuttgart

Sep 16, 2021

3:09:59 PM

'''
import os
import sys
import time
import timeit
import traceback as tb
from pathlib import Path

from fgrib import GTCConvert

DEBUG_FLAG = False


def main():

    main_dir = Path(r'P:\Downloads')
    os.chdir(main_dir)

    path_to_grib = Path(r'TOT_PRECIP.2D.199501.grb')
    path_to_nc = Path(r'TOT_PRECIP.2D.199501.nc')

    nc_crs_kind = 'EPSG'
    nc_crs = 4326

    nc_calendar = 'gregorian'
    nc_units = 'hours since 1995-01-01 00:00:00.0'

    cnvt_cls = GTCConvert(True)

    cnvt_cls.set_path_to_grib(path_to_grib)

    cnvt_cls.set_path_to_nc(path_to_nc)
    cnvt_cls.set_nc_crs(nc_crs_kind, nc_crs)
    cnvt_cls.set_nc_time(nc_calendar, nc_units)

    cnvt_cls.verify()

    cnvt_cls.read_grib()
    cnvt_cls.close_grib()

    cnvt_cls.convert_to_nc()
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
