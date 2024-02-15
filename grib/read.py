'''
@author: Faizan3800X-Uni

Sep 16, 2021

10:21:17 AM
'''
from pathlib import Path
from datetime import datetime
from collections import namedtuple

import parse
import numpy as np
from osgeo import gdal, osr

from ..misc import print_sl, print_el

# A namedtuple object to hold the raster props, to avoid remembering the
# indices.
_RasProps = namedtuple(
    'RasProps',
    ['x_min',
     'x_max',
     'y_min',
     'y_max',
     'n_cols',
     'n_rows',
     'cell_width',
     'cell_height',
     'proj',
     'band_count'])


class GRead:

    '''
    Read a GRIB file using GDAL. Supported GRIB versions depend on
    whatever GDAL supports.

    Note
    ----
    Currently the time strings in metadata for each band are supposed to
    have time units of seconds (sec) with no time zone i.e. UTC only.
    I didn't have any files at the time to take into account what other time
    representations may look like.

    Also, reinitiate the class if some of the "get" methods are mistakenly
    called multiple times in an interactive interpreter. I made the code
    to run in a non-interactive interpreter.

    Take a look at the test/read_grib.py file of this modeule for
    the intended use case.

    Description
    -----------
    Only path to a valid GRIB file is needed. See the rest of the
    documentation (all methods) for more details as well.

    How-To-Use
    ----------
    After initiating a GRead object (gread_cls = GRead(verbose_flag)),
    set the path to the GRIB file by calling set_poth_to_grib method.
    Call verify to see if all the required conditions are met. Without a call
    to verify, the file cannot be read. Call read_grib and then close_grib.
    Closing can be done after reading as all the relevant data is loaded
    in to RAM. Any required variable can then be had by calling any of the
    get_* methods. See the documentation of each method for the format.

    Last updated on: 2021-Sep-22
    '''

    _grib_time_units = (
        'sec',
        )

    _grib_time_refs = (
        'UTC',
        )

    def __init__(self, verbose=True):

        assert isinstance(verbose, bool), (
            f'verbose not of the boolean data type!')

        self._vb = verbose

        self._gread_path_to_grib = None

        self._gread_handle = None
        self._gread_sp_props_orig = None
        self._gread_grid_shape = None
        self._gread_crs = None
        self._gread_x_crds_crnrs = None
        self._gread_y_crds_crnrs = None
        self._gread_x_crds_cntrs = None
        self._gread_y_crds_cntrs = None
        self._gread_meta_data = None
        self._gread_time_stamps = None
        self._gread_data = None
        self._gread_dtype = None

        self._gread_verify_flag = False
        self._gread_read_flag = False
        return

    def set_path_to_grib(self, path_to_grib):

        '''
        Set path pointing to the input GRIB file.

        Parameters
        ----------
        path_to_grib : str, Path
            Path to the GRIB file. Must be of valid data type and exist.
            Whether it is a valid GRIB file or not is not checked here.
            This is done once read_grib is called.
        '''

        if self._vb:
            print_sl()

            print('Setting path to GRIB file...')

        assert isinstance(path_to_grib, (str, Path)), (
            f'Invalid data type of path_to_grib: type({path_to_grib})!')

        path_to_grib = Path(path_to_grib)

        assert path_to_grib.exists(), (
            f'GRIB file at: {path_to_grib} does not exist!')

        assert path_to_grib.is_file(), (
            f'Supplied path: {path_to_grib} is not a file!')

        self._gread_path_to_grib = path_to_grib

        if self._vb:
            print(f'Set the following path to GRIB file:')
            print(self._gread_path_to_grib)

            print_el()

        return

    def verify(self):

        if self._vb:
            print_sl()

            print(f'Verifying GRIB read...')

        assert self._gread_path_to_grib is not None, (
            f'Path to input file not set. Call set_path_to_grib first!')

        self._gread_verify_flag = True

        if self._vb:
            print(f'GRIB read was OK.')

            print_el()

        return

    def read_grib(self):

        if self._vb:
            print_sl()

            print('Reading GRIB file...')

        assert self._gread_verify_flag, (
            f'Inputs not verified. Call verify first!')

        grib_hdl = gdal.Open(str(self._gread_path_to_grib))

        assert grib_hdl is not None, (
            f'Could not open file: {self._gread_path_to_grib} using GDAL!')

        driver = grib_hdl.GetDriver()

        assert str(driver.ShortName) == 'GRIB', (
            f'Supplied file seems not to be a GRIB file but of the '
            f'format: {driver.LongName}, {driver.ShortName}!')

        self._gread_handle = grib_hdl
        #======================================================================

        # Read geospatial data
        n_rows = grib_hdl.RasterYSize
        n_cols = grib_hdl.RasterXSize

        geotransform = grib_hdl.GetGeoTransform()

        x_min = geotransform[0]
        y_max = geotransform[3]

        pix_width = geotransform[1]
        pix_height = abs(geotransform[5])

        x_max = x_min + (n_cols * pix_width)
        y_min = y_max - (n_rows * pix_height)

        proj = grib_hdl.GetProjectionRef()

        band_count = grib_hdl.RasterCount

        self._gread_sp_props_orig = _RasProps(
            x_min,
            x_max,
            y_min,
            y_max,
            n_cols,
            n_rows,
            pix_width,
            pix_height,
            proj,
            band_count)

        self._gread_grid_shape = (n_rows, n_cols)
        #======================================================================

        # Create spatial reference.
        crs = osr.SpatialReference()

        return_code = crs.ImportFromWkt(proj)

        assert return_code == 0, (
            f'Projection ({proj}) from GRIB file is unuseable!')

        self._gread_crs = crs
        #======================================================================

        # Create xy coordinates.
        x_crds_crnrs = np.linspace(x_min, x_max, n_cols + 1)
        y_crds_crnrs = np.linspace(y_max, y_min, n_rows + 1)

        self._gread_x_crds_crnrs = x_crds_crnrs
        self._gread_y_crds_crnrs = y_crds_crnrs

        self._gread_x_crds_cntrs = (x_crds_crnrs + (0.5 * pix_width))[:-1]
        self._gread_y_crds_cntrs = (y_crds_crnrs - (0.5 * pix_height))[:-1]
        #======================================================================

        # Read data.
        meta_data = []
        time_stamps = []
        data = None

        warned_secs = False
        for i in range(band_count):
            band = grib_hdl.GetRasterBand(i + 1)

            band_meta_data = band.GetMetadata()

            ref_time_str = band_meta_data['GRIB_REF_TIME']

            try:
                parse_res = parse.search(
                    '{time:12d} {unit:w} {ref:w}', ref_time_str)

                assert parse_res is not None, (
                    f'Could not parse: {ref_time_str} to get time!')

                assert parse_res['unit'] in self._grib_time_units, (
                    f'The key "unit" is not in parse!')

                assert parse_res['ref'] in self._grib_time_refs, (
                    f'The key "ref" is not in parse!')

                band_time = datetime.utcfromtimestamp(parse_res['time'])

            except:
                if not warned_secs:

                    print(
                        'WARNING: Only seconds seem to have been specified '
                        'in the GRIB_REF_TIME!')

                    warned_secs = True

                parse_res = parse.search('{time:12d}', ref_time_str)

                assert parse_res is not None, (
                    f'Could not parse: {ref_time_str} to get time!')

                band_time = datetime.utcfromtimestamp(
                    parse_res['time'] +
                    int(band_meta_data['GRIB_FORECAST_SECONDS']))

            band_data = band.ReadAsArray()

            if data is None:
                data = np.empty(
                    (band_count, n_rows, n_cols), dtype=band_data.dtype)

            meta_data.append(band_meta_data)
            time_stamps.append(band_time)
            data[i,:,:] = band_data

        self._gread_meta_data = tuple(meta_data)
        self._gread_time_stamps = tuple(time_stamps)
        self._gread_data = data

        self._gread_dtype = self._gread_data[0].dtype

        self._gread_read_flag = True

        if self._vb:
            print('Done reading GRIB data.')

            print_el()

        return

    def close_grib(self):

        '''
        Closes the GDAL read handle to the GRIB file.
        '''

        self._gread_handle = None

        if self._vb:
            print_sl()

            print('Closed handle to GRIB file.')

            print_el()

        return

    def get_spatial_properties_grib(self):

        '''
        Returns
        -------
        The spatial properties of the GRIB raster as a namedtuple.
        These are the raw values from the file. No transformation is
        applied at this stage.
        The tuple has the following attributes:
        1. x_min: The minimum x-coordinate.
        2. x_max: The maximum x-coordinate.
        3. y_min: The minimum y-coordinate.
        4. y_max: The maximum y-coordinate.
        5. n_cols: The number of columns of the raster for each time step.
        6. n_rows: The number of rows of the raster for each time step.
        7. cell_width: Width of cell in original coordinate system.
        8. cell_height: Width of cell in original coordinates system.
        9. proj: The projection data returned GetProjectionRef().
        10. band_count: The number of time steps.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB spatial properites...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_sp_props_orig is not None, (
            f'Required attribute (self._gread_sp_props_orig) not set!')

        assert isinstance(self._gread_sp_props_orig, _RasProps), (
            f'Expected the object to be of _RasProps type!')

        if self._vb:
            print_el()

        return self._gread_sp_props_orig

    def get_grid_shape_grib(self):

        '''
        Returns
        -------
        Shape of the GRIB grid as a tuple.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB grid shape...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_grid_shape is not None, (
            f'Required attribute (self._gread_grid_shape) not set!')

        assert isinstance(self._gread_grid_shape, tuple), (
            f'Required attribute not a tuple!')

        if self._vb:
            print_el()

        return self._gread_grid_shape

    def get_crs_grib(self):

        '''
        Returns
        -------
        The coordinates system of the GRIB file as a GDAL spatial reference.
        This is needed to reproject the coordinates to another system later.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB coordinate system as a Wkt string...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_crs is not None, (
            f'Required attribute (self._gread_crs) not set!')

        assert isinstance(self._gread_crs, osr.SpatialReference), (
            f'Required attribute not a GDAL spatial reference!')

        if self._vb:
            print_el()

        return self._gread_crs

    def get_x_coordinates_grib_crnrs(self):

        '''
        Returns
        -------
        The coordinates of each cell corner in the horizontal direction in
        the GRIB coordinate system as an array. The number of the
        coordinates is one more than the number of rows of the grid.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB X corner coordinates...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_x_crds_crnrs is not None, (
            f'Required attribute (self._gread_x_crds_crnrs) not set!')

        assert isinstance(self._gread_x_crds_crnrs, np.ndarray), (
            f'Required attribute not a np.ndarray!')

        if self._vb:
            print_el()

        return self._gread_x_crds_crnrs

    def get_y_coordinates_grib_crnrs(self):

        '''
        Returns
        -------
        The coordinates of each cell corner in the vertical direction in
        the GRIB coordinate system as an array. The number of the
        coordinates is one more than the number of columns of the grid.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB Y corner coordinates...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_y_crds_crnrs is not None, (
            f'Required attribute (self._gread_y_crds_crnrs) not set!')

        assert isinstance(self._gread_y_crds_crnrs, np.ndarray), (
            f'Required attribute not a np.ndarray!')

        if self._vb:
            print_el()

        return self._gread_y_crds_crnrs

    def get_x_coordinates_grib_cntrs(self):

        '''
        Returns
        -------
        The coordinates of each cell center in the horizontal direction in
        the GRIB coordinate system as an array. The number of the
        coordinates is equal to the number of rows of the grid.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB X center coordinates...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_x_crds_cntrs is not None, (
            f'Required attribute (self._gread_x_crds_cntrs) not set!')

        assert isinstance(self._gread_x_crds_cntrs, np.ndarray), (
            f'Required attribute not a np.ndarray!')

        if self._vb:
            print_el()

        return self._gread_x_crds_cntrs

    def get_y_coordinates_grib_cntrs(self):

        '''
        Returns
        -------
        The coordinates of each cell center in the vertical direction in
        the GRIB coordinate system as an array. The number of the
        coordinates is equal to the number of columns of the grid.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB Y center coordinates...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_y_crds_cntrs is not None, (
            f'Required attribute (self._gread_y_crds_cntrs) not set!')

        assert isinstance(self._gread_y_crds_cntrs, np.ndarray), (
            f'Required attribute not a np.ndarray!')

        if self._vb:
            print_el()

        return self._gread_y_crds_cntrs

    def get_meta_data_grib(self):

        '''
        Returns
        -------
        Metadata extracted for each time step as a tuple. The correspondance
        is one-to-one for a grid at each time step.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB metadata for each time step...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_meta_data is not None, (
            f'Required attribute (self._gread_meta_data) not set!')

        assert isinstance(self._gread_meta_data, tuple), (
            f'Required attribute not a tuple!')

        if self._vb:
            print_el()

        return self._gread_meta_data

    def get_time_stamps_grib(self):

        '''
        Returns
        -------
        Time stamps as datetime objects corresponding to each grid of the
        GRIB data. These are extracted from the metadata which are supposed
        to be in UTC seconds and then cast as datetime objects.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB time stamps for each time step...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_time_stamps is not None, (
            f'Required attribute (self._gread_time_stamps) not set!')

        assert isinstance(self._gread_time_stamps, tuple), (
            f'Required attribute not a tuple!')

        if self._vb:
            print_el()

        return self._gread_time_stamps

    def get_data_grib(self):

        '''
        Returns
        -------
        GRIB data as a np.ndarray in three dimensions. The shape is
        (time, horizontal coordinates, vertical coordinates). The dtype
        depends on whatever GDAL read. The size of this array can be
        significant so it is better to delete the GRead object after it
        is not required.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB data...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_data is not None, (
            f'Required attribute (self._gread_data) not set!')

        assert isinstance(self._gread_data, np.ndarray), (
            f'Required attribute (self._gread_data) not a np.ndarray!')

        if self._vb:
            print_el()

        return self._gread_data

    def get_dtype_grib(self):

        '''
        Returns
        -------
        The numpy dtype of the GRIB data array.

        Note: Works only if a call to read_grib is made before.
        '''

        if self._vb:
            print_sl()

            print('Getting GRIB data data-type...')

        assert self._gread_read_flag, f'Call read_grib first!'

        assert self._gread_dtype is not None, (
            f'Required attribute (self._gread_dtype) not set!')

        assert isinstance(self._gread_dtype, np.dtype), (
            f'Required attribute (self._gread_dtype) not a np.dtype!')

        if self._vb:
            print_el()

        return self._gread_dtype

    __verify = verify
