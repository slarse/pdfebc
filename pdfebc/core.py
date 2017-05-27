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

BYTES_PER_MEGABYTE = 1024**2
FILE_SIZE_LOWER_LIMIT = BYTES_PER_MEGABYTE
PDF_EXTENSION = ".pdf"

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
        raise ValueError(f"{source_directory} is not a directory!")
    return [os.path.join(source_directory, filename)
            for filename in os.listdir(source_directory)
            if filename.endswith(PDF_EXTENSION)]

def compress_pdf(filepath, output_path, ghostscript_binary):
    """Compress a single PDF file.

    Args:
        filepath (str): Path to the PDF file.
        output_path (str): Output path.
        ghostscript_binary (str): Name/alias of the Ghostscript binary.

    Returns:
        (str, str): stdout and stderr from the Ghostrscript process.

    Raises:
        ValueError
    """
    if not filepath.endswith(PDF_EXTENSION):
        raise ValueError("Filename must end with .pdf!\n%s does not." % filepath)
    try:
        file_size = os.stat(filepath).st_size
        if file_size < FILE_SIZE_LOWER_LIMIT:
            process = subprocess.Popen(['cp', f'{filepath}', f'{output_path}'])
        else:
            process = subprocess.Popen(
                [f"{ghostscript_binary}", "-sDEVICE=pdfwrite",
                 "-dCompatabilityLevel=1.4", "-dPDFSETTINGS=/ebook",
                 "-dNOPAUSE", "-dQUIET", "-dBATCH",
                 f"-sOutputFile={output_path}", filepath]
                )
    except FileNotFoundError:
        print(f"\nGhostscript not installed or not aliased to {ghostscript_binary}\n")
        sys.exit(1)
    return process.communicate()

def compress_multiple_pdfs(source_directory, output_directory, ghostscript_binary):
    """Compress all PDF files in the current directory and place the output in the given output directory.

    Args:
        source_directory (str): Filepath to the source directory.
        output_directory (str): Filepath to the output directory.
        ghostscript_binary (str): Name of the Ghostscript binary.

    Returns:
        list(str): paths to outputs.

    Raises:
        ValueError
    """
    source_paths = get_pdf_filenames_at(source_directory)
    out_paths = list()
    for source_path in source_paths:
        output = os.path.join(output_directory, os.path.basename(source_path))
        out_paths.append(output)
        out, err = compress_pdf(source_path, output, ghostscript_binary)
        handle_output(out)
        handle_errors(err)
    return out_paths

def handle_output(out):
    """Handle output from call to Ghostscript

    .. warning:: Not implemented!

    Args:
        out (str): stdout from Ghostscript.
    """
    #TODO Implement
    return

def handle_errors(err):
    """Handle output from call to Ghostscript

    .. warning:: Not implemented!

    Args:
        err (str): stderr from Ghostscript.
    """
    #TODO Implement
    return
