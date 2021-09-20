'''
@author: Faizan3800X-Uni

Sep 16, 2021

10:09:50 AM
'''
import pyproj
import numpy as np
import netCDF4 as nc

from ..grib import GRead as GR
from .settings import GTCSettings as GTCS


class GTCConvert(GR, GTCS):

    def __init__(self, verbose=True):

        GR.__init__(self, verbose)
        GTCS.__init__(self, verbose)

        self._gtcc_verify_flag = False
        return

    def verify(self):

        GR._GRead__verify(self)

        GTCS._GTCSettings__verify(self)

        self._gtcc_verify_flag = True
        return

    def convert_to_nc(self, overwrite_flag=False):

        assert self._gread_read_flag
        assert self._sett_verify_flag
        assert self._gtcc_verify_flag

        assert isinstance(overwrite_flag, bool)
        #======================================================================

        # Used to determine if the file was converted correctly.
        temp_file_path = self._sett_path_to_nc.parents[0] / (
            f'{self._sett_path_to_nc.name}.tmp')

        if temp_file_path.exists():
            overwrite_flag = True

        else:
            open(temp_file_path, 'w')

        if (not overwrite_flag) and self._sett_path_to_nc.exists():

            temp_file_path.unlink()
            return
        #======================================================================

        nc_hdl = nc.Dataset(str(self._sett_path_to_nc), mode='w')

        nc_hdl.set_auto_mask(False)
        #======================================================================

        nc_hdl.createDimension(
            self._sett_nc_x_cntrs_dim_lab, self._gread_x_crds_cntrs.shape[0])

        nc_hdl.createDimension(
            self._sett_nc_y_cntrs_dim_lab, self._gread_y_crds_cntrs.shape[0])

        x_coords_grib = nc_hdl.createVariable(
            self._sett_nc_x_cntrs_var_lab,
            self._gread_x_crds_cntrs.dtype,
            dimensions=(self._sett_nc_x_cntrs_dim_lab),
            zlib=True)

        y_coords_grib = nc_hdl.createVariable(
            self._sett_nc_y_cntrs_var_lab,
            self._gread_y_crds_cntrs.dtype,
            dimensions=(self._sett_nc_y_cntrs_dim_lab),
            zlib=True)

        x_coords_grib[:] = self._gread_x_crds_cntrs
        y_coords_grib[:] = self._gread_y_crds_cntrs

        x_coords_grib.description = (
            'Original (rotated) GRIB X coordinates for cell centers.')

        x_coords_grib.crs = self._gread_crs.ExportToWkt()

        y_coords_grib.description = (
            'Original (rotated) GRIB Y coordinates for cell centers.')

        y_coords_grib.crs = x_coords_grib.crs
        #======================================================================

        nc_hdl.createDimension(
            self._sett_nc_x_crnrs_dim_lab, self._gread_x_crds_crnrs.shape[0])

        nc_hdl.createDimension(
            self._sett_nc_y_crnrs_dim_lab, self._gread_y_crds_crnrs.shape[0])

        x_coords_nc = nc_hdl.createVariable(
            self._sett_nc_x_crnrs_var_lab,
            self._gread_x_crds_crnrs.dtype,
            zlib=True,
            dimensions=(
                self._sett_nc_y_crnrs_dim_lab, self._sett_nc_x_crnrs_dim_lab))

        y_coords_nc = nc_hdl.createVariable(
            self._sett_nc_y_crnrs_var_lab,
            self._gread_y_crds_crnrs.dtype,
            zlib=True,
            dimensions=(
                self._sett_nc_y_crnrs_dim_lab, self._sett_nc_x_crnrs_dim_lab))

        tfmd_crds = self._get_crnr_tfmd_crds()

        x_coords_nc[:,:] = tfmd_crds[0]
        y_coords_nc[:,:] = tfmd_crds[1]

        del tfmd_crds

        x_coords_nc.description = (
            'Transformed GRIB X coordinates for cell corners.')

        x_coords_nc.crs = self._sett_nc_crs.ExportToWkt()

        y_coords_nc.description = (
            'Transformed GRIB Y coordinates for cell corners.')

        y_coords_nc.crs = x_coords_nc.crs
        #======================================================================

        nc_hdl.createDimension(
            self._sett_nc_time_lab, self._gread_sp_props_orig.band_count)

        time_nc = nc_hdl.createVariable(
            self._sett_nc_time_lab,
            'i8',
            dimensions=self._sett_nc_time_lab,
            zlib=True)

        time_nc[:] = nc.date2num(
            self._gread_time_stamps,
            units=self._sett_nc_units,
            calendar=self._sett_nc_calendar)

        time_nc.units = self._sett_nc_units
        time_nc.calendar = self._sett_nc_calendar
        #======================================================================

        nc_var = nc_hdl.createVariable(
            self._gread_meta_data[0]['GRIB_ELEMENT'],
            self._gread_dtype,
            fill_value=False,
            zlib=True,
            dimensions=(
                self._sett_nc_time_lab,
                self._sett_nc_y_cntrs_dim_lab,
                self._sett_nc_x_cntrs_dim_lab))

        nc_var.units = self._gread_meta_data[0]['GRIB_UNIT']
        nc_var.standard_name = self._gread_meta_data[0]['GRIB_COMMENT']
        nc_var.short_name = self._gread_meta_data[0]['GRIB_SHORT_NAME']

        nc_var[:,:,:] = self._gread_data
        #======================================================================

        nc_hdl.Source = str(self._gread_path_to_grib)
        nc_hdl.close()
        #======================================================================

        temp_file_path.unlink()
        return

    def _get_crnr_tfmd_crds(self):

        assert self._gread_read_flag
        assert self._sett_verify_flag
        assert self._gtcc_verify_flag

        x_crds_mesh_grib, y_crds_mesh_grib = np.meshgrid(
            self._gread_x_crds_crnrs, self._gread_y_crds_crnrs)

        tfmr = pyproj.Transformer.from_crs(
            self._gread_crs.ExportToWkt(),
            self._sett_nc_crs.ExportToWkt(),
            always_xy=True)

        x_crds_mesh_nc, y_crds_mesh_nc = tfmr.transform(
            x_crds_mesh_grib, y_crds_mesh_grib)

        assert (
            np.all(np.isfinite(x_crds_mesh_nc)) and
            np.all(np.isfinite(y_crds_mesh_nc)))

        return x_crds_mesh_nc, y_crds_mesh_nc

    __verify = verify
