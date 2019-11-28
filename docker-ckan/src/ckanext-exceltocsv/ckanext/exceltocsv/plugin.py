"""
This plugin serves as a first setup to whenever a file with data_category = px_abundancies gets uploaded. The excel file
get unpacked and the different csvs get uploaded.

"""
import os
import logging

from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="log.log")


class ExceltocsvPlugin(plugins.SingletonPlugin, DefaultResourceUpload):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'exceltocsv')

    # IActions
    # plugins.implements(plugins.IActions)

    # IResourceController
    # plugins.implements(plugins.IResourceController)

    # IUploader
    plugins.implements(plugins.IUploader, inherit=True)

    # def get_path(self, id):
    #     directory = self.get_directory(id)
    #     filepath = os.path.join(directory, id[6:])
    #     logger.debug("PATH: {0}".format(filepath))
    #     return filepath
