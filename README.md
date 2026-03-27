# firstapp

`firstapp` is a small command line tool that bootstraps a project directory.

It is set up so you can:

- run it locally during development
- package it as a Debian package
- eventually distribute it through `apt install`

## What the CLI does

The starter command:

```bash
firstapp init my-project
```

creates:

- `src/`
- `tests/`
- `.gitignore`
- `README.md`
- `firstapp.json`

without overwriting files that already exist.

## Local development

Run it without installing:

```bash
PYTHONPATH=src python3 -m firstapp init demo-project
```

Show help:

```bash
PYTHONPATH=src python3 -m firstapp --help
```

## Packaging as a Debian package

This repo includes a `debian/` directory so it can be built into a `.deb` package on a Debian or Ubuntu machine with the packaging tools installed.

Typical flow:

```bash
sudo apt install build-essential debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools
dpkg-buildpackage -us -uc
```

That produces a `.deb` one directory above the repo.

## How `apt install firstapp` works

For users to install with `apt install firstapp`, you need to publish the package in an APT repository. Common approaches:

1. Build the `.deb`
2. Host it in an APT repo or PPA
3. Users add that repo
4. Users run `sudo apt update && sudo apt install firstapp`

You cannot make plain `apt install firstapp` work globally unless the package is in a repo that the user's system knows about.
