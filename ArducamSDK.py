from ctypes import *
import sys, os, time
import platform
import enum

try:
    abs_path = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        lib_name = "ArduCamLib.dll"
    elif platform.system() == "Linux":
        lib_name = "libArduCamLib.so"

    abs_lib_name = os.path.join(abs_path, lib_name)
    if os.path.exists(abs_lib_name):
        _libArduCam = cdll.LoadLibrary(abs_lib_name)
    else:
        _libArduCam = cdll.LoadLibrary(lib_name)
except Exception as e:
    print("Load lArduCamLib failed. Make sure it is installed.")
    print(e)
    sys.exit(0)

print("Loading custom ArducamSDK")
RAW_RG                                 = 0
RAW_GR                                 = 1
RAW_GB                                 = 2
RAW_BG                                 = 3

USB_1                                  = 1      # USB 1.0
USB_2                                  = 2      # USB 2.0
USB_3                                  = 3      # USB 3.0
USB_3_2                                = 4      # USB3.0 mode and USB2.0 interface

EXTERNAL_TRIGGER_MODE                  = 0x01
CONTINUOUS_MODE                        = 0x02

USB_CAMERA_NO_ERROR                    = 0x0000
USB_CAMERA_USB_CREATE_ERROR            = 0xFF01
USB_CAMERA_USB_SET_CONTEXT_ERROR       = 0xFF02
USB_CAMERA_VR_COMMAND_ERROR            = 0xFF03
USB_CAMERA_USB_VERSION_ERROR           = 0xFF04
USB_CAMERA_BUFFER_ERROR                = 0xFF05
USB_CAMERA_NOT_FOUND_DEVICE_ERROR      = 0xFF06
USB_CAMERA_I2C_BIT_ERROR               = 0xFF0B
USB_CAMERA_I2C_NACK_ERROR              = 0xFF0C
USB_CAMERA_I2C_TIMEOUT                 = 0xFF0D
USB_CAMERA_USB_TASK_ERROR              = 0xFF20
USB_CAMERA_DATA_OVERFLOW_ERROR         = 0xFF21
USB_CAMERA_DATA_LACK_ERROR             = 0xFF22
USB_CAMERA_FIFO_FULL_ERROR             = 0xFF23
USB_CAMERA_DATA_LEN_ERROR              = 0xFF24
USB_CAMERA_FRAME_INDEX_ERROR           = 0xFF25
USB_CAMERA_USB_TIMEOUT_ERROR           = 0xFF26
USB_CAMERA_READ_EMPTY_ERROR            = 0xFF30
USB_CAMERA_DEL_EMPTY_ERROR             = 0xFF31
USB_CAMERA_SIZE_EXCEED_ERROR           = 0xFF51
USB_USERDATA_ADDR_ERROR                = 0xFF61
USB_USERDATA_LEN_ERROR                 = 0xFF62
USB_BOARD_FW_VERSION_NOT_SUPPORT_ERROR = 0xFF71

# enums used as attributes of ArduCamCfg. In configuration files, used directly as integers.
# Not used in sample code; Present in ArduCam_Demo.cpp, to convert integers from config file
# into these values. However, the values are the same, and the Python demo just populates it directly.
# In the original, these are just global variables with integer values.

# class i2c_mode(enum.IntEnum):
I2C_MODE_8_8   = 0
I2C_MODE_8_16  = 1
I2C_MODE_16_8  = 2
I2C_MODE_16_16 = 3
I2C_MODE_16_32 = 4

# class format_mode(enum.IntEnum):
FORMAT_MODE_RAW   = 0
FORMAT_MODE_RGB   = 1
FORMAT_MODE_YUV   = 2
FORMAT_MODE_JPG   = 3
FORMAT_MODE_MON   = 4
FORMAT_MODE_RAW_D = 5
FORMAT_MODE_MON_D = 6

    
class ArduCamCfg(Structure):
    """
    This structure is required by the C interface with the dynamic library, but the
    Python API uses the more convenient dictionary. Convenience functions are provided
    to facilitate the use.
    """
    _fields_ = [('u32CameraType',  c_uint32),      # Uint32
                ('u16Vid',         c_uint16),      # Uint16     # Micron Imaging Vendor ID for USB
                ('u32Width',       c_uint32),      # Uint32
                ('u32Height',      c_uint32),      # Uint32
                ('u8PixelBytes',   c_uint8),       # Uint8
                ('u8PixelBits',    c_uint8),       # Uint8
                ('u32I2cAddr',     c_uint32),      # Uint32
                ('u32Size',        c_uint32),      # Uint32
                ('usbType',        c_uint8),       # Uint8
                ('emI2cMode',      c_uint),        # enum i2c_mode
                ('emImageFmtMode', c_uint8),       # enum format_mode
                ('u32TransLvl',    c_uint32),      # Uint32
               ]

    def asdict(camcfg):
        return {i: getattr(camcfg, i) for i in dir(camcfg) if not i.startswith('_') and not callable(getattr(camcfg, i))}


