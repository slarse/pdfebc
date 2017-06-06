# -*- coding: utf-8 -*-
"""Module containing util functions for the pdfebc program.

It uses Google's SMTP server for sending emails. If you wish to use another server, simply change
the SMTP_SERVER variable to your preferred server.

Requires a config file called 'email.cnf' in the user conf directory specified by appdirs. In the
case of Arch Linux, this is '$HOME/.config/pdfebc/email.cnf', but this may vary with distributions.
The config file should have the following format:

    |[email]
    |user = sender_email
    |pass = password
    |receiver = receiver_email

All characters after the colon and whitespace (as much whitespace as you'd like) until
EOL counts as the username/password.

.. module:: utils
    :platform: Unix
    :synopsis: Core functions for pdfebc.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import smtplib
import os
import configparser
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import appdirs

CONFIG_PATH = os.path.join(appdirs.user_config_dir('pdfebc'), 'email.cnf')
SECTION_KEY = "email"
PASSWORD_KEY = "pass"
USER_KEY = "user"
RECIEVER_KEY = "receiver"
SMTP_SERVER = "smtp.gmail.com"

SENDING_PRECONF = """Sending files ...
From: {}
To: {}
SMTP Server: {}
Files:
{}"""
FILES_SENT = "Files successfully sent!"""

def create_email_config(user, password, receiver):
    """Create an email config.

    Args:
        user (str): User e-mail address.
        password (str): Password to user e-mail address.
        receiver: Reciever e-mail address.

    Returns:
        configparser.ConfigParser: A ConfigParser
    """
    config = configparser.ConfigParser()
    config[SECTION_KEY] = {
        USER_KEY: user,
        PASSWORD_KEY: password,
        RECIEVER_KEY: receiver}
    return config

def write_config(config, config_path=CONFIG_PATH):
    """Write the config to the output path.
    Creates the necessary directories if they aren't there.

    Args:
        config (configparser.ConfigParser): A ConfigParser.
    """
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path))
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)

def read_email_config(config_path=CONFIG_PATH):
    """Read the email config file.

    Args:
        config_path (str): Relative path to the email config file.

    Returns:
        (str, str, str): User email, user password and receiver email.

    Raises:
        IOError
    """
    if not os.path.isfile(config_path):
        raise IOError("No config file found at %s" % config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    user = try_get_conf(config, SECTION_KEY, USER_KEY)
    password = try_get_conf(config, SECTION_KEY, PASSWORD_KEY)
    receiver = try_get_conf(config, SECTION_KEY, RECIEVER_KEY)
    return user, password, receiver

def try_get_conf(config, section, attribute):
    """Try to parse an attribute of the config file.

    Args:
        config (configparser.ConfigParser): A ConfigParser.
        section (str): The section of the config file to get information from.
        attribute (str): The attribute of the section to fetch.

    Returns:
        str: The string corresponding to the section and attribute.

    Raises:
        configparser.ParseError
    """
    try:
        return config[section][attribute]
    except KeyError:
        raise configparser.ParsingError("""Config file badly formed!\n
                Failed to get attribute '%s' from section '%s'!""" % (attribute, section))

def send_with_attachments(user, password, receiver, subject, message, filepaths):
    """Send an email from the user (a gmail) to the receiver.

    Args:
        user (str): The sender's email address.
        password (str): The password to the 'user' address.
        receiver (str): The receiver's email address.
        subject (str): Subject of the email.
        message (str): A message.
        filepaths (list(str)): Filepaths to files to be attached.
    """
    email_ = MIMEMultipart()
    email_.attach(MIMEText(message))
    email_["Subject"] = subject
    email_["From"] = user
    email_["To"] = receiver
    attach_files(filepaths, email_)
    send_email(user, password, email_)


def attach_files(filepaths, email_):
    """Take a list of filepaths and attach the files to a MIMEMultipart.

    Args:
        filepaths (list(str)): A list of filepaths.
        email_ (email.MIMEMultipart): A MIMEMultipart email_.
    """
    for filepath in filepaths:
        base = os.path.basename(filepath)
        with open(filepath, "rb") as file:
            part = MIMEApplication(file.read(), Name=base)
            part["Content-Disposition"] = 'attachment; filename="%s"' % base
            email_.attach(part)

def send_email(user, password, email_):
    """Send an email.

    Args:
        user (str): Sender's email address.
        password (str): Password to sender's email.
        email_ (email.MIMEMultipart): The email to send.
    """
    server = smtplib.SMTP(SMTP_SERVER, 587)
    server.starttls()
    server.login(user, password)
    server.send_message(email_)
    server.quit()

def send_files_preconf(filepaths, config_path=CONFIG_PATH, status_callback=None):
    """Send files using the config.ini settings.

    Args:
        filepaths (list(str)): A list of filepaths.
    """
    user, password, receiver = read_email_config(config_path)
    subject = "PDF files from pdfebc"
    message = ""
    args = (user, receiver, SMTP_SERVER, '\n'.join(filepaths))
    if_callable_call_with_formatted_string(status_callback, SENDING_PRECONF, *args)
    send_with_attachments(user, password, receiver, subject, message, filepaths)
    if_callable_call_with_formatted_string(status_callback, FILES_SENT)

def valid_config_exists(config_path=CONFIG_PATH):
    """Verify that a valid config file exists.

    Args:
        config_path (str): Path to the config file.

    Returns:
        boolean: True if there is a valid config file, false if not.
    """
    if (os.path.isfile(config_path)):
        try:
            read_email_config(config_path)
        except configparser.ParsingError:
            return False
    else:
        return False
    return True

def if_callable_call_with_formatted_string(callback, formattable_string, *args):
    """If the callback is callable, format the string with the args and make a call.
    Otherwise, do nothing.

    Args:
        callback (function): May or may not be callable.
        formattable_string (str): A string with '{}'s inserted.
        *args: A variable amount of arguments for the string formatting. Must correspond to the
        amount of '{}'s in 'formattable_string'.
    Raises:
        ValueError
    """
    try:
        formatted_string = formattable_string.format(*args)
    except IndexError:
        raise ValueError("Mismatch metween amount of insertion points in the formattable string\n"
                         "and the amount of args given.")
    if callable(callback):
        callback(formatted_string)
