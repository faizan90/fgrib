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

    '''
    A class to convert a GRIB file to netCDF4 as it should be.

    The object inherits from other objects so before conversion, all the
    requirements of the other objects have to be satisifed as well.

    See the convert_grib_to_nc.py file in the test directory of this module
    to see an example.

    Last updated on: 2021-Sep-21
    '''

    def __init__(self, verbose=True):

        GR.__init__(self, verbose)
        GTCS.__init__(self, verbose)

        self._gtcc_verify_flag = False
        return

    def verify(self):

        '''
        Verify that all the inputs have been set correctly. Has to be called
        after all the inputs and settings are specified.
        '''

        GR._GRead__verify(self)

        GTCS._GTCSettings__verify(self)

        self._gtcc_verify_flag = True
        return

    def convert_to_nc(self, overwrite_flag=False):

        '''
        Convert the GRIB file to netCDF4. Should be called after all the
        get_* methods are called and the grib is read by calling the
        read_grib method. A temporary file is used to if the last file
        creation attempt was successful, if made.

        Parameters
        ----------
        overwrite_flag : bool
            Whether to overwrite an existing output file. Should be of the
            boolean data type. If a previous attempt was made that was
            unsuccessful, then the flag is force set to True and a new file
            is created and written to.
        '''

        assert self._gread_read_flag, f'Call read_grib first!'
        assert self._sett_verify_flag, f'Call verify first!'
        assert self._gtcc_verify_flag, f'Call verify first!'

        assert isinstance(overwrite_flag, bool), (
            f'overwrite_flag not of the boolen data type!')
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
            'Original GRIB X coordinates for cell centers.')

        x_coords_grib.crs = self._gread_crs.ExportToWkt()

        y_coords_grib.description = (
            'Original GRIB Y coordinates for cell centers.')

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

        keys_to_chk = [
            'GRIB_ELEMENT', 'GRIB_UNIT', 'GRIB_COMMENT', 'GRIB_SHORT_NAME']

        for key in keys_to_chk:
            assert all([
                key in meta_data
                for meta_data in self._gread_meta_data]), (
                    f'The key "{key}" missing in at least one '
                    f'of the time steps in GRIB meta data!')
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

        assert self._gread_read_flag, f'Call read_grib first'
        assert self._sett_verify_flag, f'Call verify first!'
        assert self._gtcc_verify_flag, f'Call verify first!'

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
            np.all(np.isfinite(y_crds_mesh_nc))), (
                f'Invalid transformed coordinates!')

        return x_crds_mesh_nc, y_crds_mesh_nc

    __verify = verify
