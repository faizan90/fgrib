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

    '''
    A subclass to store settings and validate them upon entry before
    converting a given GRIB file to netCDF4.

    This class is supposed to be inherited so some things may no make sense.

    Last updated on: 2021-Sep-21
    '''

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

    # For 1D variables, having the same name for a netcdf dimension and
    # a netcdf variable does not create a problem.
    # It is a problem for 2D though.
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

        '''
        Set the path to output netCDF4 file.

        Parameters
        ----------
        path_to_nc : str or Path
            Path pointing to the output netCDF4 file.
            Must be of string or Path data type.
            Whether it will be overwritten or not depends on the
            overwrite flag that is set in another class.
        '''

        assert isinstance(path_to_nc, (str, Path)), (
            f'path_to_nc not of the string or Path data type!')

        path_to_nc = Path(path_to_nc)

        assert path_to_nc.parents[0].exists(), (
            f'Parent directory of path_to_nc does not exist!')

        self._sett_path_to_nc = path_to_nc
        return

    def set_nc_crs(self, crs_kind, crs):

        '''
        Set the coordinate system of the output netCDF4 file.
        GRIB has it own rotated pole coordinates. These are transformed to
        same or other systems, if desired.

        Parameters
        ----------
        crs_kind : str
            The kind of coordinate system supplied. The kind depends on
            what GDAL can import from e.g. ImportFromEPSG or ImportFromWkt.
            The allowed crs_kinds are held as a tuple by the class
            variable _sett_nc_crs_kinds. If it is not of the allowed kinds,
            an AssertionError is raised, showing the allowed kinds.
            Also, upon entry, the transformation is checked to see it
            returns a valid projection. If not, an error is raised.
            Should be a string.
        crs : int or string or whatever the crs_kind needs it to be.
            The coordinate system in the form specified by the crs_kind.
            e.g. if crs_kind is EPSG then crs is an integer, if it is Wkt
            then it is the Wkt string representing the coordinate system.
            An error is raised if the supplied crs is not useable by GDAL.
            But it could also happen that GDAL is incorrectly configured
            and it cannot understand the supplied crs. So, please make sure
            that GDAL works on known coordinate system(s) by returning a zero
            upon importing the projection from the relevant coordinate system.
        '''

        assert isinstance(crs_kind, str), f'crs_kind is not a string!'

        assert crs_kind in self._sett_nc_crs_kinds, (
            f'crs_kind is not among the allowed kinds: '
            f'{self._sett_nc_crs_kinds}!')

        nc_crs = osr.SpatialReference()

        return_code = getattr(nc_crs, f'ImportFrom{crs_kind}')(crs)

        assert return_code == 0, 'Invalid crs or GDAL is misconfigured!'

        self._sett_nc_crs_kind = crs_kind
        self._sett_nc_crs = nc_crs
        return

    def set_nc_time(self, calendar, units):

        '''
        Set the time information of the output netCDF4.

        Parameters
        ----------
        calendar : string
            A valid netCDF4 calendar. Should be a string.
            See netCDF4 documentation for the allowed ones. The allowed
            ones can be seen in the variable _sett_nc_calendars class
            variable. In case an incorrect calendar is supplied, the allowed
            ones are shown and an AssertionError is raised.
        units : string
            A string represeting the reference time from which the netcdf
            library can reconstruct the time. Normally of the forms:
            "hours since ...", "days since ...". The first word should be
            one in the _sett_nc_unitss class variable. If not there then
            the allowed ones are shown and an AssertionError is raised.
        '''

        assert isinstance(calendar, str), (
            f'calendar not of the data type string!')

        assert calendar in self._sett_nc_calendars, (
            f'calendar not among the valid ones: {self._sett_nc_calendars}!')

        assert isinstance(units, str), f'units not of the data type string!'

        parse_res = parse.search('{del_t:w} since {time_stamp:ti}', units)

        assert parse_res is not None, 'Unknown format of units!'

        assert parse_res['del_t'] in self._sett_nc_unitss, (
            f'Time unit in units not among the allowed ones: '
            f'{self._sett_nc_unitss}!')

        assert isinstance(parse_res['time_stamp'], datetime), (
            f'Parsed reference time not a datetime object as expected!')

        self._sett_nc_calendar = calendar
        self._sett_nc_units = units
        return

    def verify(self):

        assert self._sett_path_to_nc is not None, (
            'Call set_path_to_nc first!')

        assert self._sett_nc_crs is not None, (
            f'Call set_nc_crs first!')

        assert self._sett_nc_crs_kind is not None, (
            f'Call set_nc_crs first!')

        assert self._sett_nc_units is not None, (
            f'Call set_nc_time first!')

        assert self._sett_nc_calendar is not None, (
            f'Call set_nc_time first!')

        self._sett_verify_flag = True
        return

    __verify = verify
