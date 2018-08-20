# prpl HL-API Specification Parser

Parses a Microsoft Excel based specification of the prpl HL-API and generates a Microsoft Word file containing an updated cover, release notes, return codes, objects, procedures and events.

Note: Does not automatically update the Table of Contents.

## Environment

Tested on both Windows and Linux (Ubuntu) with Python 3. However, the “Makefile” is tailored specifically for Linux.

## Clean
Cleans up cache files and previously generated specifications.

```
make clean
```

## Install
Install dependencies.

```
make install
```

## Test
Run Python unit tests.

```
make test
```

## Run
Run parser. Change the filepath on "launcher.py" file to parse a different file.

```
make run
```