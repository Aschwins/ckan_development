import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

keys_to_remove = [u'version', u'author', u'url', u'maintainer', u'author_email', u'maintainer_email', u'private']

def get_data_categories():
    """
    Data categories define what has to be done with the data.
    :return: All available data categories.
    """
    return [u"open", u"px_sample_info", u"px_abundancies", u"px_fasta_file"]


class DsmschemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IDatasetForm, inherit=False)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dsmscheme')

    def get_helpers(self):
        return {'dsmscheme_get_data_categories': get_data_categories}

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _modify_package_schema(self, schema):
        # Add our custom country_code metadata field to the schema.
        schema['resources'].update({
                'data_category' : [ toolkit.get_validator('ignore_missing') ]
                })

        for key in keys_to_remove:
            del schema[key]

        return schema

    def create_package_schema(self):
        schema = super(DsmschemePlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(DsmschemePlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(DsmschemePlugin, self).show_package_schema()

        schema['resources'].update({
                'data_category' : [ toolkit.get_validator('ignore_missing') ]
            })

        for key in keys_to_remove:
            del schema[key]
        return schema

    def setup_template_variables(self, context, data_dict):
        return super(DsmschemePlugin, self).setup_template_variables(
                context, data_dict)

    def new_template(self):
        return super(DsmschemePlugin, self).new_template()

    def read_template(self):
        return super(DsmschemePlugin, self).read_template()

    def edit_template(self):
        return super(DsmschemePlugin, self).edit_template()

    def search_template(self):
        return super(DsmschemePlugin, self).search_template()

    def history_template(self):
        return super(DsmschemePlugin, self).history_template()

    def package_form(self):
        return super(DsmschemePlugin, self).package_form()

    def check_data_dict(self, data_dict, schema=None):
        pass
