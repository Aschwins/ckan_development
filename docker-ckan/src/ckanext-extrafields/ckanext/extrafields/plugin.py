import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    # plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    # Overwrite create_package_schema method
    def create_package_schema(self):
        # Grab the default schema for our plugin from the DefaultDatasetForm class.
        schema = super(ExtrafieldsPlugin, self).create_package_schema()
        schema.update({
            'custom_text': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).update_package_schema()

        # Our custom field

        schema.update({
            'custom_text': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).show_package_schema()

        # Our custom field
        schema.update({
            'custom_text': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []

    # IConfigurer edits
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'extrafields')
