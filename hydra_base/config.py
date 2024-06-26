#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#
import os
import glob
import sys

PYTHONVERSION = sys.version_info
if PYTHONVERSION >= (3,2):
    import configparser as ConfigParser
else:
    import ConfigParser
import logging

global CONFIG
CONFIG = None

global localfiles
global localfile
global repofile
global repofiles
global userfile
global userfiles
global sysfile
global sysfiles

def load_config():
    """Load a config file. This function looks for a config (*.ini) file in the
    following order::

        (1) ./*.ini
        (2) ~/.config/hydra/
        (3) /etc/hydra
        (4) /path/to/hydra_base/*.ini

    (1) will override (2) will override (3) will override (4). Parameters not
    defined in (1) will be taken from (2). Parameters not defined in (2) will
    be taken from (3).  (3) is the config folder that will be checked out from
    the svn repository.  (2) Will be be provided as soon as an installable
    distribution is available. (1) will usually be written individually by
    every user."""
    global localfiles
    global localfile
    global repofile
    global repofiles
    global userfile
    global userfiles
    global sysfile
    global sysfiles
    global CONFIG
    logging.basicConfig(level='INFO')

    config = ConfigParser.ConfigParser(allow_no_value=True)

    modulepath = os.path.dirname(os.path.abspath(__file__))

    localfile = os.path.join(os.getcwd(), 'hydra.ini')
    localfiles = glob.glob(localfile)

    repofile = os.path.join(modulepath, 'hydra.ini')
    repofiles = glob.glob(repofile)

    if os.name == 'nt':
        import winpath
        userfile = os.path.join(os.path.expanduser('~'),'AppData','Local','hydra.ini')
        userfiles = glob.glob(userfile)

        sysfile = os.path.join(winpath.get_common_documents(), 'Hydra','hydra.ini')
        sysfiles = glob.glob(sysfile)
    else:
        userfile = os.path.join(os.path.expanduser('~'), '.hydra', 'hydra.ini')
        userfiles = glob.glob(userfile)

        sysfile = os.path.join('etc','hydra','hydra.ini')
        sysfiles = glob.glob(sysfile)


    for ini_file in repofiles:
        logging.debug("Repofile: %s"%ini_file)
        config.read(ini_file)
    for ini_file in sysfiles:
        logging.debug("Sysfile: %s"%ini_file)
        config.read(ini_file)
    for ini_file in userfiles:
        logging.debug("Userfile: %s"%ini_file)
        config.read(ini_file)
    for ini_file in localfiles:
        logging.info("Localfile: %s"%ini_file)
        config.read(ini_file)

    env_value = os.environ.get('HYDRA_CONFIG')
    if env_value is not None:

        if os.path.isabs(env_value):
            config_path = env_value
        else:
            config_path = os.path.join(os.getcwd(), env_value)
        if os.path.exists(config_path):
            logging.info("Setting config from {}".format(config_path))
            config.read(config_path)
        else:
            logging.warning('HYDRA_CONFIG set as %s but file does not exist', env_value)


    if os.name == 'nt':
        set_windows_env_variables(config)

    try:
        home_dir = config.get('DEFAULT', 'home_dir')
    except:
        home_dir = os.environ.get('HYDRA_HOME_DIR', '~')
    config.set('DEFAULT', 'home_dir', os.path.expanduser(home_dir))

    try:
        hydra_base = config.get('DEFAULT', 'hydra_base_dir')
    except:
        hydra_base = os.environ.get('HYDRA_BASE_DIR', modulepath)
    config.set('DEFAULT', 'hydra_base_dir', os.path.expanduser(hydra_base))

    # read values from environment using pattern HYDRA__section_key__options_key (case insensitive)
    # i.e., all hydra.ini settings can be set via environment variables
    for k, v in os.environ.items():
        parts = k.split('__')
        if len(parts) == 3 and parts[0] == 'HYDRA':
            section_key = parts[1]
            if section_key.lower() == 'default':
                section_key = section_key.upper()
            else:
                section_key = section_key.lower()
            options_key = parts[2].lower()
            config.set(section_key, options_key, v)

    CONFIG = config

    return config


def set_windows_env_variables(config):
    import winpath
    config.set('DEFAULT', 'common_app_data_folder', winpath.get_common_appdata())
    config.set('DEFAULT', 'win_local_appdata', winpath.get_local_appdata())
    config.set('DEFAULT', 'win_appdata', winpath.get_appdata())
    config.set('DEFAULT', 'win_desktop', winpath.get_desktop())
    config.set('DEFAULT', 'win_programs', winpath.get_programs())
    config.set('DEFAULT', 'win_common_admin_tools', winpath.get_common_admin_tools())
    config.set('DEFAULT', 'win_common_documents', winpath.get_common_documents())
    config.set('DEFAULT', 'win_cookies', winpath.get_cookies())
    config.set('DEFAULT', 'win_history', winpath.get_history())
    config.set('DEFAULT', 'win_internet_cache', winpath.get_internet_cache())
    config.set('DEFAULT', 'win_my_pictures', winpath.get_my_pictures())
    config.set('DEFAULT', 'win_personal', winpath.get_personal())
    config.set('DEFAULT', 'win_my_documents', winpath.get_my_documents())
    config.set('DEFAULT', 'win_program_files', winpath.get_program_files())
    config.set('DEFAULT', 'win_program_files_common', winpath.get_program_files_common())
    config.set('DEFAULT', 'win_system', winpath.get_system())
    config.set('DEFAULT', 'win_windows', winpath.get_windows())
    config.set('DEFAULT', 'win_startup', winpath.get_startup())
    config.set('DEFAULT', 'win_recent', winpath.get_recent())

def get(section, option, default=None):

    if CONFIG is None:
        load_config()

    try:
        return CONFIG.get(section, option)
    except:
        return default

def getint(section, option, default=None):

    if CONFIG is None:
        load_config()

    try:
        return CONFIG.getint(section, option)
    except:
        return default
