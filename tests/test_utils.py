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
        cls.user = 'test_user'
        cls.password = 'test_password'
        cls.receiver = 'test_receiver'
        cls.smtp_server = 'test_server'
        cls.smtp_port = 999
        cls.user_key = pdfebc.utils.USER_KEY
        cls.password_key = pdfebc.utils.PASSWORD_KEY
        cls.receiver_key = pdfebc.utils.RECEIVER_KEY
        cls.smtp_server_key = pdfebc.utils.SMTP_SERVER_KEY
        cls.smtp_port_key = pdfebc.utils.SMTP_PORT_KEY
        cls.gs_binary_default_key = pdfebc.utils.GS_DEFAULT_BINARY_KEY
        cls.out_dir_default_key = pdfebc.utils.OUT_DEFAULT_DIR_KEY
        cls.src_dir_default_key = pdfebc.utils.SRC_DEFAULT_DIR_KEY
        cls.email_section_key = pdfebc.utils.EMAIL_SECTION_KEY
        cls.default_section_key = pdfebc.utils.DEFAULT_SECTION_KEY
        cls.email_section_keys = {cls.user_key, cls.password_key, cls.receiver_key,
                                  cls.smtp_server_key, cls.smtp_port_key}
        cls.default_section_keys = {cls.gs_binary_default_key, cls.src_dir_default_key, cls.out_dir_default_key}
        cls.section_keys = {cls.email_section_key: cls.email_section_keys,
                            cls.default_section_key: cls.default_section_keys}


    @classmethod
    def setUp(cls):
        cls.temp_config_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        cls.attachment_filenames = []
        for _ in range(cls.NUM_ATTACHMENT_FILENAMES):
            file = tempfile.NamedTemporaryFile(
                encoding='utf-8', suffix=pdfebc.core.PDF_EXTENSION, mode='w', delete=False)
            cls.attachment_filenames.append(file.name)
            file.close()
        cls.valid_config = configparser.ConfigParser()
        cls.valid_config[pdfebc.utils.EMAIL_SECTION_KEY] = ({
            cls.user_key: cls.user,
            cls.password_key: cls.password,
            cls.receiver_key: cls.receiver,
            cls.smtp_server_key: cls.smtp_server,
            cls.smtp_port_key: cls.smtp_port})
        cls.valid_config[pdfebc.utils.DEFAULT_SECTION_KEY] = {
            cls.gs_binary_default_key: pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT,
            cls.src_dir_default_key: pdfebc.cli.SRC_DIR_DEFAULT,
            cls.out_dir_default_key: pdfebc.cli.OUT_DIR_DEFAULT}
        cls.invalid_config = configparser.ConfigParser()
        cls.invalid_config[pdfebc.utils.EMAIL_SECTION_KEY] = {
            cls.user_key: cls.user,
            cls.password_key: cls.password}

    @classmethod
    def tearDown(cls):
        cls.temp_config_file.close()
        os.unlink(cls.temp_config_file.name)
        for filename in cls.attachment_filenames:
            os.unlink(filename)

    def test_create_config(self):
        sections = self.section_keys.keys()
        section_contents = [{
            self.user_key: self.user,
            self.password_key: self.password,
            self.receiver_key: self.receiver,
            self.smtp_server_key: pdfebc.utils.DEFAULT_SMTP_SERVER,
            self.smtp_port_key: str(pdfebc.utils.DEFAULT_SMTP_PORT)},
           {self.gs_binary_default_key: pdfebc.cli.GHOSTSCRIPT_BINARY_DEFAULT,
            self.src_dir_default_key: pdfebc.cli.SRC_DIR_DEFAULT,
            self.out_dir_default_key: pdfebc.cli.OUT_DIR_DEFAULT}]
        config = pdfebc.utils.create_config(sections, section_contents)
        for section, section_content in zip(sections, section_contents):
            config_section = config[section]
            for section_content_key, section_content_value in section_content.items():
                self.assertEqual(section_content_value, config_section[section_content_key])

    def test_create_config_too_few_sections(self):
        sections = ["EMAIL"]
        section_contents = [{1: 2, 3: 4}, {1: 2}]
        with self.assertRaises(ValueError):
            pdfebc.utils.create_config(sections, section_contents)

    def test_write_valid_email_config(self):
        self.temp_config_file.close()
        pdfebc.utils.write_config(self.valid_config, self.temp_config_file.name)
        config = configparser.ConfigParser()
        with open(self.temp_config_file.name) as file:
            config.read_file(file)
        section = config[pdfebc.utils.EMAIL_SECTION_KEY]
        self.assertEqual(self.user, section[self.user_key])
        self.assertEqual(self.password, section[self.password_key])
        self.assertEqual(self.receiver, section[self.receiver_key])

    def test_read_valid_email_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.flush()
        self.temp_config_file.close()
        email_section = pdfebc.utils.read_config(self.temp_config_file.name)[
            pdfebc.utils.EMAIL_SECTION_KEY]
        actual_user = email_section[self.user_key]
        actual_password = email_section[self.password_key]
        actual_receiver = email_section[self.receiver_key]
        actual_smtp_server = email_section[self.smtp_server_key]
        actual_smtp_port = int(email_section[self.smtp_port_key])
        self.assertEqual(self.user, actual_user)
        self.assertEqual(self.password, actual_password)
        self.assertEqual(self.receiver, actual_receiver)
        self.assertEqual(self.smtp_server, actual_smtp_server)
        self.assertEqual(self.smtp_port, actual_smtp_port)

    def test_read_config_no_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            config_path = tmp.name
        with self.assertRaises(IOError) as context:
            pdfebc.utils.read_config(config_path)

    def test_attach_valid_files(self):
        email_ = MIMEMultipart()
        pdfebc.utils.attach_files(self.attachment_filenames, email_)
        expected_filenames = list(self.attachment_filenames)
        part_dispositions = [part.get('Content-Disposition')
                             for part in email.message_from_bytes(email_.as_bytes()).walk()
                             if part.get_content_maintype() == 'application']
        for filename_base in map(os.path.basename, self.attachment_filenames):
            self.assertTrue(
                any(map(lambda disp: filename_base in disp, part_dispositions)))

    @patch('smtplib.SMTP')
    def test_send_valid_email(self, mock_smtp):
        subject = "Test e-mail"
        email_ = MIMEMultipart()
        email_['From'] = self.user
        email_['To'] = self.receiver
        email_['Subject'] = subject
        pdfebc.utils.send_email(email_, self.valid_config._sections)
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_smtp_instance = mock_smtp()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once_with(email_)
        mock_smtp_instance.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_valid_email_with_attachments(self, mock_smtp):
        subject = "Test e-mail"
        message = "Test e-mail body"
        pdfebc.utils.send_with_attachments(subject, message, self.attachment_filenames,
                                           self.valid_config._sections)
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_smtp_instance = mock_smtp()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

    def test_create_email_config(self):
        section_key = pdfebc.utils.EMAIL_SECTION_KEY
        user_key = self.user_key
        password_key = self.password_key
        receiver_key = self.receiver_key
        actual_user = self.valid_config[section_key][user_key]
        actual_password = self.valid_config[section_key][password_key]
        actual_receiver = self.valid_config[section_key][receiver_key]
        self.assertEqual(self.user, actual_user)
        self.assertEqual(self.password, actual_password)
        self.assertEqual(self.receiver, actual_receiver)

    def test_valid_config_exists_no_config(self):
        with tempfile.NamedTemporaryFile() as file:
            config_path = file.name
        self.assertFalse(pdfebc.utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_valid_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path = self.temp_config_file.name
        self.assertTrue(pdfebc.utils.valid_config_exists(config_path))

    def test_valid_config_exists_with_invalid_config(self):
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

    @patch('smtplib.SMTP')
    def test_send_files_preconf_valid_files(self, mock_smtp):
        mock_smtp_instance = mock_smtp()
        mock_status_callback = Mock(return_value=None)
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        pdfebc.utils.send_files_preconf(self.attachment_filenames, config_path=self.temp_config_file.name,
                                        status_callback=mock_status_callback)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.user, self.password)
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
        expected_send_message = pdfebc.utils.SENDING_PRECONF.format(
            self.user, self.receiver,
            self.smtp_server, self.smtp_port, '\n'.join(self.attachment_filenames))
        expected_sent_message = pdfebc.utils.FILES_SENT
        mock_status_callback.assert_any_call(expected_send_message)
        mock_status_callback.assert_any_call(expected_sent_message)

    def test_run_config_diagnostics_valid_config(self):
        self.valid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path, missing_sections, malformed_entries = pdfebc.utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertFalse(missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_empty_config(self):
        config = configparser.ConfigParser()
        config.write(self.temp_config_file)
        config_path, missing_sections, malformed_entries = pdfebc.utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertEqual(self.section_keys.keys(), missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_empty_sections(self):
        config = configparser.ConfigParser()
        for section in self.section_keys.keys():
            config[section] = {}
        config.write(self.temp_config_file)
        config_path, missing_sections, malformed_entries = pdfebc.utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        self.assertEqual(self.section_keys.keys(), missing_sections)
        self.assertFalse(malformed_entries)

    def test_run_config_diagnostics_missing_section_and_options(self):
        self.invalid_config.write(self.temp_config_file)
        self.temp_config_file.close()
        config_path, missing_sections, malformed_entries = pdfebc.utils.run_config_diagnostics(
            self.temp_config_file.name)
        self.assertEqual(self.temp_config_file.name, config_path)
        expected_missing_email_options = self.email_section_keys - {self.user_key, self.password_key}
        self.assertEqual({self.default_section_key}, missing_sections)
        self.assertEqual(expected_missing_email_options, malformed_entries[self.email_section_key])

    def test_confg_to_string(self):
        gs_binary_default = "gs"
        section_string = "[{}]"
        option_string = "{} = {}"
        config = {self.default_section_key: {self.gs_binary_default_key: gs_binary_default},
                 self.email_section_key: {self.user_key: self.user, self.password_key: self.password}}
        expected_output = "\n".join([section_string.format(self.default_section_key),
                           option_string.format(self.gs_binary_default_key, gs_binary_default),
                           section_string.format(self.email_section_key),
                           option_string.format(self.user_key, self.user),
                           option_string.format(self.password_key, self.password)])
        print(expected_output)
        actual_output = pdfebc.utils.config_to_string(config)
        self.assertEqual(expected_output, actual_output)