class ArduCamIndexinfo(Structure):
    """
    Structure used for retrieving scan information on camera. 
    """
    _fields_ = [('u8UsbIndex',     c_uint8),         # Uint8
                ('u8SerialNum',    c_uint8 * 16),    # Uint8[16]
               ]


# -- camera output data -- 
class ArduCamOutData(Structure):
    _fields_ = [('stImagePara',    ArduCamCfg),      # ArduCamCfg
                ('u64Time',        c_uint64),        # UInt64
                ('pu8ImageData',   POINTER(c_uint8)),        # Uint8*
               ]

# Probably not used
class Control(Structure):
    _fields_ = [('min',            c_int64),         # int64_t
                ('max',            c_int64 ),        # int64_t
                ('step',           c_int32),         # int32_t
                ('def',            c_int64),         # int64_t
                ('flags',          c_uint32),        # uint32_t
                ('name',           c_char * 128),    # char[128]
                ('func',           c_char * 128),    # char[128]
                ('code',           c_char_p),        # char* -- Python: bytes
               ]

### Functions to access camera, reordered in sections

## General Functions
def Py_ArduCam_scan():
    """
    C prototype:
      unsigned int ArduCam_scan(ArduCamIndexinfo *pstUsbIdxArray);
    """
    return

def Py_ArduCam_autoopen(cfg):
    """
    C prototype:
      unsigned int ArduCam_autoopen(ArduCamHandle &useHandle, ArduCamCfg *useCfg );
    """
    return

def Py_ArduCam_open(cfg, index=0):
    """
    C prototype:
      unsigned int ArduCam_open(ArduCamHandle &useHandle, ArduCamCfg* useCfg, Uint32 usbIdx );
    """
    return


def Py_ArduCam_close(handle):
    """
    C prototype:
      unsigned int ArduCam_close(ArduCamHandle useHandle);
    """
    return


def Py_ArduCam_getSensorCfg(handle):
    """
    C prototype:
      unsigned int ArduCam_getSensorCfg(ArduCamHandle useHandle, ArduCamCfg* useCfg );
    """
    return


def Py_ArduCam_setCamCfg(handle, cfg):
    """
    Not in C API, but present in Python API; not documented.
    Possibly closes camera and opens it back qith new configuration, but that changes the handle.
    """
    raise NotImplementedError("This function is not implemented in the C API.")
    return 


## Image Capture Functions
def Py_ArduCam_beginCaptureImage(handle):
    """
    C prototype:
      unsigned int ArduCam_beginCaptureImage(ArduCamHandle useHandle);
    """
    return

def Py_ArduCam_captureImage(handle):
    """
    C prototype:
      unsigned int ArduCam_captureImage(ArduCamHandle useHandle);
    """
    return

def Py_ArduCam_endCaptureImage(handle):
    """
    C prototype:
      unsigned int ArduCam_endCaptureImage(ArduCamHandle useHandle);
    """
    return


## Image Read Functions
def Py_ArduCam_availableImage(handle):
    """
    C prototype:
      unsigned int ArduCam_availableImage(ArduCamHandle useHandle);
    """
    return

def Py_ArduCam_readImage(handle):
    """
    C prototype:
      unsigned int ArduCam_readImage(ArduCamHandle useHandle, ArduCamOutData* &pstFrameData);
    """
    return


def Py_ArduCam_del(handle):
    """
    C prototype:
      unsigned int ArduCam_del(ArduCamHandle useHandle);
    """
    return

def Py_ArduCam_flush(handle):
    """
    C prototype:
      unsigned int ArduCam_flush(ArduCamHandle useHandle);
    """
    return



