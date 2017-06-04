# -*- coding: utf-8 -*-
"""Unit tests for the core module.

Author: Simon Larsén
"""
import unittest
import tempfile
import os
from unittest.mock import Mock, patch
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

class CoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trash_can = tempfile.TemporaryDirectory()
        cls.default_trash_file = os.path.join(cls.trash_can.name, 'default')
        cls.file_size_lower_limit = pdfebc.core.FILE_SIZE_LOWER_LIMIT

    @classmethod
    def setUp(cls):
        pdfebc.core.FILE_SIZE_LOWER_LIMIT = cls.file_size_lower_limit


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

    def test_compress_non_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            non_pdf_file = create_temporary_files_with_suffixes(tmpdir,
                                                                suffixes=OTHER_FILE_EXTENSIONS,
                                                                files_per_suffix=1).pop()
            non_pdf_filename = non_pdf_file.name
            with self.assertRaises(ValueError) as context:
                pdfebc.core.compress_pdf(non_pdf_filename,
                                         self.default_trash_file,
                                         pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT)

    def test_compress_pdf_that_does_not_exist(self):
        with tempfile.NamedTemporaryFile() as file:
            filename = file.name
        with self.assertRaises(ValueError) as context:
            pdfebc.core.compress_pdf(filename, self.default_trash_file, pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT)

    @patch('pdfebc.core.send_less_than_min_size_status_message')
    def test_compress_too_small_pdf(self, mock_less_than_min_size_status):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            mock_status_callback = Mock(return_value=None)
            pdf_file = create_temporary_files_with_suffixes(self.trash_can.name, files_per_suffix=1)[0]
            pdf_file.close()
            output_path = os.path.join(tmpoutdir, os.path.basename(pdf_file.name))
            pdfebc.core.compress_pdf(pdf_file.name, output_path,
                                     pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT, mock_status_callback)
            mock_less_than_min_size_status.assert_called_once()
            mock_status_callback.assert_called_once()

    @patch('subprocess.Popen', autospec=True)
    def test_compress_adequately_sized_pdf(self, mock_popen):
        # change the lower limit for file size, is reset in the setUp method
        pdfebc.core.FILE_SIZE_LOWER_LIMIT = 0
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpoutdir:
            mock_status_callback = Mock(return_value=None)
            pdf_file = create_temporary_files_with_suffixes(self.trash_can.name, files_per_suffix=1)[0]
            pdf_file.close()
            output_path = os.path.join(tmpoutdir, os.path.basename(pdf_file.name))
            pdfebc.core.compress_pdf(pdf_file.name, output_path,
                                     pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT, mock_status_callback)
            mock_popen.assert_called_once()
            mock_popen_instance = mock_popen([])
            mock_popen_instance.communicate.assert_called_once()
            mock_status_callback.assert_called()

    def test_send_compressing_status_message(self):
        source_path = "/home/simon/Documents/github/pdfebc/superpdf.pdf"
        expected_status_message = "Compressing '%s' ..." % source_path
        mock_status_callback = Mock(return_value=None)
        pdfebc.core.send_compressing_status_message(source_path, mock_status_callback)
        mock_status_callback.assert_called_once_with(expected_status_message)

    def test_send_file_done_status_message(self):
        output_path = "/home/simon/Documents/github/pdfebc/pdfebc_out/superpdf.pdf"
        expected_status_message = "File done! Result saved to '%s'" % output_path
        mock_status_callback = Mock(return_value=None)
        pdfebc.core.send_file_done_status_message(output_path, mock_status_callback)
        mock_status_callback.assert_called_once_with(expected_status_message)

    def test_send_less_than_min_size_status_message(self):
        source_path = "/home/simon/Documents/github/pdfebc/superpdf.pdf"
        file_size = 0.5*pdfebc.core.FILE_SIZE_LOWER_LIMIT
        expected_status_message = """Not compressing '%s'
Reason: Actual file size is %d bytes,
lower limit for compression is %d bytes""" % (
    source_path,
    file_size,
    pdfebc.core.FILE_SIZE_LOWER_LIMIT)
        mock_status_callback = Mock(return_value=None)
        pdfebc.core.send_less_than_min_size_status_message(source_path,
                                                           file_size,
                                                           mock_status_callback)
        mock_status_callback.assert_called_once_with(expected_status_message)


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

