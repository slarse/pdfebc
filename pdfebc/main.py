# -*- coding: utf-8 -*-
"""Main module for the PDFEBC project.

Author: Simon Larsén
"""
import os
import shutil
from . import cli, core, utils

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
            user, password, reciever = cli.prompt_for_config_values()
            config = utils.create_email_config(user, password, reciever)
            utils.write_config(config)
        utils.send_files_preconf(filepaths)
    if args.clean:
        shutil.rmtree(args.outdir)

if __name__ == '__main__':
    main()
