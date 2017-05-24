"""Module containint util functions for the PDFEBC project.

Uses Google's SMTP server for sending emails. If you wish to use another server, simply change
the SMTP_SERVER variable.

Requires a config file in $HOME/.config/pdfebc/config.ini that should look like:
    [EMAIL]
    user = sender_email
    pass = password
    reciever = reciever_email

All characters after the colon and whitespace (as much whitespace as you'd like) until
EOL counts as the username/password.

Author: Simon Larsén
"""
import smtplib
import os
import configparser
import subprocess

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

CONFIG_RELATIVE_PATH = ".config/pdfebc/config.ini"
SECTION_KEY = "EMAIL"
PASSWORD_KEY = "pass"
USER_KEY = "user"
RECIEVER_KEY = "reciever"
SMTP_SERVER = "smtp.gmail.com"

def read_email_config(config_relative_path=CONFIG_RELATIVE_PATH):
    """Return the contents of the config file.

    config_relative_path -- Relative path to the email config file.
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
    """Try to parse an attribute of the config file."""
    try:
        return config[section][attribute]
    except KeyError:
        raise ValueError(f"""Config file badly formed!
                \nFailed to get attribute '{attribute}' from section '{section}'!""")

def send_with_attachments_autoconf(subject, message, filepaths):
    """Send an email with the user, password and reciever defined in config.ini.

    Arguments:
    subject -- Subject of the email.
    message -- A message.
    filepaths -- Filepaths to files to be attached.
    """
    user, password, reciever = read_email_config()
    send_with_attachments(user, password, reciever, subject, message, filepaths)

def send_with_attachments(sender, password, reciever, subject, message, filepaths):
    """Send an email from the sender (a gmail) to the reciever.

    sender -- A Google Mail address.
    password -- The password to the 'sender' address.
    reciever -- The recievers' email address.
    subject -- Subject of the email.
    message -- A message.
    filepaths -- Filepaths to files to be attached.
    """
    email = MIMEMultipart()
    email.attach(MIMEText(message))
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = reciever
    attach_files(filepaths, email)
    send_email(sender, password, email)


def attach_files(filepaths, message):
    """Take a list of filepaths and attach the files to a MIMEMultipart."""
    for filepath in filepaths:
        base = os.path.basename(filepath)
        with open(filepath, "rb") as file:
            part = MIMEApplication(file.read(), Name=base)
            part["Content-Disposition"] = f'attachment; filename="{base}"'
            message.attach(part)

def send_email(user, password, email):
    """Sends the email."""
    server = smtplib.SMTP(SMTP_SERVER, 587)
    server.starttls()
    server.login(user, password)
    server.send_message(email)
    server.quit()

def send_files_preconf(filepaths):
    """Email files using the config.ini settings.

    Arguments:
    filepaths -- A list of filepaths.
    """
    user, password, reciever = read_email_config(CONFIG_RELATIVE_PATH)
    subject = "PDF files from pdfebc"
    message = ""
    send_with_attachments(
        user, password, reciever, subject, message, filepaths
        )

def make_output_directory(path):
    """Create the output directory."""
    subprocess.call(["mkdir", "-p", path])

def rm_r(path):
    """Recursive remove starting from 'path'."""
    subprocess.call(['rm', '-r', path])
