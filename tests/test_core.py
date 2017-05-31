# -*- coding: utf-8 -*-
"""Unit tests for the core module.

Author: Simon Larsén
"""
import unittest
import tempfile
import os
from .context import pdfebc

PDF_FILE_EXTENSION = '.pdf'
OTHER_FILE_EXTENSIONS = ['.png', '.bmp', '.txt', '.sh', '.py']

def create_temporary_files_with_suffixes(directory, suffixes=[PDF_FILE_EXTENSION], files_per_suffix=20):
    """Create an arbitrary amount of tempfile.NamedTemporaryFile files with given suffixes.
    Note that the files are NOT deleted automatically, so should be used in a tempfile.TemporaryDirectory
    context to avoid having to clean them up manually.

    Args:
        directory (str): Path to the directory to create the files in.
        suffixes ([str]): List of suffixes of the files to create.
        files_per_suffix (int): Amount of files to create per suffix.

    Returns:
        [tempfile.NamedTemporaryFile]: A list of tempfile.NamedTemporaryFile.
    """
    filepaths = [tempfile.NamedTemporaryFile(suffix=suffix, dir=directory, delete=False)
                 for i in range(files_per_suffix) for suffix in suffixes]
    return filepaths

def create_tempo(directory, suffixes=OTHER_FILE_EXTENSIONS, amount=20):
    """Create an arbitrary amount of tempfile.NamedTemporaryFile files with file exte"""


class CoreTest(unittest.TestCase):
    def test_get_pdf_filenames_from_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assertFalse(filepaths)

    def test_get_pdf_filenames_from_dir_with_only_pdfs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = create_temporary_files_with_suffixes(tmpdir)
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assert_filepaths_match_file_names(filepaths, files)

    def test_get_pdf_filenames_from_dir_with_only_other_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = create_temporary_files_with_suffixes(tmpdir, suffixes=OTHER_FILE_EXTENSIONS)
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assertFalse(filepaths)

    def test_get_pdf_filenames_from_dir_that_does_not_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # TemporaryDirectory is deleted upon exiting with-context
            path_to_dir = tmpdir
        with self.assertRaises(ValueError) as context:
            pdfebc.core.get_pdf_filenames_at(path_to_dir)

    def test_get_pdf_filenames_from_dir_with_mixed_file_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            amount_of_pdfs = 10
            pdf_files = create_temporary_files_with_suffixes(tmpdir, files_per_suffix=amount_of_pdfs)
            non_pdf_files = create_temporary_files_with_suffixes(tmpdir, suffixes=OTHER_FILE_EXTENSIONS)
            filepaths = pdfebc.core.get_pdf_filenames_at(tmpdir)
            self.assert_filepaths_match_file_names(filepaths, pdf_files)

    def assert_filepaths_match_file_names(self, filepaths, temporary_files):
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
