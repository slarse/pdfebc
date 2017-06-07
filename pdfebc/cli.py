# -*- coding: utf-8 -*-
"""This module contains the argument parser for the pdfebc program.

.. module:: cli
    :platform: Unix
    :synopsis: The pdfebc CLI.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import argparse
import sys

OUTPUT_DIR_DEFAULT = "pdfebc_out"
SOURCE_DIR_DEFAULT = "."
GHOSTSCRIPT_BINARY_DEFAULT = "gs"

DESCRIPTION = "Compresses all pdf files in the current directory"
OUTPUT_DIR_SHORT = "-o"
OUTPUT_DIR_LONG = "--outdir"
OUTPUT_DIR_HELP = "Output directory. If not specified, default is '{}'".format(OUTPUT_DIR_DEFAULT)
SOURCE_DIR_SHORT = "-src"
SOURCE_DIR_LONG = "--sourcedir"
SOURCE_DIR_HELP = "Source directory. Default is '{}'".format(SOURCE_DIR_DEFAULT)
NO_MAKEDIR_SHORT = "-nm"
NO_MAKEDIR_LONG = "--nomakedir"
NO_MAKEDIR_HELP = "Do not create the output directory."
GS_SHORT = "-gs"
GS_LONG = "--ghostscript"
GS_HELP = "Specify the name of the Ghostscript binary. Default is '{}'.".format(
    GHOSTSCRIPT_BINARY_DEFAULT)
SEND_SHORT = "-s"
SEND_LONG = "--send"
SEND_HELP = "Attempt to send the compressed PDF files with the settings in config.ini."
CLEAN_SHORT = "-c"
CLEAN_LONG = "--clean"
CLEAN_HELP = """Automatically remove output directory after finishing the program.
Most useful in conjuction with --send."""

def create_argparser():
    """
    Returns:
        argparse.ArgumentParser: The argument parser for pdfebc.
    """
    parser = argparse.ArgumentParser(
        description=DESCRIPTION
        )
    parser.add_argument(
        OUTPUT_DIR_SHORT, OUTPUT_DIR_LONG, help=OUTPUT_DIR_HELP, type=str,
        default=OUTPUT_DIR_DEFAULT
        )
    parser.add_argument(
        SOURCE_DIR_SHORT, SOURCE_DIR_LONG, help=SOURCE_DIR_HELP, type=str,
        default=SOURCE_DIR_DEFAULT
        )
    parser.add_argument(
        NO_MAKEDIR_SHORT, NO_MAKEDIR_LONG, help=NO_MAKEDIR_HELP,
        action="store_true"
        )
    parser.add_argument(
        GS_SHORT, GS_LONG, help=GS_HELP,
        type=str, default=GHOSTSCRIPT_BINARY_DEFAULT
        )
    parser.add_argument(
        SEND_SHORT, SEND_LONG, help=SEND_HELP,
        action="store_true"
        )
    parser.add_argument(
        CLEAN_SHORT, CLEAN_LONG, help=CLEAN_HELP,
        action='store_true'
        )
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
