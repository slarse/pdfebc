# -*- coding: utf-8 -*-
"""Main module for the PDFEBC project.

Author: Simon Larsén
"""
import os
import shutil
import smtplib
import sys
from . import cli, core, utils

AUTH_ERROR = """An authentication error has occured!
Status code: {}
Message: {}

This usually happens due to incorrect username and/or password in the configuration file, 
so please look it over!"""

UNEXPECTED_ERROR = """An unexpected error occurred when attempting to send the e-mail.

Python error repr: {}

Please open an issue about this error at 'https://github.com/slarse/pdfebc/issues'.
"""

def main():
    """Run PDFEBC."""
    try:
        parser = cli.create_argparser()
    except utils.ConfigurationError as e:
        print("FIRST TIME CONFIG NOT YET IMPLEMENTED")
        print("FIX THE CONFIG FILE!")
        print("EXITING!")
        print(e)
        sys.exit(1)
    args = parser.parse_args()
    os.makedirs(args.outdir)
    filepaths = core.compress_multiple_pdfs(args.srcdir, args.outdir,
                                            args.ghostscript, cli.status_callback)
    if args.email:
        if not utils.valid_config_exists():
            # TODO Add step-by-step config creation here.
            pass
        try:
            utils.send_files_preconf(filepaths, status_callback=cli.status_callback)
        except smtplib.SMTPAuthenticationError as e:
            cli.status_callback(AUTH_ERROR.format(e.smtp_code, e.smtp_error))
        except Exception as e:
            cli.status_callback(UNEXPECTED_ERROR.format(repr(e)))
    if args.clean:
        shutil.rmtree(args.outdir)

if __name__ == '__main__':
    main()
