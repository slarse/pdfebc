# -*- coding: utf-8 -*-
"""Unit tests for the utils module.

Author: Simon Larsén
"""
import unittest
from unittest.mock import patch
import tempfile
import configparser
import os
import email
from email.mime.multipart import MIMEMultipart
from .context import pdfebc

def create_configparser(section, user, password, reciever):
    """Create a ConfigParser for testing purposes.

    Args:
        section (str): The section name.
        user (str): User e-mail address.
        password (str): User password.
        reciever (str): Reciever e-mail address.

    Returns:
        configparser.ConfigParser: A ConfigParser.
    """
    config = configparser.ConfigParser()
    config[section] = {'user': user,
                       'pass': password,
                       'reciever': reciever}
    return config

class UtilsTest(unittest.TestCase):
    NUM_attachment_filenames = 10

    @classmethod
    def setUp(cls):
        cls.temp_config_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        cls.attachment_filenames = []
        for _ in range(cls.NUM_attachment_filenames):
            file = tempfile.NamedTemporaryFile(
                encoding='utf-8', suffix=pdfebc.core.PDF_EXTENSION, mode='w', delete=False)
            cls.attachment_filenames.append(file.name)
            file.close()


    @classmethod
    def tearDown(cls):
        cls.temp_config_file.close()
        os.unlink(cls.temp_config_file.name)
        for filename in cls.attachment_filenames:
            os.unlink(filename)

    def test_read_valid_email_config(self):
        expected_user, expected_password, expected_reciever = "test_user", "test_password", "test_reciever"
        config = create_configparser(pdfebc.utils.SECTION_KEY,
                                     expected_user,
                                     expected_password,
                                     expected_reciever)
        config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        actual_user, actual_password, actual_reciever = pdfebc.utils.read_email_config(self.temp_config_file.name)
        self.assertEqual(expected_user, actual_user)
        self.assertEqual(expected_password, actual_password)
        self.assertEqual(expected_reciever, actual_reciever)

    def test_read_empty_email_config(self):
        with self.assertRaises(ValueError) as context:
            pdfebc.utils.read_email_config(self.temp_config_file.name)

    def test_read_email_config_without_reciever(self):
        expected_user, expected_password = "test_user", "test_password"
        config = configparser.ConfigParser()
        config[pdfebc.utils.SECTION_KEY] = {'user': expected_user, 'pass': expected_password}
        config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        with self.assertRaises(ValueError) as context:
            pdfebc.utils.read_email_config(self.temp_config_file.name)

    def test_attach_valid_files(self):
        email_ = MIMEMultipart()
        pdfebc.utils.attach_files(self.attachment_filenames, email_)
        expected_filenames = list(self.attachment_filenames)
        part_dispositions = [part.get('Content-Disposition')
                             for part in email.message_from_bytes(email_.as_bytes()).walk()
                             if part.get_content_maintype() == 'application']
        print(part_dispositions)
        for filename_base in map(os.path.basename, self.attachment_filenames):
            self.assertTrue(
                any(map(lambda disp: filename_base in disp, part_dispositions)))

    @patch('smtplib.SMTP')
    def test_send_valid_email(self, mock_smtp):
        mock_smtp_instance = mock_smtp()
        user, password, reciever = "test_user", "test_password", "test_reciever"
        subject = "Test e-mail"
        email_ = MIMEMultipart()
        email_['From'] = user
        email_['To'] = reciever
        email_['Subject'] = subject
        pdfebc.utils.send_email(user, password, email_)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(user, password)
        mock_smtp_instance.send_message.assert_called_once_with(email_)
        mock_smtp_instance.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_valid_email_preconf(self, mock_smtp):
        mock_smtp_instance = mock_smtp()
        user, password, reciever = "test_user", "test_password", "test_reciever"
        subject = "Test e-mail"
        message = "Test e-mail body"
        pdfebc.utils.send_with_attachments(user, password, reciever, subject, message, self.attachment_filenames)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(user, password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
