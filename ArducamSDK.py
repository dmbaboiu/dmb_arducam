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
    
    def __init__(camcfg, cfgdict=None):
        if(cfgdict is None):
            return
        for att in cfgdict:
            setattr(camcfg, att, cfgdict[att])

    def asdict(camcfg):
        return {i: getattr(camcfg, i) for i in dir(camcfg) if not i.startswith('_') and not callable(getattr(camcfg, i))}

    def __getitem__(camcfg, key):
        return getattr(camcfg, key)


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

    Scan USB for available cameras.
      unsigned int ArduCam_scan(ArduCamIndexinfo *pstUsbIdxArray);
    Returns:
      number of discovered cameras
      list with their indices
      list with their serial numbers (as bytes objects)
    The number of cameras is redundant, as it is implicit in the length of the lists, but is provided for completness.
    The original list for the C interface has a fixed length preallocated, with only camera_num populated (as in C),
    but the returned lists only have the valid entries.
    """
    scan = _libArduCam.ArduCam_scan
    scan.argtypes = [POINTER(ArduCamIndexinfo * 16)]
    scan.restype  = c_uint
    pUsbIdxArray = (ArduCamIndexinfo * 16)()
    camera_num  = scan(byref(pUsbIdxArray));
    index_list  = [pUsbIdxArray[cam_idx].u8UsbIndex for cam_idx in range(camera_num)]
    serial_list = [bytes(pUsbIdxArray[cam_idx].u8SerialNum) for cam_idx in range(camera_num)]
    return camera_num, index_list, serial_list


def Py_ArduCam_autoopen(cfg):
    """
    C prototype:
      unsigned int ArduCam_autoopen(ArduCamHandle &useHandle, ArduCamCfg *useCfg );
    """
    ardu_autoopen = _libArduCam.ArduCam_autoopen
    ardu_autoopen.argtypes = [POINTER(c_ulonglong), POINTER(ArduCamCfg)]
    ardu_autoopen.restype  = c_uint
    handle = c_ulonglong()
    camcfg = ArduCamCfg(cfg)
    err_code = ardu_autoopen(handle, camcfg)
    return err_code, handle, camcfg.asdict()


def Py_ArduCam_open(cfg, index=0):
    """
    C prototype:
      unsigned int ArduCam_open(ArduCamHandle &useHandle, ArduCamCfg* useCfg, Uint32 usbIdx );
    """
    ardu_open = _libArduCam.ArduCam_open
    ardu_open.argtypes = [POINTER(c_ulonglong), POINTER(ArduCamCfg), c_uint32]
    ardu_open.restype  = c_uint
    handle = c_ulonglong()
    camcfg = ArduCamCfg(cfg)
    err_code = ardu_open(handle, camcfg, index)
    return err_code, handle, camcfg.asdict()


def Py_ArduCam_close(handle):
    """
    C prototype:
      unsigned int ArduCam_close(ArduCamHandle useHandle);
    """
    ardu_close = _libArduCam.ArduCam_close
    ardu_close.argtypes = [c_ulonglong]
    ardu_close.restype  = c_uint
    err_code = ardu_close(handle)
    return err_code


def Py_ArduCam_getSensorCfg(handle):
    """
    C prototype:
      unsigned int ArduCam_getSensorCfg(ArduCamHandle useHandle, ArduCamCfg* useCfg );
    """
    ardu_getSensorCfg = _libArduCam.ArduCam_getSensorCfg
    ardu_getSensorCfg.argtypes = [c_ulonglong, POINTER(ArduCamCfg)]
    ardu_getSensorCfg.restype  = c_uint
    camcfg = ArduCamCfg()
    err_code = ardu_getSensorCfg(handle, camcfg)
    return err_code, camcfg.asdict()


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
    ardu_beginCapture = _libArduCam.ArduCam_beginCaptureImage
    ardu_beginCapture.argtypes = [c_ulonglong]
    ardu_beginCapture.restype  = c_uint
    err_code = ardu_beginCapture(handle)
    return err_code

def Py_ArduCam_captureImage(handle):
    """
    C prototype:
      unsigned int ArduCam_captureImage(ArduCamHandle useHandle);
    """
    ardu_Capture = _libArduCam.ArduCam_captureImage
    ardu_Capture.argtypes = [c_ulonglong]
    ardu_Capture.restype  = c_uint
    err_code = ardu_Capture(handle)
    return err_code

def Py_ArduCam_endCaptureImage(handle):
    """
    C prototype:
      unsigned int ArduCam_endCaptureImage(ArduCamHandle useHandle);
    """
    ardu_endCapture = _libArduCam.ArduCam_endCaptureImage
    ardu_endCapture.argtypes = [c_ulonglong]
    ardu_endCapture.restype  = c_uint
    err_code = ardu_endCapture(handle)
    return err_code


## Image Read Functions
def Py_ArduCam_availableImage(handle):
    """
    C prototype:
      unsigned int ArduCam_availableImage(ArduCamHandle useHandle);
    """
    ardu_available = _libArduCam.ArduCam_availableImage
    ardu_available.argtypes = [c_ulonglong]
    ardu_available.restype  = c_uint
    err_code = ardu_available(handle)
    return err_code

def Py_ArduCam_readImage(handle):
    """
    C prototype:
      unsigned int ArduCam_readImage(ArduCamHandle useHandle, ArduCamOutData* &pstFrameData);

    The `* &` in the prototype is a C++ reference to a pointer. In the underlying C ABI used by `ctypes`,
    a reference to a pointer behaves exactly like a pointer to a pointer (`ArducamOutData**`)
    
    The API does not mention any allocation/deallocation of data. I assume that the memory is fully allocated
    by the underlying library, returns a handle to it, and deallocates it on close.
    """
    ardu_read = _libArduCam.ArduCam_readImage
    ardu_read.argtypes = [c_ulonglong, POINTER(POINTER(ArduCamOutData))]
    ardu_read.restype  = c_uint
    outData = POINTER(ArduCamOutData)()
    err_code = ardu_read(handle, outData)
    if outData:
        cfg_dict = outData.contents.stImagePara.asdict()
        cfg_dict['u64Time'] = outData.contents.u64Time
        # `data` is to be converted to memoryview, for compatibility with standard interface and flexibility
        pythonapi.PyMemoryView_FromMemory.argtypes = [c_char_p, c_ssize_t, c_int]
        pythonapi.PyMemoryView_FromMemory.restype = py_object
        data = pythonapi.PyMemoryView_FromMemory(cast(outData.contents.pu8ImageData, c_char_p), cfg_dict['u32Size'], 0x200)
        return err_code, data, cfg_dict
    else:
        return None, None, None


def Py_ArduCam_del(handle):
    """
    C prototype:
      unsigned int ArduCam_del(ArduCamHandle useHandle);
    """
    ardu_del = _libArduCam.ArduCam_del
    ardu_del.argtypes = [c_ulonglong]
    ardu_del.restype  = c_uint
    err_code = ardu_del(handle)
    return err_code

def Py_ArduCam_flush(handle):
    """
    C prototype:
      unsigned int ArduCam_flush(ArduCamHandle useHandle);
    """
    ardu_flush = _libArduCam.ArduCam_flush
    ardu_flush.argtypes = [c_ulonglong]
    ardu_flush.restype  = c_uint
    err_code = ardu_flush(handle)
    return err_code



## Register Access Functions
def Py_ArduCam_writeSensorReg(handle, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeSensorReg( ArduCamHandle useHandle, Uint32 regAddr,  Uint32 val );
    """
    ardu_writeSensorReg = _libArduCam.ArduCam_writeSensorReg
    ardu_writeSensorReg.argtypes = [c_ulonglong, c_uint32, c_uint32]
    ardu_writeSensorReg.restype  = c_uint
    err_code = ardu_writeSensorReg(handle, regAddr, val)
    return err_code

