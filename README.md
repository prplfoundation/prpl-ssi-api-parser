# prpl HL-API Specification Parser

Parses a Microsoft Excel based specification of the prpl HL-API and converts it into other formats.
 
Currently supports the generation of:
- A Microsoft Word file containing an updated cover, release notes, return codes, objects, procedures and events. 

Note: Does not automatically update the Table of Contents.

- A Graphviz diagram in both ".gv" and ".png".

Note: May require updating "config.json" in case the "PATH" system variable was not updated with the Graphviz bin folder.

## Environment

Tested on both Windows and Mac OS with Python 3. However, the “Makefile” is tailored specifically for the latter.

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
Run parser.

Notes:
- Make sure to download the HL-API specification and place it under the "specs/input" folder.
- Update the file path on "launcher.py" file to match the intended spec file.

```
make run
```