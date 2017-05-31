# -*- coding: utf-8 -*-
"""Unit tests for the core module.

Author: Simon Larsén
"""
import unittest
import tempfile
import os
from .context import pdfebc

PDF_FILE_EXTENSION = ".pdf"

def create_temporary_files_with_suffix(directory, suffix=PDF_FILE_EXTENSION, amount=20):
    """Create an arbitrary amount of tempfile.NamedTemporaryFile files with a given suffix.
    Note that the files are NOT deleted automatically, so should be used in a tempfile.TemporaryDirectory
    context to avoid having to clean them up manually.

    Args:
        suffix (str): Suffix of the files to create.
        directory (str): Path to the directory to create the files in.
        amount (int): Amount of files to create.

    Returns:
        [tempfile.NamedTemporaryFile]: A list of tempfile.NamedTemporaryFile.
    """
    filepaths = [tempfile.NamedTemporaryFile(suffix=suffix, dir=directory, delete=False)
                 for i in range(amount)]
    return filepaths


class CoreTest(unittest.TestCase):
    def test_get_pdf_filenames_from_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assertFalse(filepaths)

    def test_get_pdf_filenames_from_dir_with_only_pdfs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temporary_files = create_temporary_files_with_suffix(tmpdir)
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assert_filepaths_match_temporary_file_names(filepaths, temporary_files)

    def assert_filepaths_match_temporary_file_names(self, filepaths, temporary_files):
        """Assert that a list of filepaths match a list of temporary files.

        Args:
            filepaths ([str]): A list of filepaths.
            temporary_files (tempfile.NamedTemporaryFile): A list of tempfile.NamedTemporaryFile.
        """
        self.assertEqual(len(temporary_files), len(filepaths))
        sorted_filepaths = sorted(filepaths)
        sorted_temporary_files = sorted(temporary_files, key=lambda tmpfile: tmpfile.name)
        for filepath, tmpfile in zip(sorted_filepaths, sorted_temporary_files):
            self.assertEqual(filepath, tmpfile.name)
