"""
This plugin serves as a first setup to whenever a file with data_category = px_abundancies gets uploaded. The excel file
get unpacked and the different csvs get uploaded.

Python 2.7.15
numpy-1.16.5
pandas-0.24.2
xlrd-1.2.0
"""
import os
import logging
import ckan.logic as logic

from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload
from ckan.lib.uploader import _get_underlying_file

from xlrd import open_workbook
import csv

MB = 1 << 20

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="log.log")


def excel_to_csv(filepath, directory):
    """
    doc
    """
    wb = open_workbook(filepath)

    logger.debug("Found a workbook: {0}".format(wb))
    result = []

    for i in range(wb.nsheets):
        sheet = wb.sheet_by_index(i)
        file_location_filename = "{0}/{1}.csv".format(directory, sheet.name)
        result.append(file_location_filename)
        logger.debug("New file location filename: {0}".format(file_location_filename))
        with open(file_location_filename, "w") as f:
            writer = csv.writer(f, delimiter=",")
            header = [cell.value for cell in sheet.row(0)]
            writer.writerow(header)
            for row_idx in range(1, sheet.nrows):
                row = [cell.value for cell in sheet.row(row_idx)]
                writer.writerow(row)

    logger.debug("Created csvs in : {0}".format(result))
    return result


def _copy_file(input_file, output_file, max_size):
    input_file.seek(0)
    current_size = 0
    while True:
        current_size = current_size + 1
        # MB chunks
        data = input_file.read(MB)

        if not data:
            break
        output_file.write(data)
        if current_size > max_size:
            raise logic.ValidationError({'upload': ['File upload too large']})


class ExceltocsvPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IUploader, inherit=True)

    def get_resource_uploader(self, data_dict):
        return ResourceUpload(data_dict)


class ResourceUpload(DefaultResourceUpload):
    path_prefix = 'filename_prefix_'

    def get_path(self, id):
        directory = self.get_directory(id)
        filepath = os.path.join(
            directory, '{}_{}'.format(self.path_prefix, id[6:]))
        logger.debug(u"[IUPLOADER], filepath: {}".format(filepath)) #filepath: /var/lib/ckan/resources/a48/b1e/filename_prefix__62-9d1f-4ef6-ba2a-687a0ccd7f15
        return filepath

    def upload(self, id, max_size=10):
        '''Actually upload the file.

        :returns: ``'file uploaded'`` if a new file was successfully uploaded
            (whether it overwrote a previously uploaded file or not),
            ``'file deleted'`` if an existing uploaded file was deleted,
            or ``None`` if nothing changed
        :rtype: ``string`` or ``None``

        '''
        if not self.storage_path:
            return

        # Get directory and filepath on the system
        # where the file for this resource will be stored
        directory = self.get_directory(id)
        filepath = self.get_path(id)
        logger.debug(u"[UPLOAD] Directory: {0}".format(directory))
        logger.debug(u"[UPLOAD] filepath: {0}".format(filepath))
        logger.debug(u"[UPLOAD] filename: {0}".format(self.filename))
        logger.debug(u"[UPLOAD] filename: {0}".format(self.upload_file))

        # If a filename has been provided (a file is being uploaded)
        # we write it to the filepath (and overwrite it if it already
        # exists). This way the uploaded file will always be stored
        # in the same location
        if self.filename:
            try:
                os.makedirs(directory)
            except OSError as e:
                # errno 17 is file already exists
                if e.errno != 17:
                    raise
            tmp_filepath = filepath + '~'
            with open(tmp_filepath, 'wb+') as output_file:
                try:
                    _copy_file(self.upload_file, output_file, max_size)
                except logic.ValidationError:
                    os.remove(tmp_filepath)
                    raise
                finally:
                    self.upload_file.close()
            os.rename(tmp_filepath, filepath)

            upload_csv = _get_underlying_file(self.upload_field_storage)


            # If the resource extension is a .xlsx file we parse the sheets and also upload the csvs
            if self.filename.split('.')[-1] == 'xlsx': # using os for this is safer.
                csvs = excel_to_csv(filepath, directory)

                for comma_seperated_value_file in csvs:
                    count = 0
                    tmp_filepath = filepath + "{0}".format(count) + '~'
                    logger.debug("tmp_filepath created:".format(tmp_filepath))
                    with open(tmp_filepath, 'wb+') as output_file:
                        try:
                            _copy_file(comma_seperated_value_file, output_file, max_size)
                        except logic.ValidationError:
                            os.remove(tmp_filepath)
                            raise
                        finally:
                            comma_seperated_value_file.close()
                    count +=1
            os.rename(tmp_filepath, filepath)

            return



        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear:
            try:
                os.remove(filepath)
            except OSError as e:
                pass



