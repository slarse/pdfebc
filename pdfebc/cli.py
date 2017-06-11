# -*- coding: utf-8 -*-
"""This module contains the argument parser for the pdfebc program.

.. module:: cli
    :platform: Unix
    :synopsis: The pdfebc CLI.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import argparse
import sys
import os
from . import utils

OUT_DIR_DEFAULT = "pdfebc_out"
SRC_DIR_DEFAULT = "."
GHOSTSCRIPT_BINARY_DEFAULT = "gs"

DESCRIPTION = "CLI tool for compressing PDF files, and sending the output via e-mail."
OUT_DIR_SHORT = "-o"
OUT_DIR_LONG = "--outdir"
OUT_DIR_HELP = "Output directory. Defaults to '{}'".format(OUT_DIR_DEFAULT)
SRC_DIR_SHORT = "-s"
SRC_DIR_LONG = "--srcdir"
SRC_DIR_HELP = "Source directory, 'pdfebc' will look for PDF files here. Defaults to '{}'".format(
    SRC_DIR_DEFAULT)
GS_SHORT = "-gs"
GS_LONG = "--ghostscript"
GS_HELP = "Specify the name of the Ghostscript binary. Defaults to '{}'.".format(
    GHOSTSCRIPT_BINARY_DEFAULT)
SEND_SHORT = "-e"
SEND_LONG = "--email"
SEND_HELP = "Attempt to send the compressed PDF files with the settings in config.ini."
CLEAN_SHORT = "-c"
CLEAN_LONG = "--clean"
CLEAN_HELP = """Automatically remove output directory after finishing the program.
Most useful in conjuction with {}.""".format(SEND_LONG)
STATUS_SHORT = "-cs"
STATUS_LONG = "--configstatus"
STATUS_HELP = "Show the location and health of the configuration file."

CONFIG_STATUS = """
#############################
# CONFIGURATION FILE STATUS #
#############################
Location: '{}'

Health: {}
"""
NO_CONFIG_FOUND = """No configuration file could be found.
Please place one at: '{}'

See 'https://github.com/slarse/pdfebc' for more information.
"""

CONFIG_CONTENTS = """
Configuration currently looks like this:
{start}
{}
{end}
"""
CONFIG_HEALTHY = "The configuration file is correctly formatted!"
CONFIG_NOT_HEALTHY = "The configuration file contains errors!"
MISSING_SECTIONS = """The following sections are missing or empty:
--------------------------------------------
{}
--------------------------------------------
"""
MALFORMED_ENTRIES = """The following sections contain entries that missing or malformed:
-----------------------------------------------------------------
{}
-----------------------------------------------------------------
"""

START_CONFIG = "START-CONFIG".center(50).replace(" ", "-")
END_CONFIG = "END-CONFIG".center(50).replace(" ", "-")

def create_argparser():
    """
    Returns:
        argparse.ArgumentParser: The argument parser for pdfebc.
    """
    config = utils.read_config()
    out_dir_default = utils.try_get_conf(config, utils.DEFAULT_SECTION_KEY,
                                         utils.OUT_DEFAULT_DIR_KEY)
    src_dir_default = utils.try_get_conf(config, utils.DEFAULT_SECTION_KEY,
                                         utils.SRC_DEFAULT_DIR_KEY)
    gs_default_binary = utils.try_get_conf(config, utils.DEFAULT_SECTION_KEY,
                                           utils.GS_DEFAULT_BINARY_KEY)
    parser = argparse.ArgumentParser(
        description=DESCRIPTION)
    parser.add_argument(
        SRC_DIR_SHORT, SRC_DIR_LONG, help=SRC_DIR_HELP, type=str, default=src_dir_default)
    parser.add_argument(
        OUT_DIR_SHORT, OUT_DIR_LONG, help=OUT_DIR_HELP, type=str, default=out_dir_default)
    parser.add_argument(
        GS_SHORT, GS_LONG, help=GS_HELP, type=str, default=gs_default_binary)
    parser.add_argument(
        SEND_SHORT, SEND_LONG, help=SEND_HELP, action='store_true')
    parser.add_argument(
        CLEAN_SHORT, CLEAN_LONG, help=CLEAN_HELP, action='store_true')
    parser.add_argument(
        STATUS_SHORT, STATUS_LONG, help=STATUS_HELP, action='store_true')
    return parser

def prompt_for_config_values():
    """Prompt the user for the user, password and receiver values for the config.

    Returns:
        str, str, str: user e-mail, user password and receiver e-mail (or whatever the user enters
        when prompted for these).
    """
    print("""The 'send' functionality requires an e-mail configuration file, and I can't find one!
    Please follow the instructions to create a configuration file. Please note that all of the
    information must be filled in, nothing can be left empty!\n""")
    user = input("Please enter the sender's e-mail address: ")
    password = input("Please enter the password for the sender's e-mail address: ")
    receiver = input("Please enter the receiver's email address: ")
    if not user or not password or not receiver:
        print("""One or more fields were left empty! I'm gonna crash now, re-run the program and
        try again. And be more careful this time.""")
        sys.exit(1)
    print("Everything looks spiffy, thank you!")
    return user, password, receiver

def status_callback(status):
    """Callback function for recieving status messages. This one simply prints the message to
    stdout.

    Args:
        status (str): A status message.
    """
    print(status + "\n")

def diagnose_config():
    """Print the results of the configuration diagnostics check."""
    if not os.path.isfile(utils.CONFIG_PATH):
        status_callback(NO_CONFIG_FOUND.format(utils.CONFIG_PATH))
        return
    config = utils.read_config()
    config_path, missing_sections, malformed_entries = utils.run_config_diagnostics()
    output = []
    if not missing_sections and not malformed_entries:
        output.append(CONFIG_STATUS.format(config_path, CONFIG_HEALTHY))
    else:
        output.append(CONFIG_STATUS.format(config_path, CONFIG_NOT_HEALTHY))
        if missing_sections:
            missing = MISSING_SECTIONS.format("\n".join(missing_sections))
            output.append(missing)
        if malformed_entries:
            malformed = []
            for section, options in malformed_entries.items():
                malformed.append("\n".join(["[{}]".format(section), *options]))
            output.append(MALFORMED_ENTRIES.format("\n".join(malformed)))
    config_string = utils.config_to_string(config)
    config_contents = CONFIG_CONTENTS.format(config_string, start=START_CONFIG, end=END_CONFIG)
    output.append(config_contents)
    status_callback("\n\n".join(output))
