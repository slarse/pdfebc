# -*- coding: utf-8 -*-
"""Unit tests for the utils module.

Author: Simon Larsén
"""
import unittest
from unittest.mock import patch, create_autospec, Mock
import tempfile
import configparser
import os
import email
from email.mime.multipart import MIMEMultipart
from .context import pdfebc

class UtilsTest(unittest.TestCase):
    NUM_ATTACHMENT_FILENAMES = 10

    @classmethod
    def setUpClass(cls):
        cls.expected_user = "test_user"
        cls.expected_password = "test_password"
        cls.expected_reciever = "test_reciever"

    @classmethod
    def setUp(cls):
        cls.temp_config_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        cls.attachment_filenames = []
        for _ in range(cls.NUM_ATTACHMENT_FILENAMES):
            file = tempfile.NamedTemporaryFile(
                encoding='utf-8', suffix=pdfebc.core.PDF_EXTENSION, mode='w', delete=False)
            cls.attachment_filenames.append(file.name)
            file.close()
        cls.valid_config = pdfebc.utils.create_email_config(cls.expected_user,
                                                            cls.expected_password,
                                                            cls.expected_reciever)
        cls.invalid_config = configparser.ConfigParser()
        cls.invalid_config[pdfebc.utils.SECTION_KEY] = {pdfebc.utils.USER_KEY: cls.expected_user,
                                                        pdfebc.utils.PASSWORD_KEY: cls.expected_password}

    @classmethod
    def tearDown(cls):
        cls.temp_config_file.close()
        os.unlink(cls.temp_config_file.name)
        for filename in cls.attachment_filenames:
            os.unlink(filename)

    def test_write_valid_email_config(self):
        self.temp_config_file.close()
        pdfebc.utils.write_config(self.valid_config, self.temp_config_file.name)
        config = configparser.ConfigParser()
        with open(self.temp_config_file.name) as file:
            config.read_file(file)
        section = config[pdfebc.utils.SECTION_KEY]
        self.assertEqual(self.expected_user, section[pdfebc.utils.USER_KEY])
        self.assertEqual(self.expected_password, section[pdfebc.utils.PASSWORD_KEY])
        self.assertEqual(self.expected_reciever, section[pdfebc.utils.RECIEVER_KEY])

    def test_read_valid_email_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        actual_user, actual_password, actual_reciever = pdfebc.utils.read_email_config(self.temp_config_file.name)
        self.assertEqual(self.expected_user, actual_user)
        self.assertEqual(self.expected_password, actual_password)
        self.assertEqual(self.expected_reciever, actual_reciever)

    def test_read_empty_email_config(self):
        with self.assertRaises(configparser.ParsingError) as context:
            pdfebc.utils.read_email_config(self.temp_config_file.name)

    def test_read_email_config_no_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            config_path = tmp.name
        with self.assertRaises(IOError) as context:
            pdfebc.utils.read_email_config(config_path)

    def test_read_email_config_without_reciever(self):
        self.invalid_config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        with self.assertRaises(configparser.ParsingError) as context:
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

    def test_create_email_config(self):
        section_key = pdfebc.utils.SECTION_KEY
        user_key = pdfebc.utils.USER_KEY
        password_key = pdfebc.utils.PASSWORD_KEY
        reciever_key = pdfebc.utils.RECIEVER_KEY
        actual_user = self.valid_config[section_key][user_key]
        actual_password = self.valid_config[section_key][password_key]
        actual_reciever = self.valid_config[section_key][reciever_key]
        self.assertEqual(self.expected_user, actual_user)
        self.assertEqual(self.expected_password, actual_password)
        self.assertEqual(self.expected_reciever, actual_reciever)

    def test_valid_config_exists_no_config(self):
        with tempfile.NamedTemporaryFile() as file:
            config_path = file.name
        self.assertFalse(pdfebc.utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_valid_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path = self.temp_config_file.name
        self.assertTrue(pdfebc.utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_config_without_reciever(self):
        self.invalid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path = self.temp_config_file.name
        self.assertFalse(pdfebc.utils.valid_config_exists(config_path))

    def test_if_callable_call_with_formatted_string_too_few_args(self):
        three_args_formattable_string = "test {} test {} test {}"
        mock_callback = Mock(return_value=None)
        args = ("test", "test")
        with self.assertRaises(ValueError) as context:
            pdfebc.utils.if_callable_call_with_formatted_string(
                mock_callback,
                three_args_formattable_string,
                *args)

    def test_if_callable_call_with_formatted_string_valid_args(self):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test", "test")
        mock_callback = Mock(return_vale=None)
        pdfebc.utils.if_callable_call_with_formatted_string(
                mock_callback,
                three_args_formattable_string,
                *args)
        mock_callback.assert_called_once_with(
            three_args_formattable_string.format(*args))

    @patch('pdfebc.utils.callable', return_value=False)
    def test_if_callable_call_with_formatted_string_not_callable_too_few_args(self, mock_callable):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test")
        mock_callback = Mock(return_value=None)
        with self.assertRaises(ValueError) as context:
            pdfebc.utils.if_callable_call_with_formatted_string(
                mock_callback,
                three_args_formattable_string,
                *args)

    @patch('pdfebc.utils.callable', return_value=False)
    def test_if_callable_call_with_formatted_string_not_callable_valid_args(self, mock_callable):
        three_args_formattable_string = "test {} test {} test {}"
        args = ("test", "test", "test")
        mock_callback = Mock(return_value=None)
        pdfebc.utils.if_callable_call_with_formatted_string(
            mock_callback,
            three_args_formattable_string,
            *args)
        self.assertFalse(mock_callback.called)

