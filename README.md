# pdfebc - PDF ebook compressor

**[Docs](http://pdfebc.readthedocs.io/en/latest/)**

[![Build Status](https://travis-ci.org/slarse/pdfebc.svg?branch=master)](https://travis-ci.org/slarse/pdfebc)
[![codecov](https://codecov.io/gh/slarse/pdfebc/branch/master/graph/badge.svg)](https://codecov.io/gh/slarse/pdfebc)
[![Documentation Status](https://readthedocs.org/projects/pdfebc/badge/?version=latest)](http://pdfebc.readthedocs.io/en/latest/?badge=latest)


## Overview
`pdfebc` is a CLI tool that uses `Ghostscript` to compress PDF documents to a size that befits 
an ebook reader, such as a Kindle. The CLI works by targeting a source and output directory (if 
not specified by the user, defults to use `.` for source and `pdfebc_out` for output), then 
compresses all PDF files in the source directory and puts the results in the output directory. 
There is also functionality for sending the compressed documents to a pre-configured e-mail 
address using Google's SMTP server (which can easily be swapped for any SMTP server by editing 
the source code, see **Requirements** below). Files that are less than 1 MB in size are not 
compressed, as I have found that compressing such small files often leads to them increasing 
in size several times over instead (I have yet to figure out why). Do note that `Ghostscript` 
is fairly slow, so expect large files to take a while to compress.

As an example use case, I mainly use `pdfebc` as an easy way to compress lecture slides and 
similar study materials, send them to my Kindle and then clean up the output.

### Purpose of the project
The core functionality of `pdfebc` was already done when I started this little project. As 
such, the main purpose here isn't to provide the functionality, but to do so in a robust way, 
with proper documentation, testing and continuous integration. It is, essentially, my first 
foray into using stuff like `sphinx`, `Travis-CI` and `ReadTheDocs`, so there's bound to be 
some weirdness here and there.

### Requirements
* Python 3.6
    - Strictly speaking, 3.5 should also work fine, but the tests use 3.6 features so the
    build is only tested for 3.6.
* `Ghostscript`
    - `pdfebc` requires `Ghostscript` for the PDF compression. The default binary is `gs`,
    but this can be specified via the CLI.
* A Gmail account (for sending e-mails)
    - By default, `pdfebc` uses Google's SMTP server to send e-mails. If you don't intend
    to use the send functionality, then you may disregard this requirement.
    - It is possible to use a different SMTP server by changing the `SMTP_SERVER` variable in the
    `pdfebc.utils` module. Note that TLS is enabled and will likely cause sending e-mails
    using a local server that does not have TLS imnpossible.

### Install
1. Clone the repo with `git`:
    - `git clone https://github.com/slarse/pdfebc`
2. `cd` into the project root directory and install with `pip`.
    - `pip install --user .`, global installs are not recommended.
    - Or just `pip install .` if you use `virtualenv`.
    - For development, use `pip install -e .` in a `virtualenv`.
3. All done! Type `pdfebc -h` on the command line for usage.
4. Note that the first time you try to send an e-mail, the CLI will walk you through the creation
of a configuration file. I strongly recommend that you use an 
[App password](https://support.google.com/accounts/answer/185833?hl=en) instead of your
actual account password.

### License
This software is licensed under the MIT License. See the [LICENSE](LICENSE) file for specifics.

### TODO
* Improve code coverage.
* Add more negative tests.
* Add status messages to show progress (for example, which file is currently being 
compressed and how many are left).
