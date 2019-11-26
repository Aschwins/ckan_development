#!/bin/bash

# Install any local extensions in the src_extensions volume
echo "Setting up environment variables..."
echo "Extension config vars"

# Set ckanext-scheming variables
echo "Enabling Scheming "
paster --plugin=ckan config-tool $CKAN_INI -s $CKAN_INI "scheming.dataset_schemas = ckanext.scheming:ana_dataset_tweaked.json"
paster --plugin=ckan config-tool $CKAN_INI -s $CKAN_INI "scheming.presets = ckanext.scheming:presets.json"
paster --plugin=ckan config-tool $CKAN_INI -s $CKAN_INI "scheming.dataset_fallback = false"