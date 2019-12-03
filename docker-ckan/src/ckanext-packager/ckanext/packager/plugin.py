import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import requests
import os
import threading

from ckan.common import config, c

# Logger settings.
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="log.log")

# Global variables
SITE_URL = config.get('ckan.site_url', None)
logger.debug("SET SITE_URL TO: {0}".format(SITE_URL))


def download_file(url, filepath_to_store_file):
    request = requests.get(url, allow_redirects=True)
    open(filepath_to_store_file, 'wb').write(request.content)
    logger.debug("DOWNLOADED FILE in {0}".format(filepath_to_store_file))
    return filepath_to_store_file


def create_resource(filepath, package_id, api_key):
    logger.debug("CREATING RESOURCE THROUGH THE API.")
    with open(filepath, 'rb') as f:
        files = {"upload": f}
        values = {"package_id": package_id}
        headers = {"Authorization": api_key}
        api_url = "{0}/api/action/resource_create".format(SITE_URL)
        r = requests.post(api_url, files=files, data=values, headers=headers)
        logger.debug("Request response: {0}".format(r.content))

    logger.debug("\n Created resource...")
    delete_file(filepath)


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        logger.debug("File doesn't exist.")


class PackagerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController, inherit=True)

    # IPackageController
    def read(self, entity):
        u'''Called after IGroupController.before_view inside package_read.
        '''
        logger.debug("READ")
        pass

    def create(self, entity):
        u'''Called after group had been created inside package_create.
        '''
        logger.debug("CREATE")
        pass

    def edit(self, entity):
        u'''Called after group had been updated inside package_update.
        '''
        logger.debug("EDIT:")
        pass

    def delete(self, entity):
        u'''Called before commit inside package_delete.
        '''
        logger.debug("[DELETE]")
        pass

    def after_create(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            has been created (Note that the create method will return a package
            domain object, which may not include all fields). Also the newly
            created package id will be added to the dict.
        '''
        logger.debug("[AFTER_CREATE]: ")
        pass

    def after_update(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            has been updated (Note that the edit method will return a package
            domain object, which may not include all fields).
        '''
        # Upload the csvs as resources to this dataset.
        # Done

    def after_delete(self, context, pkg_dict):
        u'''
            Extensions will receive the data dict (tipically containing
            just the package id) after the package has been deleted.
        '''
        logger.debug("AFTER_DELETE")
        pass

    def after_show(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            is ready for display (Note that the read method will return a
            package domain object, which may not include all fields).
        '''
        logger.debug("AFTER_SHOW")
        pass

    def before_search(self, search_params):
        u'''
            Extensions will receive a dictionary with the query parameters,
            and should return a modified (or not) version of it.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''
        logger.debug("BEFORE SEARCH: search_params: {0}".format(search_params))
        return search_params

    def after_search(self, search_results, search_params):
        u'''
            Extensions will receive the search results, as well as the search
            parameters, and should return a modified (or not) object with the
            same structure:

                {'count': '', 'results': '', 'facets': ''}

            Note that count and facets may need to be adjusted if the extension
            changed the results for some reason.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''
        logger.debug("AFTER SEARCH")

        return search_results

    def before_index(self, pkg_dict):
        u'''
             Extensions will receive what will be given to the solr for
             indexing. This is essentially a flattened dict (except for
             multli-valued fields such as tags) of all the terms sent to
             the indexer. The extension can modify this by returning an
             altered version.
        '''
        logger.debug("BEFORE INDEX: pkg_dict")
        return pkg_dict

    def before_view(self, pkg_dict):
        u'''
             Extensions will recieve this before the dataset gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        logger.debug("BEFORE VIEW")
        api_key = c.get("userobj").apikey
        resources = pkg_dict.get("resources")

        if (len(resources) == 1) & (pkg_dict.get("data_category") == u"px_abundancies"):
            logger.debug("RESOURCES IN PACKAGE FOUND.")
            for i in range(len(resources)):
                if pkg_dict.get("resources")[i].get("format") in ("xlsx", "XLSX"):
                    logger.debug("EXCEL FILE FOUND.")
                    url = pkg_dict.get("resources")[i].get("url")
                    resource_id = pkg_dict.get("resources")[i].get("id")
                    package_id = pkg_dict.get("resources")[i].get("package_id")
                    xlsx_url = "{}/dataset/{}/resource/{}/download/{}".format(
                        SITE_URL,
                        package_id, resource_id, url)
                    logger.debug("XLSX url: {0}".format(xlsx_url))

                    # Download excel
                    logger.debug("CREATING NEW EXCEL...")
                    filepath_download = download_file(xlsx_url, "new_excel.xlsx")

                    # Upload Excel Under Different Name and wait
                    thread = threading.Thread(target=create_resource, args=(filepath_download, package_id, api_key))
                    thread.start()
                    logger.debug("Started Thread, now waiting on create_resource...")
                    thread.join()
                    logger.debug("SUCCES = ")

        return pkg_dict