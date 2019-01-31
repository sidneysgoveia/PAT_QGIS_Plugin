# -*- coding: utf-8 -*-
"""
/***************************************************************************
  CSIRO Precision Agriculture Tools (PAT) Plugin
  pat_plugin - This script initializes the plugin, making it known to QGIS.
           -------------------
        begin      : 2017-05-25
        git sha    : $Format:%H$
        copyright  : (c) 2018, Commonwealth Scientific and Industrial Research Organisation (CSIRO)
        email      : PAT@csiro.au PAT@csiro.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the associated CSIRO Open Source Software       *
 *   License Agreement (GPLv3) provided with this plugin.                  *
 *                                                                         *
 ***************************************************************************/

"""

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import site
import sys
import tempfile
import osgeo.gdal
import logging
import resources  # import resources like icons for the plugin
import qgis.utils
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QMessageBox

PLUGIN_DIR = os.path.abspath( os.path.dirname(__file__))
PLUGIN_NAME = "PAT"
PLUGIN_SHORT= "PAT"
LOGGER_NAME = 'pyprecag'
TEMPDIR = os.path.join(tempfile.gettempdir(), PLUGIN_NAME)

''' Adds the path to the external libraries to the sys.path if not already added'''
if PLUGIN_DIR not in sys.path:
    sys.path.append(PLUGIN_DIR)

# if os.path.join(PLUGIN_DIR, 'ext-libs') not in sys.path:
#     site.addsitedir(os.path.join(PLUGIN_DIR, 'ext-libs'))

def classFactory(iface):
    """Load pat_toolbar class from file pat_toolbar.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    if not os.path.exists(TEMPDIR):
        os.mkdir(TEMPDIR)

    from pat_plugin.util.settings import read_setting, write_setting
    if read_setting(PLUGIN_NAME + "/DISP_TEMP_LAYERS") is None:
        write_setting(PLUGIN_NAME + "/DISP_TEMP_LAYERS", False)
    
    if read_setting(PLUGIN_NAME + "/DEBUG") is None:
        write_setting(PLUGIN_NAME + "/DEBUG", False)

    try:
        from pyprecag import config
        config.set_debug_mode(read_setting(PLUGIN_NAME + "/DEBUG",bool))
    except ImportError:
        # pyprecag is not yet installed
        pass

    # the custom logging import requires qgis_config so leave it here
    from pat_plugin.util.custom_logging import setup_logger

    # Call the logger pyprecag so it picks up the module debugging as well.
    setup_logger(LOGGER_NAME)
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.addHandler( logging.NullHandler())   # logging.StreamHandler()
    
    from pat_plugin.util.check_dependencies import check_gdal_dependency
    
    gdal_ver, check_gdal = check_gdal_dependency()  
    
    if not check_gdal:
        # TODO: Implement running the BAT file from within QGIS see https://jira.csiro.au/browse/PA-67
        LOGGER.critical('QGIS Version {} and GDAL {} is are not currently supported.'.format(qgis.utils.QGis.QGIS_VERSION, gdal_ver))
        
        message = 'QGIS Version {} and GDAL {}  are not currently supported. Downgrade QGIS to an earlier version. If required email PAT@csiro.au for assistance.'.format(qgis.utils.QGis.QGIS_VERSION, gdal_ver)
        
        iface.messageBar().pushMessage("ERROR Failed Dependency Check", message, level=QgsMessageBar.CRITICAL,
                                       duration=0)
        QMessageBox.critical(None, 'Failed Dependency Check', message)
        sys.exit(message)
    
    from pat_plugin.util.check_dependencies import check_python_dependencies, check_vesper_dependency
        
    check_python_dependencies(PLUGIN_DIR, iface)
    vesper_exe = check_vesper_dependency()

    # Retrieve values from the plugin metadata file
    cfg = configparser.SafeConfigParser()
    cfg.read(os.path.join(PLUGIN_DIR, 'metadata.txt'))
    version = cfg.get('general', 'version')

    plugin_state = 'PAT Plugin State:\n'
    plugin_state += '    {:20}\t{}\n'.format('QGIS Version:', qgis.utils.QGis.QGIS_VERSION)
    plugin_state += '    {:20}\t{}\n'.format('Python Version:',  sys.version)
    plugin_state += '    {:20}\t{}\n'.format('PAT Version:', version)
    
    LOGGER.info(plugin_state)
    from pat_toolbar import pat_toolbar

    return pat_toolbar(iface)