"""Main module for the PDFEBC project.

Author: Simon Larsén
"""
import cli
import core
import utils

def main():
    """Run PDFEBC."""
    parser = cli.create_argparser()
    args = parser.parse_args()
    if not args.nomakedir:
        utils.make_output_directory(args.outdir)
    filepaths = core.compress_multiple_pdfs(args.sourcedir, args.outdir, args.ghostscript)
    if args.send:
        utils.send_files_preconf(filepaths)
    if args.clean:
        utils.rm_r(args.outdir)

if __name__ == '__main__':
    main()
