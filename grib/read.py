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

    _grib_time_units = (
        'sec')

    _grib_time_refs = (
        'UTC')

    def __init__(self, verbose):

        assert isinstance(verbose, bool)

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

        assert isinstance(path_to_grib, (str, Path))

        path_to_grib = Path(path_to_grib)

        assert path_to_grib.exists()
        assert path_to_grib.is_file()

        self._gread_path_to_grib = path_to_grib
        return

    def verify(self):

        assert self._gread_path_to_grib is not None

        self._gread_verify_flag = True
        return

    def read_grib(self):

        assert self._gread_verify_flag

        grib_hdl = gdal.Open(str(self._gread_path_to_grib))

        assert grib_hdl is not None

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

        assert return_code == 0

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
        for i in range(band_count):
            band = grib_hdl.GetRasterBand(i + 1)

            band_meta_data = band.GetMetadata()

            ref_time_str = band_meta_data['GRIB_REF_TIME']

            parse_res = parse.search(
                '{time:12d} {unit:w} {ref:w}', ref_time_str)

            assert parse_res is not None
            assert parse_res['unit'] in self._grib_time_units
            assert parse_res['ref'] in self._grib_time_refs

            band_time = datetime.utcfromtimestamp(parse_res['time'])

            band_data = band.ReadAsArray()

            if data is None:
                data = np.empty(
                    (band_count, n_rows, n_cols), dtype=band_data.dtype)

            meta_data.append(band_meta_data)
            time_stamps.append(band_time)
            data[i,:,:] = band_data

        self._gread_meta_data = tuple(meta_data)
        self._gread_time_stamps = tuple(time_stamps)
        self._gread_data = tuple(data)

        self._gread_dtype = self._gread_data[0].dtype

        self._gread_read_flag = True
        return

    def close_grib(self):

        self._gread_handle = None
        return

    def get_spatial_properties_grib(self):

        assert self._gread_read_flag

        assert self._gread_sp_props_orig is not None

        return self._gread_sp_props_orig

    def get_grid_shape_grib(self):

        assert self._gread_read_flag

        assert self._gread_grid_shape is not None

        return self._gread_grid_shape

    def get_crs_grib(self):

        assert self._gread_read_flag

        assert self._gread_crs is not None

        return self._gread_crs

    def get_x_coordinates_grib_crnrs(self):

        assert self._gread_read_flag

        assert self._gread_x_crds_crnrs is not None

        return self._gread_x_crds_crnrs

    def get_y_coordinates_grib_crnrs(self):

        assert self._gread_read_flag

        assert self._gread_y_crds_crnrs is not None

        return self._gread_y_crds_crnrs

    def get_x_coordinates_grib_cntrs(self):

        assert self._gread_read_flag

        assert self._gread_x_crds_cntrs is not None

        return self._gread_x_crds_cntrs

    def get_y_coordinates_grib_cntrs(self):

        assert self._gread_read_flag

        assert self._gread_y_crds_cntrs is not None

        return self._gread_y_crds_cntrs

    def get_meta_data_grib(self):

        assert self._gread_read_flag

        assert self._gread_meta_data is not None

        return self._gread_meta_data

    def get_time_stamps_grib(self):

        assert self._gread_read_flag

        assert self._gread_time_stamps is not None

        return self._gread_time_stamps

    def get_data_grib(self):

        assert self._gread_read_flag

        assert self._gread_data is not None

        return self._gread_data

    def get_dtype_grib(self):

        assert self._gread_read_flag

        assert self._gread_dtype is not None

        return self._gread_dtype

    __verify = verify
