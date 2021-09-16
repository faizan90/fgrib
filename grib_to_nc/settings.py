'''
@author: Faizan3800X-Uni

Sep 16, 2021

9:16:44 AM
'''

from pathlib import Path
from datetime import datetime

import parse
from osgeo import osr


class GTCSettings:

    # String case matters. It has to match that of the osr module.
    _sett_nc_crs_kinds = (
        'EPSG',
        'EPSGA',
        'ERM',
        'ESRI',
        'MICoordSys',
        'Ozi',
        'PCI',
        'Proj4',
        'Url',
        'USGS',
        'Wkt',
        'XML')

    _sett_nc_calendars = (
        'standard',
        'gregorian',
        'proleptic_gregorian',
        'noleap',
        '365_day',
        '360_day',
        'julian',
        'all_leap',
        '366_day')

    _sett_nc_unitss = (
        'days',
        'hours',
        'minutes',
        'seconds',
        'milliseconds',
        'microseconds')

    # For 1D variables, having the same name for the netcdf dimension and
    # netcdf variable does not create problem. It is a problem for 2D though.
    # I think it's a bug.
    _sett_nc_x_cntrs_dim_lab = 'rX'
    _sett_nc_y_cntrs_dim_lab = 'rY'

    _sett_nc_x_cntrs_var_lab = 'rX'
    _sett_nc_y_cntrs_var_lab = 'rY'

    _sett_nc_x_crnrs_dim_lab = '_X'
    _sett_nc_y_crnrs_dim_lab = '_Y'

    _sett_nc_x_crnrs_var_lab = 'X'
    _sett_nc_y_crnrs_var_lab = 'Y'

    _sett_nc_time_lab = 'time'

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool)

        self._vb = verbose
        #======================================================================

        self._sett_path_to_nc = None

        self._sett_nc_crs = None
        self._sett_nc_crs_kind = None

        self._sett_nc_units = None
        self._sett_nc_calendar = None

        self._sett_verify_flag = False
        return

    def set_path_to_nc(self, path_to_nc):

        assert isinstance(path_to_nc, (str, Path))

        path_to_nc = Path(path_to_nc)

        assert path_to_nc.parents[0].exists()

        self._sett_path_to_nc = path_to_nc
        return

    def set_nc_crs(self, crs_kind, crs):

        assert isinstance(crs_kind, str)

        assert crs_kind in self._sett_nc_crs_kinds

        nc_crs = osr.SpatialReference()

        return_code = getattr(nc_crs, f'ImportFrom{crs_kind}')(crs)

        assert return_code == 0

        self._sett_nc_crs_kind = crs_kind
        self._sett_nc_crs = nc_crs
        return

    def set_nc_time(self, calendar, units):

        assert isinstance(calendar, str)
        assert calendar in self._sett_nc_calendars

        assert isinstance(units, str)

        parse_res = parse.search('{del_t:w} since {time_stamp:ti}', units)

        assert parse_res is not None

        assert parse_res['del_t'] in self._sett_nc_unitss

        assert isinstance(parse_res['time_stamp'], datetime)

        self._sett_nc_calendar = calendar
        self._sett_nc_units = units
        return

    def verify(self):

        assert self._sett_path_to_nc is not None

        assert self._sett_nc_crs is not None
        assert self._sett_nc_crs_kind is not None

        assert self._sett_nc_units is not None
        assert self._sett_nc_calendar is not None

        self._sett_verify_flag = True
        return

    __verify = verify
