
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
    * Cause: Requesting a frame size, mode, or pixel format that the active camera firmware or configuration preset does not support.
    * Fix: Check your initialization script or GUI settings. Ensure the resolution and color format match the exact parameters defined in your config file.
 * Capture Thread Interruption / Timing Issues
    * Cause: Stopping, restarting, or overlapping the frame capture thread too quickly causes the SDK to lose track of the active buffer index.
    * Fix: Keep the continuous capture loop running stable without abruptly killing and re-initializing the capture instance on every single frame.
 * USB Bandwidth or Connection Faults
    * Cause: Dropped packets or slow bus transfer speeds (especially on high-resolution or high-framerate USB 3.0/2.0 cameras) desynchronize the frame counter.
    * Fix: Connect directly to a native USB port (avoid passive hubs), use a shorter or high-quality shielded USB cable, and lower the framerate or resolution to test stability.
 