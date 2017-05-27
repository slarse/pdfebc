"""This module contains the argument parser for the pdfebc program.

.. module:: cli
    :platform: Unix
    :synopsis: The pdfebc CLI.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import argparse

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
        "-o", "--outdir", help=f"Output directory. If not specified, default is '{OUTPUT_DIR_DEFAULT}'", type=str,
        default=OUTPUT_DIR_DEFAULT
        )
    parser.add_argument(
        "-src", "--sourcedir", help=f"Source directory. Default is '{SOURCE_DIR_DEFAULT}'", type=str,
        default=SOURCE_DIR_DEFAULT
        )
    parser.add_argument(
        "-nm", "--nomakedir", help="Do not create the output directory.",
        action="store_true"
        )
    parser.add_argument(
        "-gs", "--ghostscript", help=f"Specify the name of the Ghostscript binary. Default is '{GHOSTSCRIPT_BINARY_DEFAULT}'.",
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
