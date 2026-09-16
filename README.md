# Arducam camera with USB shield

## Motivation

A while ago I bought several cameras, most importantly two cameras, monochrome and color versions of the same model.
The firmware is exactly the same for both (the only difference is the presence of the Bayer array on the color version).
Since these cameras can not be connected to a RaspberryPi (they use DVP, not MIPI), I had to also purchase an USB3 adapter board.

Arducam provides three main interfaces for their cameras installed on camera shields:

1. The original SDK: mostly self-contained.
    The Linux version does not contain the dynamic libraries for `arducam_config_parser`. 
    The `ArducamSDK` has only binary versions written in `Cython`, for Python 3.6, 3.7, 3.8
    
1. The "new" version, splits the CPP and Python demos into separate repos. Drivers and configuration files
   are to be used from the original repo. Uses the same SDK, but comes with an object-oriented wrapper,
   also encapsulating some boilerplate functions. The Python libraries are available via `pip`, only for Python 3.5 to 3.12

1. Arducam EVK:a more object-oriented Python interface, with packages loaded by `pip`, supporteds for Python 3.5 to 3.14 (the most recent as of this writing). More comprehensive, but leaves the impression of being overdesigned, and the demos are very basic.

The purpose if this project is to provide a Python wrapper around the C/C++ dynamic libraries for the original SDK,
independent of the Python version (although some Python features may be specific to more recent releases). The dynamic libraries
are retrieved from the `.deb` files for the C/C++ version 

Another task will be to build a GUI interface similar to the `USBTest` executable available for Windows. As usual, OpenCV is necessary
for image processing, particularly for debayering raw color images. This GUI might be enhanced with other features to make easier to
tweak camera parameters (registers, etc.)

**NOTE:** OpenCV uses BGR format for color channels, while others (PIL, for example) use RGB, thus requiring rearranging the channels.
