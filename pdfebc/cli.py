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

def create_argparser():
    """
    Returns:
        argparse.ArgumentParser: The argument parser for pdfebc.
    """
    parser = argparse.ArgumentParser(
        description="Compresses all pdf files in the current directory"
        )
    parser.add_argument(
        "-o", "--outdir", help="Output directory. If not specified, default is '%s'" % OUTPUT_DIR_DEFAULT, type=str,
        default=OUTPUT_DIR_DEFAULT
        )
    parser.add_argument(
        "-src", "--sourcedir", help="Source directory. Default is '%s'" % SOURCE_DIR_DEFAULT, type=str,
        default=SOURCE_DIR_DEFAULT
        )
    parser.add_argument(
        "-nm", "--nomakedir", help="Do not create the output directory.",
        action="store_true"
        )
    parser.add_argument(
        "-gs", "--ghostscript", help="Specify the name of the Ghostscript binary. Default is '%s'." % GHOSTSCRIPT_BINARY_DEFAULT,
        type=str, default=GHOSTSCRIPT_BINARY_DEFAULT
        )
    parser.add_argument(
        "-s", "--send", help="Attempt to send the compressed PDF files with the settings in config.ini.",
        action="store_true"
        )
    parser.add_argument(
        '-c', '--clean', help="""Automatically remove output directory after finishing the program.
                                 Most useful in conjuction with --send.""",
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
