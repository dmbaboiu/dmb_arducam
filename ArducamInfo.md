# Arducam info

## Using USB3 Camera Shield UC-593 Rev C

***NOTE:*** This combination does NOT support *External Trigger* (firmware does not accept it). Only the Streaming Demo can be used.

There are three main interfaces published by Arducam. Note that the Python demos, in all versions, require *opencv-python*, along with its own dependency, 

1. (The original SDK)[https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield]: fully self-contained, except for  for Linux.
    Contains demos for C/C++ and Python, for Windows, Linux, RaspberryPi, Nvidia Jetson
    * Configuration files for various sheild/camera combinations
    * Drivers for Windows, also available from its Releases section
    * Linux only needs  standard USB libraries (libusb) and setting udev rules to allow regular user run without *sudo*
    * Demos for Windows include a GUI tool to open the camera using configuration file and do image capture, as well as possibility to view/change camera registers
    * The SDK includes binaries for Python 2.7 (not versioned), as well as for Python 3.6-3.8. However, the demos are fully compatible with the Python dependencies in the "split" demo, which can be installed via `pip`.
       To run, you need to remove the ArducamSDK libraries and the config_parser. Otherwise, python will try to load these and fail.
    * The repo does **not** include the Linux dynamic library for *arducam_config_parser* (only the Python wrapper), but that can be obtained from [its own repo](https://github.com/ArduCAM/arducam_config_parser) **NOTE** that this is only an early version, not supporting all features (e.g. Controls); it is incompatible with the parser used by demo. Only the Windows version contains the corresponding library.
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

6. In documentation, error code 0 is marked as "no error". In practice, all actual error codes are above 0xFF00. Sample code marks `rtn_val > 255` as errors. I found that `1` is usually returned as return value by `captureImage()`.
2. An image may still be captured for some error codes (e.g., `USB_CAMERA_FRAME_INDEX_ERROR`, code `0xFF25`), although the image may be corrupt. Unless the image is needed for diagnostics, it should be deleted.
3. It is normal to have some errors at the beginning (e.g., `USB_CAMERA_DATA_LEN_ERROR`, code `0xFF24`). This usually vanishes as parameters take effect (in
4. If there is a delay (in my experiment, between 0.01 and 0.1 seconds), the next capture may end with error.


## Error codes:

### USB_CAMERA_DATA_LEN_ERROR (Error code 0xFF24)
In the Arducam SDK, it means a data transmission mismatch or dropped frame has occurred. This happens when the host fails to process incoming USB data in time, resolution/config settings do not match the hardware profile, or bandwidth is constrained.
This is a transmission error. The data may be lost due to the failure to process the data output by the device in time.

*Common Causes and Fixes*
 * USB Port Speed: Ensure your camera is plugged into a true USB 3.0 (or higher) port. Plugging a high-bandwidth USB 3.0 Arducam shield or kit into a USB 2.0 port frequently triggers length and timeout errors.
 * Mismatched Configuration: Verify that the .cfg or .json resolution and pixel clock configuration file matches your exact sensor model, lane count, and hardware revision. Do not manually alter width/height parameters inside code without updating the base config.
 * System Bottlenecks / CPU Load: Reduce the pixel clock frequency in your configuration file if your host processor (such as a Raspberry Pi) cannot handle the high data throughput rate.
 * Transient Startup Errors: If the length error only fires once or twice during the initial stream bootup sequence and then disappears, it is normally safe to ignore.

Suggestion: do not stop the capture thread. The capture thread is actually the thread that obtains data from the USB. If it does not process the USB data in time, it will cause problems with the data on the device.


### USB_CAMERA_FRAME_INDEX_ERROR (code 0xFF25)
In the Arducam SDK, this error means the host software requested an invalid or out-of-bounds frame index, or the USB data stream fell out of sync during image capture/buffer retrieval.
This error means that the image frames are not continuous, and each image frame has a frame number. If it is not continuous, it will prompt this error, but you can ignore it.

*Causes and Fixes*
 * Incorrect Resolution or Format Settings
   ** Cause: Requesting a frame size, mode, or pixel format that the active camera firmware or configuration preset does not support.
   ** Fix: Check your initialization script or GUI settings. Ensure the resolution and color format match the exact parameters defined in your config file.
 * Capture Thread Interruption / Timing Issues
   ** Cause: Stopping, restarting, or overlapping the frame capture thread too quickly causes the SDK to lose track of the active buffer index.
   ** Fix: Keep the continuous capture loop running stable without abruptly killing and re-initializing the capture instance on every single frame.
 * USB Bandwidth or Connection Faults
   ** Cause: Dropped packets or slow bus transfer speeds (especially on high-resolution or high-framerate USB 3.0/2.0 cameras) desynchronize the frame counter.
   ** Fix: Connect directly to a native USB port (avoid passive hubs), use a shorter or high-quality shielded USB cable, and lower the framerate or resolution to test stability.
   

## Configuration file

### Image formats
> FORMAT    = &lt;value1&gt;[, &lt;value2&gt;]
**FORMAT** sets the format of the image generated by the camera.
* `&lt;value 1&gt;` is the main format, set in the configuration sent to camera when opening connection.
* `&lt;value 2&gt;` is the subtype, used internally to decode the raw data into color image. Used only by raw-like color formats to specify channel ordering, and passed only to processing decoder. Monochrome formats do not use it.

Arducam st_raw typically refers to saving, capturing, or streaming sensor raw data (such as Bayer RAW formats) using Arducam's software development kits or example repositories (like their MIPI or SPI camera C/C++ libraries)

**Capturing and Handling Raw Data**
* *Image Encoding*: Functions use definitions like IMAGE_ENCODING_RAW_BAYER to fetch unprocessed sensor pixels.
* *Alignment and Resolution*: Raw sensor frames often require specific byte-width and height alignment (e.g., width aligned to 32 bytes and height to 16 bytes depending on the SDK implementation).
* *Storage*: Raw frames can be dumped directly into binary *.raw* or *.dng* files via host evaluation software or embedded scripts for offline processing.
* *Display Limitation*: Standard LCD or preview windows may display incorrect or false colors when fed raw Bayer data directly because proper debayering/demosaicing is required before RGB conversion


In Arducam configuration files and software SDKs, RAW and ST_RAW are distinct data format identifiers used to define how sensor pixel data is read, structured, and parsed by the host application or USB/MIPI camera shield.
* *RAW*
    * **Definition**: Standard uncompressed Bayer or raw sensor data format.
    * **Data Handling**: The pixel values are streamed directly from the sensor array with standard color gain parameters (Red, GreenR, GreenB, Blue) mapped traditionally. The same is valid for Monochrome images (separate gains for the four pixels in the square), although it doesn't make much sense to have different values in this case. 
    * **Use Case**: General computer vision, image processing, or saving standard unedited Bayer grid arrays for debayering on a host processor.
* *ST_RAW*
    * **Definition**: "Software Trigger" or specialized stream-indexed raw format (FORMAT = 5) used in Arducam's proprietary USB/MIPI evaluation software and configuration profiles.
    * **Data Handling**: While it still processes raw sensor matrix streams and accepts color balance gains (R, B, G1), it tells the Arducam firmware/SDK pipeline to handle packet framing, synchronization, or triggering flags specific to Arducam's developer kits and testing software.
    * **Use Case**: Controlled industrial captures, multi-camera synchronization, or when utilizing Arducam's specialized USB test and evaluation GUIs that require specific packet headers.
