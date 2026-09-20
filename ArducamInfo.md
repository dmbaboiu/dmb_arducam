# Arducam info

## Using USB3 Camera Shield UC-593 Rev C

***NOTE:*** This combination does NOT support *External Trigger* (firmware does not accept it).
 Only the Streaming Demo can be used.

There are three main interfaces published by Arducam. Note that the Python demos, in all versions,
 require *opencv-python*, along with its own dependency, `numpy`, for image processing (especially debayering,
 which is not supported by `Pillow`) and for image display in its standalone demo.  

1. (The original SDK)[https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield]: fully self-contained, except for  for Linux.
    Contains demos for C/C++ and Python, for Windows, Linux, RaspberryPi, Nvidia Jetson
    * Configuration files for various sheild/camera combinations
    * Drivers for Windows, also available from its Releases section
    * Linux only needs  standard USB libraries (libusb) and setting udev rules to allow regular user run without *sudo*
    * Demos for Windows include a GUI tool to open the camera using configuration file and do image capture, as well as possibility to view/change camera registers
    * The SDK includes binaries for Python 2.7 (not versioned), as well as for Python 3.6-3.8. However, the demos are fully compatible with the Python dependencies in the "split" demo, which can be installed via `pip`.
       To run, you need to remove the ArducamSDK libraries and the config_parser. Otherwise, python will try to load these and fail.
    * The repo does **not** include the Linux dynamic library for *arducam_config_parser* (only the Python wrapper), but that can be obtained from [its own repo](https://github.com/ArduCAM/arducam_config_parser). **NOTE** that this is only an early version, not supporting all features (e.g. Controls); it is incompatible with the parser used by demo. Only the Windows version contains the corresponding library.
    * The SDK User Guide (API documentation) is available online as PDF (see below), but is incomplete.
    * **Not all functions of the SDK are documented,**. For example, `ArducamSDK.Py_ArduCam_readReg_8_8()` is used in the demo, but is not present in the published documentation.


1. The "new" version, splits the CPP and Python demos into separate repos. 
    * [ArduCAM_USB_Camera_Shield_Cpp_Demo](https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield_Cpp_Demo); the SDK User Guide is [available online as PDF](https://blog.arducam.com/downloads/shields/USB_Shield/ArduCAM_USB_Camera_SDK_Guide_V1.3.pdf)
    * [ArduCAM_USB_Camera_Shield_Python_Demo](https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield_Python_Demo); the SDK User Guide is [available online as PDF](https://blog.arducam.com/downloads/shields/USB_Shield/ArduCAM_USB_Camera_Python_SDK_Guide_V1.3.pdf)
    * Drivers are to be downloaded from Releases of the original SDK
    * The demo uses the same SDK as v1, but it has object oriented structure (`class ArducamCamera`, wrapped around the same API; its methods contain some of the boilerplate functions from the original demo).
    * Config files are not provided, but there is a separate github repo (mostly identical with the original), [ArduCAM_USB_Camera_Shield_Config](https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield_Config)
    * Python dependencies are to be installed via *pip*, from [PyPI](pypi.org)
        > python3 -m pip install arducam_config_parser ArducamSDK
        - [arducam_config_parser](https://pypi.org/project/arducam-config-parser/#files) has single wheel for all Python versions, wraps around *so* library
        - [ArducamSDK](https://pypi.org/project/ArducamSDK/#files) has wheels for Python versions 2.7, 3.5-3.12; wraps around the *.so* library.
    * CPP dependencies are to be installed via apt as *.deb* files from the Arducam repo, but these are stored at [Arducam PPA on Guthub](https://github.com/ArduCAM/arducam_ppa) along with other related binaries.
        * *arducam_config_parser-dev*
        * *arducam-usb-sdk-dev*

   
1. [ArduCam EVK Demo](https://github.com/ArduCAM/ArduCam_EVK_Demo), a more object-oriented approach, with demos for C, C++, Python.
    Drivers for Windows are aslso stored in the Release section of the original repo.  
    For python, it contains a *requirements.txt* file, with the main package *arducamevksdk* to be installed via *pip*. These are available for Python 2.7 and 3.5-
    This package includes *arducam-config-parser* as a dynamic library, used internally by the EVK SDK.  
    The camera registries are no longer loaded manually; instead, the file name is passed when the camera is open.

    The API documentation is [available online](https://www.arducam.com/docs/arducam-evk/)


***arducam_config_parser*** does not provide the dynamic library for Linux in the original, but has its own
[github repo](https://github.com/ArduCAM/arducam_config_parser), containing in its Releases folder the *.so*,
along with the corresponding *.h* and *.py* files. This utility parses a *.conf/.ini* file with
commands to initialize the camera, as well as configuration for the board and camera registry.

The config file is organized in sections like a regular *.ini* file, but keys for VRCMD, REG and DELAY are repeated,
and stored in ordered list, keeping the sectioning. The corresponding entries have a *type* field with flags as bitfields
identifying the command and its sectioning information.

Note that a regular configparser (like the one in the Python standard library) do not allow repeated keys.


## Connecting the camera

On Windows, you need to install the drivers for connecting via USB.

On Linux,Due to permission restrictions (the new device is owned by *root*), the capture programs will have to be run with *sudo*. This can be avoided by changing the *udev* rules:
1. Put these in /etc/udev/rules.d/arducam-usb.rules:
> SUBSYSTEM=="usb",ENV{DEVTYPE}=="usb_device",ATTRS{idVendor}=="52cb",MODE="0666"  
> SUBSYSTEM=="usb",ENV{DEVTYPE}=="usb_device",ATTRS{idVendor}=="04b4",MODE="0666"

2. Run:
> sudo udevadm control --reload-rules && sudo udevadm trigger

## Outline of operation

1. Load the config file using *arducam_config_parser*
2. Open the camera, passing the `[camera parameter]` values in a structure. Use `autoopen` if you have only one camera.
3. Load the register values (for board and for camera), keeping in mind the USB configuration.
4. Capture the image:
   * Start capture: `beginCaptureImage()`
   * Capture: `captureImage()`. Each successful call results in an image stored in the buffer, up to maximum capacity. The call returns an error code.
   * End capture when done: `endCaptureImage()`
6. Read the image ():
   * Check if any image is available; `availableImage()` returns the number of available in the buffer
   * Read the image from buffer, `readImage()`
   * Delete the image from the buffer, `del()`, to make space for a new capture
   * When completely done, call `flush()` to completely clean the camera buffer

## Common approach -- Normal use (streaming) starts two threads:
1. Start a ***capture image thread***
    1. Call `beginCaptureImage()` when thread starts
    2. Send `captureImage()` command continuously
    3. When thread ends, call `endCaptureImage()`
	
2. Start a ***read image thread***
    1. Check if an image is available, `imageAvailable()` (returns number of images in camera buffer)
    2. Read the image (`readImage()`) as soon as it becomes available and process it
    3. Delete image from camera buffer to make room for next capture
	
3. The threads will end when a control variable is set.

## Non-threaded approach:
The threaded approach is not the only approach. It is also OK to check and read the image after a successful capture in the same (main) thread. This approach is useful if a single image needs to be captured for diagnostics. 

1. Call `beginCaptureImage()`

2. In a continuous loop,
    1. Call `captureImage()`
    2. Check if image is available, and read it if it is (and delete from buffer).

3. Call `endCapture` when done

**NOTES:**

1. In documentation, error code 0 is marked as "no error". In practice, all actual error codes are above 0xFF00. Sample code marks `rtn_val > 255` as errors. I found that `1` is usually returned as return value by `captureImage()`.
2. An image may still be captured for some error codes (e.g., `USB_CAMERA_FRAME_INDEX_ERROR`, code `0xFF25`), although the image may be corrupt. Unless the image is needed for diagnostics, it should be deleted.
3. It is normal to have some errors at the beginning (e.g., `USB_CAMERA_DATA_LEN_ERROR`, code `0xFF24`). This usually vanishes as parameters take effect (in
4. If there is a delay (in my experiment, between 0.01 and 0.1 seconds), the next capture may end with error.
