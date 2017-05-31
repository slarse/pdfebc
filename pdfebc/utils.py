# -*- coding: utf-8 -*-
"""Module containing util functions for the pdfebc program.

It uses Google's SMTP server for sending emails. If you wish to use another server, simply change
the SMTP_SERVER variable to your preferred server.

Requires a config file in $HOME/.config/pdfebc/config.ini that should look like:
    [email]
    user = sender_email
    pass = password
    reciever = reciever_email

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
import subprocess

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

CONFIG_RELATIVE_PATH = ".config/pdfebc/config.ini"
SECTION_KEY = "email"
PASSWORD_KEY = "pass"
USER_KEY = "user"
RECIEVER_KEY = "reciever"
SMTP_SERVER = "smtp.gmail.com"

def read_email_config(config_relative_path=CONFIG_RELATIVE_PATH):
    """Read the email config file.

    Args:
        config_relative_path (str): Relative path to the email config file.

    Returns:
        (str, str, str): User email, user password and reciever email.
    """
    home = os.path.expanduser("~")
    config_path = os.path.join(home, config_relative_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    user = try_get_conf(config, SECTION_KEY, USER_KEY)
    password = try_get_conf(config, SECTION_KEY, PASSWORD_KEY)
    reciever = try_get_conf(config, SECTION_KEY, RECIEVER_KEY)
    return user, password, reciever

def try_get_conf(config, section, attribute):
    """Try to parse an attribute of the config file.

    Args:
        config (configparser.ConfigParser): A ConfigParser.
        section (str): The section of the config file to get information from.
        attribute (str): The attribute of the section to fetch.

    Returns:
        str: The string corresponding to the section and attribute.

    Raises:
        ValueError
    """
    try:
        return config[section][attribute]
    except KeyError:
        raise ValueError(f"""Config file badly formed!
                \nFailed to get attribute '{attribute}' from section '{section}'!""")

def send_with_attachments_autoconf(subject, message, filepaths):
    """Send an email with the user, password and reciever defined in config.ini.

    Args:
        subject (str): Subject of the email.
        message (str): A message.
        filepaths (list(str)): Filepaths to files to be attached.
    """
    user, password, reciever = read_email_config()
    send_with_attachments(user, password, reciever, subject, message, filepaths)

def send_with_attachments(sender, password, reciever, subject, message, filepaths):
    """Send an email from the sender (a gmail) to the reciever.

    Args:
        sender (str): The sender's email address.
        password (str): The password to the 'sender' address.
        reciever (str): The reciever's email address.
        subject (str): Subject of the email.
        message (str): A message.
        filepaths (list(str)): Filepaths to files to be attached.
    """
    email_ = MIMEMultipart()
    email_.attach(MIMEText(message))
    email_["Subject"] = subject
    email_["From"] = sender
    email_["To"] = reciever
    attach_files(filepaths, email_)
    send_email(sender, password, email_)


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
            part["Content-Disposition"] = f'attachment; filename="{base}"'
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

def send_files_preconf(filepaths):
    """Send files using the config.ini settings.

    Args:
        filepaths (list(str)): A list of filepaths.
    """
    user, password, reciever = read_mail_config(CONFIG_RELATIVE_PATH)
    subject = "PDF files from pdfebc"
    message = ""
    send_with_attachments(
        user, password, reciever, subject, message, filepaths
        )

def make_output_directory(path):
    """Create the output directory.

    Args:
        path (str): Path to the directory.
    """
    subprocess.call(["mkdir", "-p", path])

def rm_r(path):
    """Recursive remove starting from 'path'.

    Args:
        path (str): Path to the directory.
    """
    subprocess.call(['rm', '-r', path])
