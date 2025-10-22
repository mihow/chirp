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

"""Radtel RT-880 (Also known as iRadio UV-98) radio driver"""

import logging

from chirp import chirp_common, directory
from chirp.drivers import radtel_rt900

LOG = logging.getLogger(__name__)


@directory.register
class RT880(radtel_rt900.RT900BT):
    """Radtel RT-880 / iRadio UV-98"""
    VENDOR = "Radtel"
    MODEL = "RT-880"
    
    # RT-880 is similar to RT-900 series but may have different:
    # - fingerprint/magic bytes for identification
    # - memory size and channel count
    # - power levels
    # - feature availability
    
    # These will need to be updated based on actual RT-880 specifications
    # For now, using RT-900 BT as base with potential differences
    
    _upper = 999  # Number of channels - may need adjustment
    _mem_params = (_upper,)
    
    # Magic string for RT-880 - needs to be determined from actual radio
    # This is a placeholder and should be updated
    _magic = b"PROGRAMBT80U"  # May be different for RT-880
    
    # Fingerprint strings - these identify the radio model
    # These are placeholders and need to be updated with actual RT-880 values
    _fingerprint = [
        b"\x01\x36\x01\x80\x04\x00\x05\x20",  # Placeholder
    ]
    _fingerprint2 = [
        b"\x02\x00\x02\x60\x01\x03\x30\x04",  # Placeholder
    ]
    
    # Power levels for RT-880 - may differ from RT-900
    POWER_LEVELS = [
        chirp_common.PowerLevel("High", watts=8.00),
        chirp_common.PowerLevel("Middle", watts=4.00),
        chirp_common.PowerLevel("Low", watts=1.00)
    ]
    
    # Frequency bands supported by RT-880
    VALID_BANDS = [(18000000, 1000000000)]
    
    # Feature flags - adjust based on RT-880 capabilities
    _has_bt_denoise = True
    _has_am_per_channel = True
    _has_am_switch = not _has_am_per_channel
    _has_single_mode = True
    
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
