#!/bin/bash

# set config flags
debug_flags="-all,err+all"
prefix_path="/Volumes/thunderbolt-drive/wine/xenon"


WINEDEBUG=$debug_flags WINEPREFIX=$prefix_path wineconsole 2_compress.bat

