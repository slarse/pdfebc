# -*- coding: utf-8 -*-
"""Main module for the PDFEBC project.

Author: Simon Larsén
"""
import os
import shutil
import smtplib
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
    parser = cli.create_argparser()
    args = parser.parse_args()
    if not args.nomakedir:
        os.makedirs(args.outdir)
    filepaths = core.compress_multiple_pdfs(args.sourcedir, args.outdir,
                                            args.ghostscript, cli.status_callback)
    if args.send:
        if not utils.valid_config_exists():
            user, password, receiver = cli.prompt_for_config_values()
            config = utils.create_email_config(user, password, receiver)
            utils.write_config(config)
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
