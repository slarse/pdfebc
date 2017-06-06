# -*- coding: utf-8 -*-
"""This module contains the core functions of the pdfebc program. These consist mostly
of functions that manipulate PDF files and the file system.

.. module:: core
    :platform: Unix
    :synopsis: Core functions for pdfebc.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import sys
import subprocess
from . import utils

BYTES_PER_MEGABYTE = 1024**2
FILE_SIZE_LOWER_LIMIT = BYTES_PER_MEGABYTE
PDF_EXTENSION = ".pdf"

COMPRESSING_MULTIPLE = """Source directory: '{}'
Output directory: '{}'
Found '{}' PDF files. Starting compression ..."""
ALL_FILES_DONE = """All files done!
Results saved to '{}'"""
COMPRESSING = "Compressing '{}' ..."
FILE_DONE = "File done! Result saved to '{}'"
NOT_COMPRESSING = """Not compressing '{}'
Reason: Actual file size is {} bytes,
lower limit for compression is {} bytes"""
GS_NOT_INSTALLED = """Ghostscript not installed or not aliased to '{}'.
Exiting ..."""

def get_pdf_filenames_at(source_directory):
    """Find all PDF files in the specified directory.

    Args:
        source_directory (str): The source directory.

    Returns:
        list(str): Filepaths to all PDF files in the specified directory.

    Raises:
        ValueError
    """
    if not os.path.isdir(source_directory):
        raise ValueError("%s is not a directory!" % source_directory)
    return [os.path.join(source_directory, filename)
            for filename in os.listdir(source_directory)
            if filename.endswith(PDF_EXTENSION)]

def compress_pdf(filepath, output_path, ghostscript_binary, status_callback=None):
    """Compress a single PDF file.

    Args:
        filepath (str): Path to the PDF file.
        output_path (str): Output path.
        ghostscript_binary (str): Name/alias of the Ghostscript binary.
        status_callback (function): A callback function for passing status messages to a view.

    Raises:
        ValueError
    """
    if not filepath.endswith(PDF_EXTENSION):
        raise ValueError("Filename must end with .pdf!\n%s does not." % filepath)
    try:
        file_size = os.stat(filepath).st_size
        if file_size < FILE_SIZE_LOWER_LIMIT:
            utils.if_callable_call_with_formatted_string(status_callback, NOT_COMPRESSING,
                                                         filepath, file_size, FILE_SIZE_LOWER_LIMIT)
            process = subprocess.Popen(['cp', filepath, output_path])
        else:
            utils.if_callable_call_with_formatted_string(status_callback, COMPRESSING, filepath)
            process = subprocess.Popen(
                [ghostscript_binary, "-sDEVICE=pdfwrite",
                 "-dCompatabilityLevel=1.4", "-dPDFSETTINGS=/ebook",
                 "-dNOPAUSE", "-dQUIET", "-dBATCH",
                 "-sOutputFile=%s" % output_path, filepath]
                )
    except FileNotFoundError:
        utils.if_callable_call_with_formatted_string(status_callback, GS_NOT_INSTALLED,
                                                     ghostscript_binary)
        sys.exit(1)
    process.communicate()
    utils.if_callable_call_with_formatted_string(status_callback, FILE_DONE, output_path)

def compress_multiple_pdfs(source_directory, output_directory, ghostscript_binary, status_callback=None):
    """Compress all PDF files in the current directory and place the output in the given output directory.

    Args:
        source_directory (str): Filepath to the source directory.
        output_directory (str): Filepath to the output directory.
        ghostscript_binary (str): Name of the Ghostscript binary.
        status_callback (function): A callback function for passing status messages to a view.

    Returns:
        list(str): paths to outputs.
    """
    source_paths = get_pdf_filenames_at(source_directory)
    out_paths = list()
    utils.if_callable_call_with_formatted_string(status_callback, COMPRESSING_MULTIPLE,
                                                 source_directory, output_directory, len(source_paths))
    for source_path in source_paths:
        output = os.path.join(output_directory, os.path.basename(source_path))
        out_paths.append(output)
        compress_pdf(source_path, output, ghostscript_binary, status_callback)
    utils.if_callable_call_with_formatted_string(status_callback, ALL_FILES_DONE, output_directory)
    return out_paths