## Register Access Functions
def Py_ArduCam_writeSensorReg(handle, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeSensorReg( ArduCamHandle useHandle, Uint32 regAddr,  Uint32 val );
    """
    return

def Py_ArduCam_readSensorReg(handle, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readSensorReg( ArduCamHandle useHandle, Uint32 regAddr,  Uint32* pval );
    """
    return

# TODO: Check these functions with examples
def Py_ArduCam_writeReg_8_8(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    return
    
def Py_ArduCam_readReg_8_8(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    return
    
def Py_ArduCam_writeReg_8_16(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    return

def Py_ArduCam_readReg_8_16(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_8_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    return
    

def Py_ArduCam_writeReg_16_8(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    return
    
def Py_ArduCam_readReg_16_8(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    return
    
def Py_ArduCam_writeReg_16_16(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    return
    
def Py_ArduCam_readReg_16_16(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    return
    
def Py_ArduCam_writeReg_16_32(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_32( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    return
   
def Py_ArduCam_readReg_16_32(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_32( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    return


## ??? Not in SDK API description. 
def ArduCam_setForceOutput(handle, value):
    """
    C prototype:
      void ArduCam_setForceOutput( ArduCamHandle useHandle, bool value);
    """
    return

def Py_ArduCam_enableForceRead(handle):
    """
    C prototype:
      void ArduCam_enableForceRead( ArduCamHandle useHandle );
    """
    return

def Py_ArduCam_disableForceRead():
    """
    C prototype:
      void ArduCam_disableForceRead( ArduCamHandle useHandle );
    """
    return


## Configuration Functions
def Py_ArduCam_setboardConfig(handle, u8Command, u16Value, u16Index, u32BufSize, data):
    """
    C prototype:
      unsigned int ArduCam_setboardConfig( ArduCamHandle useHandle, Uint8 u8Command, Uint16 u16Value, Uint16 u16Index, Uint32 u32BufSize, Uint8 *pu8Buf );
    """
    return

def Py_ArduCam_getboardConfig(handle, u8Command, u16Value, u16Index, u32BufSize):
    """
    C prototype:
      unsigned int ArduCam_getboardConfig( ArduCamHandle useHandle, Uint8 u8Command, Uint16 u16Value, Uint16 u16Index, Uint32 u32BufSize, Uint8 *pu8Buf );
    """
    return



## User Data Access Functions
def Py_ArduCam_readUserData(handle, u16Addr, u8Len):
    """
    C prototype:
      unsigned int ArduCam_readUserData(  ArduCamHandle useHandle, Uint16 u16Addr, Uint8 u8Len, Uint8* pu8Data );
    """
    return

def Py_ArduCam_writeUserData(handle, u16Addr, u8Len, data ):
    """
    C prototype:
      unsigned int ArduCam_writeUserData( ArduCamHandle useHandle, Uint16 u16Addr, Uint8 u8Len, Uint8* pu8Data );
    """
    return


    
## External Trigger functions
#  NOT TESTED, MY SETUP DOES NOT SUPPORT IT
def Py_ArduCam_setMode(handle, mode):
    """
    C prototype:
      unsigned int ArduCam_setMode(       ArduCamHandle useHandle, int mode);
    """
    return

def Py_ArduCam_isFrameReady(handle):
    """
    C prototype:
      unsigned int ArduCam_isFrameReady(  ArduCamHandle useHandle);
    """
    return

def Py_ArduCam_softTrigger(handle):
    """
    C prototype:
      unsigned int ArduCam_softTrigger(   ArduCamHandle useHandle);
    """
    return

# Adapted from readImage, based on actual C prototype. The API documentation does not have parameter for the frame
def Py_ArduCam_getSingleFrame(handle, time_out = 1500):
    """
    C prototype:
      unsigned int ArduCam_getSingleFrame(ArduCamHandle useHandle, ArduCamOutData* &pstFrameData, int time_out = 1500);
    """
    return



## Controls Functions
# NOTE: These two functions are the only ones that return regular int instead of unsigned int
def Py_ArduCam_registerCtrls(handle, controls, controls_length):
    """
    C prototype:
      int ArduCam_registerCtrls(ArduCamHandle useHandle, Control *controls, Uint32 controls_length);
    """
    return

def Py_ArduCam_setCtrl(handle, func_name, val):
    """
    C prototype:
      int ArduCam_setCtrl(ArduCamHandle useHandle, const char *func_name, Int64 val);
    """
    return



