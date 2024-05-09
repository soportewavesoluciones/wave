DIST_LOW =                  0x00   # cm
DIST_HIGH =                 0x01
AMP_LOW =                   0x02
AMP_HIGH =                  0x03
TEMP_LOW =                  0x04   # Unit: 0.01 Celsius
TEMP_HIGH =                 0x05
TICK_LOW =                  0x06   # Timestamp
TICK_HIGH =                 0x07
ERROR_LOW =                 0x08
ERROR_HIGH =                0x09
VERSION_REVISION =          0x0A
VERSION_MINOR =             0x0B
VERSION_MAJOR =             0x0C
SN =                        0x10    # Production code in 14 bytes ASCI code (0x10 is the first byte)
SAVE =                      0x20    # Write 0x01 to save current setting
SHUTDOWN_REBOOT =           0x21    # Write 0x02 to reboot
SLAVE_ADDR =                0x22    # Default: 0x10, Range: [0x08, 0x77]
MODE =                      0x23    # Default: 0x00 | Continuous ranging mode: 0x00  Trigger mode: 0x01
TRIG_ONE_SHOT =             0x24    # 0x01: Trigger once (only on trigger mode)
ENABLE =                    0x25    # Turn on LiDAR: 0x00, Turn off LiDAR: 0x01
FPS_LOW =                   0x26    # Default: 0x64 100Hz, 0xFA 250Hz
FPS_HIGH =                  0x27
LOW_POWER =                 0x28    # Default: 0x00, Normal: 0x00, Power saving mode: 0x01
RESTORE_FACTORY_DEFAULTS =  0x29    # Write 0x01 to restore factory default settings
AMP_THR_LOW =               0x2A    # Default: 0x64, Amp threshold value
MIN_DIST_LOW =              0x2E    # Default: 0x00, Minimum dist in cm, but not working on DUMMY_DIST
MIN_DIST_HIGH =             0x2F    # Default: 0x00
MAX_DIST_LOW =              0x30    # Default: 0x20, Maximum dist in cm, but not working on DUMMY_DIST
MAX_DIST_HIGH =             0x31    # Default: 0x03