# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

def most_popular_groups():
    '''Return a sorted list of the groups with the most datasets.'''

    # Get a list of all the site's groups from CKAN, sorted by number of
    # datasets.
    groups = toolkit.get_action('group_list')(
        data_dict={'all_fields': True})

    # groups = toolkit.get_action('member_list')(
    #     data_dict={'id': 'curators', 'object_type': 'user'})

    # Truncate the list to the 10 most popular groups only.
    # groups = groups[:10]

    return groups

class Example_ThemePlugin(plugins.SingletonPlugin):
    # Declare that this plugin will implement IConfigurer.
    plugins.implements(plugins.IConfigurer)

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'example_theme')

    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'example_theme_most_popular_groups': most_popular_groups}