def Py_ArduCam_readSensorReg(handle, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readSensorReg( ArduCamHandle useHandle, Uint32 regAddr,  Uint32* pval );
    """
    ardu_readSensorReg = _libArduCam.ArduCam_readSensorReg
    ardu_readSensorReg.argtypes = [c_ulonglong, c_uint32, POINTER(c_uint32)]
    ardu_readSensorReg.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readSensorReg(handle, regAddr, regValue)
    # err_code = ardu_readSensorReg(handle, regAddr, byref(regValue))
    return err_code, regValue.value


# TODO: Check these functions with examples
def Py_ArduCam_writeReg_8_8(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    ardu_writeReg_8_8 = _libArduCam.ArduCam_writeReg_8_8
    ardu_writeReg_8_8.argtypes = [c_ulonglong, c_uint32, c_uint32, c_uint32]
    ardu_writeReg_8_8.restype  = c_uint
    err_code = ardu_writeReg_8_8(handle, shipAddr, regAddr, val)
    return err_code
    
def Py_ArduCam_readReg_8_8(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    ardu_readReg_8_8 = _libArduCam.ArduCam_readReg_8_8
    ardu_readReg_8_8.argtypes = [c_ulonglong, c_uint32, c_uint32, POINTER(c_uint32)]
    ardu_readReg_8_8.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readReg_8_8(handle, shipAddr, regAddr, regValue)
    return err_code, regValue.value
    
def Py_ArduCam_writeReg_8_16(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_8_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    ardu_writeReg_8_16 = _libArduCam.ArduCam_writeReg_8_16
    ardu_writeReg_8_16.argtypes = [c_ulonglong, c_uint32, c_uint32, c_uint32]
    ardu_writeReg_8_16.restype  = c_uint
    err_code = ardu_writeReg_8_16(handle, shipAddr, regAddr, val)
    return err_code

def Py_ArduCam_readReg_8_16(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_8_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    ardu_readReg_8_16 = _libArduCam.ArduCam_readReg_8_16
    ardu_readReg_8_16.argtypes = [c_ulonglong, c_uint32, c_uint32, POINTER(c_uint32)]
    ardu_readReg_8_16.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readReg_8_16(handle, shipAddr, regAddr, regValue)
    return err_code, regValue.value
    

def Py_ArduCam_writeReg_16_8(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    ardu_writeReg_16_8 = _libArduCam.ArduCam_writeReg_16_8
    ardu_writeReg_16_8.argtypes = [c_ulonglong, c_uint32, c_uint32, c_uint32]
    ardu_writeReg_16_8.restype  = c_uint
    err_code = ardu_writeReg_16_8(handle, shipAddr, regAddr, val)
    return err_code
    
def Py_ArduCam_readReg_16_8(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_8( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    ardu_readReg_16_8 = _libArduCam.ArduCam_readReg_16_8
    ardu_readReg_16_8.argtypes = [c_ulonglong, c_uint32, c_uint32, POINTER(c_uint32)]
    ardu_readReg_16_8.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readReg_16_8(handle, shipAddr, regAddr, regValue)
    return err_code, regValue.value
    
def Py_ArduCam_writeReg_16_16(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );
    """
    ardu_writeReg_16_16 = _libArduCam.ArduCam_writeReg_16_16
    ardu_writeReg_16_16.argtypes = [c_ulonglong, c_uint32, c_uint32, c_uint32]
    ardu_writeReg_16_16.restype  = c_uint
    err_code = ardu_writeReg_16_16(handle, shipAddr, regAddr, val)
    return err_code
    
def Py_ArduCam_readReg_16_16(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_16( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    ardu_readReg_16_16 = _libArduCam.ArduCam_readReg_16_16
    ardu_readReg_16_16.argtypes = [c_ulonglong, c_uint32, c_uint32, POINTER(c_uint32)]
    ardu_readReg_16_16.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readReg_16_16(handle, shipAddr, regAddr, regValue)
    return err_code, regValue.value
    
def Py_ArduCam_writeReg_16_32(handle, shipAddr, regAddr, val):
    """
    C prototype:
      unsigned int ArduCam_writeReg_16_32( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32 val );

    """
    ardu_writeReg_16_32 = _libArduCam.ArduCam_writeReg_16_32
    ardu_writeReg_16_32.argtypes = [c_ulonglong, c_uint32, c_uint32, c_uint32]
    ardu_writeReg_16_32.restype  = c_uint
    err_code = ardu_writeReg_16_32(handle, shipAddr, regAddr, val)
    return err_code
   
def Py_ArduCam_readReg_16_32(handle, shipAddr, regAddr):
    """
    C prototype:
      unsigned int ArduCam_readReg_16_32( ArduCamHandle useHandle, Uint32 shipAddr, Uint32 regAddr, Uint32* pval );
    """
    ardu_readReg_16_32 = _libArduCam.ArduCam_readReg_16_32
    ardu_readReg_16_32.argtypes = [c_ulonglong, c_uint32, c_uint32, POINTER(c_uint32)]
    ardu_readReg_16_32.restype  = c_uint
    regValue = c_uint32()
    err_code = ardu_readReg_16_32(handle, shipAddr, regAddr, regValue)
    return err_code, regValue.value


## ??? Not in SDK API description. 
# This function sets the force capture flag for the Arducam camera.
# If force_capture is true, the camera will capture a frame even if some error occurs during the capture process.
# If force_capture is false, the camera will not.
# These three functions are the only ones with `void` return,
# NOTE: THIS SET IS NOT TESTED
def ArduCam_setForceOutput(handle, value):
    """
    C prototype:
      void ArduCam_setForceOutput( ArduCamHandle useHandle, bool value);

    Not implemented in original Python API
    """
    ardu_setForceOutput = _libArduCam.ArduCam_setForceOutput
    ardu_setForceOutput.argtypes = [c_ulonglong, c_bool]
    ardu_setForceOutput.restype  = None
    ardu_setForceOutput(handle, value)
    return

def Py_ArduCam_enableForceRead(handle):
    """
    C prototype:
      void ArduCam_enableForceRead( ArduCamHandle useHandle );
    """
    ardu_enableForceRead = _libArduCam.ArduCam_enableForceRead
    ardu_enableForceRead.argtypes = [c_ulonglong,]
    ardu_enableForceRead.restype  = None
    ardu_enableForceRead(handle, value)
    return

def Py_ArduCam_disableForceRead():
    """
    C prototype:
      void ArduCam_disableForceRead( ArduCamHandle useHandle );
    """
    ardu_disableForceRead = _libArduCam.ArduCam_disableForceRead
    ardu_disableForceRead.argtypes = [c_ulonglong,]
    ardu_disableForceRead.restype  = None
    ardu_disableForceRead(handle, value)
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



