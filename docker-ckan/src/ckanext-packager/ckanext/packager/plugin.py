import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
import logging
import requests
import os

from xlrd import open_workbook
import pandas as pd

# Logger settings.
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="log.log")

# Global variables
SITE_URL = config.get('ckan.site_url', None)  # Does not end in /


def download_file(url, filepath_to_store_file):
    request = requests.get(url, allow_redirects=True)
    open(filepath_to_store_file, 'wb').write(request.content)
    logger.debug("DOWNLOADED FILE in {0}".format(filepath_to_store_file))
    return filepath_to_store_file


def get_user_api_key():
    cntxt = toolkit.c
    return cntxt.userobj.apikey


def create_resource(filepath, package_id, api_key, name="Default"):
    """
    Function to create a resource via the API. Could maybe also be done with ckan.action function.
    TODO: Should be able to handle a lot more: minimum is data category included.
    :param filepath:
    :param package_id:
    :param api_key:
    :param name:
    :return:
    """
    logger.debug("CREATING RESOURCE THROUGH THE API.")
    with open(filepath, 'rb') as f:
        files = {"upload": f}
        values = {"package_id": package_id, "name": name}
        headers = {"Authorization": api_key}
        api_url = "{0}/api/action/resource_create".format(SITE_URL)
        r = requests.post(api_url, files=files, data=values, headers=headers)

    logger.debug("\n Created resource...")
    return r.status_code


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        logger.debug("File doesn't exist.")


def excel_to_csv(filepath, outputpath):
    """
    Takes an excel in filepath and spits out csvs for every sheet in the excel in the outputpath.
    :return a list of filepaths of the csvs.
    """
    logger.debug("Filepath: {0}".format(filepath))
    wb = open_workbook(filepath)
    filename = os.path.basename(filepath)
    name = os.path.splitext(filename)[0]

    result = []

    for i in range(wb.nsheets):
        excel = pd.read_excel(filepath, sheet_name=i)
        sheet = wb.sheet_by_index(i)
        filepath_to_write_csv = os.path.join(outputpath, name + sheet.name + '.csv')
        excel.to_csv(filepath_to_write_csv, encoding='utf-8', decimal=',')
        result.append(filepath_to_write_csv)

    logger.debug("Created csvs in : {0}".format(result))
    return result


def preprocess_px_abundancies(resource):
    """
    The preprocessing pipeline for a px_abundancies file. This function calls excel_to_csv to convert the sheets
    in the excel to seperate csvs. Then it uploads the csvs to CKAN with the api. Then deletes the csvs.
    """
    filename = resource.get("name")
    url = resource.get("url")
    package_id = resource.get("package_id")
    API_KEY = get_user_api_key()

    # Download excel
    logger.debug("CREATING NEW EXCEL...")
    filepath_download = download_file(url, filename)

    # Convert excel file to seperate csv's
    csv_filepaths = excel_to_csv(filepath_download, os.getcwd())
    logger.debug("csv_filepaths: {}".format(csv_filepaths))

    # # Upload Excel Under Different Name
    for csv_filepath in csv_filepaths:
        csv_filename = os.path.basename(csv_filepath)
        status_code = create_resource(csv_filepath, package_id, API_KEY, name=csv_filename)
        delete_file(csv_filepath)
        logger.debug("SUCCES = {0}".format(status_code))

    delete_file(filepath_download)


def preprocessing_pipeline(resources):
    """
    The Preprocessing pipeline for all resources. If a resource needs preprocessing it should be called within this
    function.
    """
    for resource in resources:
        if (resource.get("data_category") == "px_abundancies") & (resource.get('preprocessing_done') != 'True'):
            preprocess_px_abundancies(resource)
            id = resource.get('id')
            toolkit.get_action('resource_patch')({}, {'id': id, 'preprocessing_done': 'True'})
            #ckan.logic.action.update.resource_update(context, data_dict)
            #ckan.logic.action.patch.resource_patch(context, data_dict)

    # Above should should be rewritten so it handles the pipelines for each data category. Which means for each
    # category it should check if it has a preprocessing pipeline, done yes or no, do it yes or no.


class PackagerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    # IPackageController
    def before_view(self, pkg_dict):
        u'''
            Before a dataset get's displayed a check is done on the dataset.
            If Prepocessing steps have to be taken for the dataset they are done.
        '''
        logger.debug("BEFORE VIEW")
        logger.debug("\n\n pkg_dict: {0} \n\n".format(pkg_dict))
        resources = pkg_dict.get("resources")

        # Check if it has resources which need preprocessing.
        if len(resources) >= 1:
            preprocessing_pipeline(resources)

        return pkg_dict
