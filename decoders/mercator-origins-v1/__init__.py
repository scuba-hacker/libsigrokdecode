##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2025 Mark Jones
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

'''
This decoder handles the Mercator Origins V1 telemetry protocol used for 
underwater navigation systems. The protocol transmits 114-byte messages 
containing various sensor readings including depth, water pressure, temperature,
humidity, navigation data, accelerometer readings, gyroscope data, and system 
status information.

The message format consists of:
- 57 x 16-bit words (114 bytes total)
- Little-endian byte order
- XOR checksum validation
- Float values packed as two consecutive 16-bit words

This decoder expects to receive UART data as input and will automatically 
detect and parse complete telemetry messages, performing checksum validation
and providing detailed field-by-field annotations.
'''

from .pd import Decoder