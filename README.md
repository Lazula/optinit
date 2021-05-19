# optinit

This project started as a script to initialize my `/opt` folder with custom scripts of my own creation, public git repositories, and pre-compiled binaries, but as it progressed, I generalized several features and decided that it should be released.
This repository is made public for many reasons, including my own convenience, use as a reference by others, and a demonstration of basic scripting and administrative ability.
It is intended for use primarily on Kali Linux (ideally via `live-build` if I ever get `apt` to work properly...) or single-user pentesting distributions more generally, but it should function on any distribution of GNU/Linux, as long as both Bash and Python 3 are present.
There are no plans at this time to support other operating systems.
Please note that any dependencies or packages needed are not checked for or included at this time.
For further details about installed software, please refer to the files contained in [directory_readmes](directory_readmes) for each folder, which are placed in the respective directories after installation.

At this time, no actions are taken within each repository.
This may change in the future, though it may be determined to be outside this project's scope.

## Usage

Simply clone this repository and run `optinit.py` with desired arguments.
By default, it is not suited to unattended installation - the script will *not* continue if a recoverable error is encountered, preferring to simply complain and exit.
Provide the `-i/--ignore-errors` flag to exit only on nonrecoverable errors.
An internet connection is expected unless the `-l/--local-only` flag is provided, which disables all remote downloads.
When an error is encountered, if the current execution context defines it as requiring program termination, the proper `errno` error code is propagated to `sys.exit()`.

## Binaries

The binary information file is in JSON format, with the name on disk as the key and a dictionary containing its parameters as the value.
Each dictionary must contain the following entries:

* `source_url_format`: A format string used as the parent directory for downloading the binary and any related files.
* `file_name_format`: A format string used to determine the literal file name to download from the remote server.

Additionally, the following optional entries may be used:

* `checksum_file_name_format`: A format string used to determine the literal file name for a release checksum file. Requires `checksum_algorithm`.
* `checksum_algorithm`: The type of checksum to use. Accepts `"md5"`, `"sha1"`, `"sha256"`, and `"sha512"`.
* `compressed`: If present and `true`, extract the downloaded binary with gzip before writing it to disk.
* `release_version`: A convenience variable to streamline specifying and updating release versions.

The format strings may use any of the other arguments excluding the other format strings\*.
They may also use `arch_string`, the `arch_strings` entry corresponding to the value of `arch`, which is either `"32"` or `"64"`.

\* You *can* use the other format strings, but it is not officially supported and the order they are formatted in is not guaranteed to stay the same.

The script automatically detects the python binary architecture to determine whether to download 32-bit or 64-bit binaries.

## Repositories

The repository information file is in JSON format, with the directory name as the key and the remote URL as the value.
Adding custom repositories is as simple as adding new entries in this file or providing a custom file.
A custom repository file can be selected with `-r`, which overrides the default, `repositories.txt`.
If the name of an existing repository is changed in this file, updating an existing installation will *not* delete or rename the original.
The ability to track repositories by remote URL may be added in the future.

## Shells

Shells can be configured similarly to repositories and binaries.
No formal documentation currently exists, but it will be added soon.
Please consult the source code for information - the variables are documented there.

## Security

The initialization script contains command execution via the `subprocess` module using data that could potentially be modified by a malicious actor.
Please ensure the integrity of these files before using them.
Once installed, the code contained here is no longer necessary unless you want to update an existing installation and may be deleted if desired.

## Licensing

This program is distributed under the GNU GPL, version 3 or later; see [COPYING](COPYING).
If a script does not contain explicit copyright information, consider it to be a part of this project for copyright purposes.
While the licensing of related projects varies, the terms do not apply this project, as it merely provides a method to acquire each piece of software from its original source, and does not redistribute any of them itself.
If you would like to redistribute any related projects yourself, please ensure you follow any relevant licensing constraints.
