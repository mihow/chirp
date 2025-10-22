# Copyright 2025 CHIRP Contributors
# Based on radtel_rt900.py driver
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Radtel RT-880 (Also known as iRadio UV-98) radio driver

This driver is based on the Radtel RT-900 driver structure and provides
initial support for the RT-880 / iRadio UV-98 mobile radio.

IMPORTANT NOTES FOR TESTING:
----------------------------
This driver has been created based on the RT-900 structure but has not been
tested with actual RT-880 hardware. The following parameters are placeholders
and will need to be verified/updated when tested with an actual radio:

1. Magic bytes (_magic): Used to initiate programming mode
2. Fingerprint strings (_fingerprint, _fingerprint2): Used to identify radio
3. Channel count (_upper): Currently set to 999, may be different
4. Memory ranges (_ranges): Memory map structure
5. Power levels: Currently set to 8W/4W/1W, verify with actual specs
6. Feature flags: Bluetooth, noise reduction, AM support, etc.

To test and update this driver:
-------------------------------
1. Connect RT-880 radio via programming cable
2. Attempt download - if it fails, capture the identification strings
3. Update _magic, _fingerprint, and _fingerprint2 with correct values
4. Save a test image file as tests/images/Radtel_RT-880.img
5. Verify channel count, power levels, and features match radio capabilities
6. Update this documentation once verified

The RT-880 may share protocol with RT-900, or it may use a different
communication protocol. The protocol document referenced in the issue
(https://github.com/rampa069/RT880-misc/blob/main/Protocol.md) appears
to be for firmware flashing and may not be directly applicable to
memory programming.
"""

import logging

from chirp import chirp_common, directory
from chirp.drivers import radtel_rt900

LOG = logging.getLogger(__name__)


@directory.register
class RT880(radtel_rt900.RT900BT):
    """Radtel RT-880 / iRadio UV-98

    This driver inherits from RT900BT and uses its communication protocol
    and memory structure. The RT-880 appears to be related to the RT-900
    series of mobile radios.

    TESTING REQUIRED: This driver needs verification with actual hardware.
    """
    VENDOR = "Radtel"
    MODEL = "RT-880"

    # Channel Configuration
    # NOTE: Verify actual channel count with real radio
    # Could be 128, 256, 512, or 999 channels
    _upper = 999  # Number of channels
    _mem_params = (_upper,)

    # Programming Protocol Identification
    # NOTE: These values are inherited from RT-900 and need verification
    # When testing fails, capture actual values returned by radio
    _magic = b"PROGRAMBT80U"  # Initial handshake string

    # Radio identification fingerprints
    # NOTE: Update these with actual values from RT-880
    # First fingerprint is checked during initial connection
    _fingerprint = [
        b"\x01\x36\x01\x80\x04\x00\x05\x20",  # From RT-900, needs verification
    ]
    # Second fingerprint is checked after encryption setup
    _fingerprint2 = [
        b"\x02\x00\x02\x60\x01\x03\x30\x04",  # From RT-900, needs verification
    ]

    # Power Level Configuration
    # NOTE: Verify actual power output specifications
    # RT-880 specs may differ from RT-900
    POWER_LEVELS = [
        chirp_common.PowerLevel("High", watts=8.00),
        chirp_common.PowerLevel("Middle", watts=4.00),
        chirp_common.PowerLevel("Low", watts=1.00)
    ]

    # Frequency Band Configuration
    # NOTE: Verify actual frequency range supported by RT-880
    # May be more restricted than the wide range shown here
    VALID_BANDS = [(18000000, 1000000000)]

    # Feature Availability Flags
    # NOTE: Verify which features RT-880 actually supports
    _has_bt_denoise = True      # Bluetooth and noise reduction
    _has_am_per_channel = True  # Per-channel AM mode
    _has_am_switch = not _has_am_per_channel  # Global AM mode switch
    _has_single_mode = True     # Single channel display mode

    @classmethod
    def get_prompts(cls):
        rp = chirp_common.RadioPrompts()
        rp.experimental = (
            'This driver is experimental for the Radtel RT-880 '
            '(also known as iRadio UV-98).\n'
            '\n'
            'Please save an unedited copy of your first successful\n'
            'download to a CHIRP Radio Images(*.img) file.\n\n'
            'PROCEED AT YOUR OWN RISK!'
        )
        rp.pre_download = (
            "1. Turn radio off.\n"
            "2. Connect cable to mic/spkr connector.\n"
            "3. Make sure connector is firmly connected.\n"
            "4. Turn radio on (volume may need to be set at 100%).\n"
            "5. Ensure that the radio is tuned to channel with no activity.\n"
            "6. Click OK to download image from device."
        )
        rp.pre_upload = (
            "1. Turn radio off.\n"
            "2. Connect cable to mic/spkr connector.\n"
            "3. Make sure connector is firmly connected.\n"
            "4. Turn radio on (volume may need to be set at 100%).\n"
            "5. Ensure that the radio is tuned to channel with no activity.\n"
            "6. Click OK to upload image to device."
        )
        return rp


@directory.register
class iRadioUV98(RT880):
    """iRadio UV-98 (Alternate branding of RT-880)"""
    VENDOR = "iRadio"
    MODEL = "UV-98"

    # Same as RT880 but with different vendor/model name
    # All functionality inherited from RT880 class
