"""
This CKAN plugin implements the IDatasetForm to follow the DefaultDatasetForm, remove redundant fields and add the
following fields:
- data_category \in {'px_sample_info', 'px_abundancies', 'fasta_file'}
"""

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="log.log")

keys_to_remove = [u'version', u'author', u'url', u'maintainer', u'author_email', u'maintainer_email', u'private']


def get_data_categories():
    """
    Data categories define what has to be done with the data.
    :return: All available data categories.
    """
    return [u"open", u"px_sample_info", u"px_abundancies", u"px_fasta_file"]


class daschemePlugin(plugins.SingletonPlugin, plugins.toolkit.DefaultDatasetForm):
    # IConfigurer
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'extrafields')

    # ITemplatehelpers
    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        """
        Register the get_data_categories function to the template helpers.
        """
        logger.debug("Added new helper function.")
        return {"dascheme_get_data_categories": get_data_categories}

    # IDatasetForm
    plugins.implements(plugins.IDatasetForm)

    def is_fallback(self):
        """
        :return: Set dascheme as DefaultDataSetForm
        """
        return True

    def create_package_schema(self):
        """Return the schema for validating new dataset dicts.

        CKAN will use the returned schema to validate and convert data coming
        from users (via the dataset form or API) when creating new datasets,
        before entering that data into the database.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``create_package_schema()``
        method to get the default schema and then modify and return it.

        CKAN's ``convert_to_tags()`` or ``convert_to_extras()`` functions can
        be used to convert custom fields into dataset tags or extras for
        storing in the database.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary
        """
        schema = super(daschemePlugin, self).create_package_schema()
        logger.debug(u"CREATE: Found Schema: {0}".format(schema))
        schema.update({
            'data_category': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })

        for key in keys_to_remove:
            logger.debug("deleting key: {}".format(key))
            del schema[key]

        logger.debug(u"CREATE: Set Schema to: {0}".format(schema))
        return schema

    def update_package_schema(self):
        """Return the schema for validating updated dataset dicts.

        CKAN will use the returned schema to validate and convert data coming
        from users (via the dataset form or API) when updating datasets, before
        entering that data into the database.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``update_package_schema()``
        method to get the default schema and then modify and return it.

        CKAN's ``convert_to_tags()`` or ``convert_to_extras()`` functions can
        be used to convert custom fields into dataset tags or extras for
        storing in the database.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary

        """
        schema = super(daschemePlugin, self).update_package_schema()

        # Our custom field
        logger.debug(u"UPDATE: Found Schema: {0}".format(schema))
        schema.update({
            'data_category': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        for key in keys_to_remove:
            del schema[key]

        logger.debug(u"UPDATE: Set Schema to: {0}".format(schema))
        return schema

    def show_package_schema(self):
        """
        Return a schema to validate datasets before they're shown to the user.

        CKAN will use the returned schema to validate and convert data coming
        from the database before it is returned to the user via the API or
        passed to a template for rendering.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``show_package_schema()``
        method to get the default schema and then modify and return it.

        If you have used ``convert_to_tags()`` or ``convert_to_extras()`` in
        your ``create_package_schema()`` and ``update_package_schema()`` then
        you should use ``convert_from_tags()`` or ``convert_from_extras()`` in
        your ``show_package_schema()`` to convert the tags or extras in the
        database back into your custom dataset fields.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary

        """

        schema = super(daschemePlugin, self).show_package_schema()

        # Our custom field
        schema.update({
            'data_category': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        for key in keys_to_remove:
            del schema[key]

        logger.debug(u"Showing Schema: {0}".format(schema))
        return schema

    def package_types(self):
        return []
