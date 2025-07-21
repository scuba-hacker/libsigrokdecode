
import sigrokdecode as srd
import struct

'''
Mercator Origins V1 Telemetry Protocol Decoder

This decoder handles the 114-byte telemetry messages sent from the Mako system
to the Lemon system via UART. The message format contains:
- 57 x 16-bit words (114 bytes total)
- Various sensor readings, navigation data, and system status
- XOR checksum validation
'''

class Decoder(srd.Decoder):
    api_version = 3
    id = 'mercator-origins-v1'
    name = 'Mercator Origins V1'
    longname = 'Mercator Origins V1 Telemetry Protocol'
    desc = 'Mercator Origins underwater navigation telemetry protocol.'
    license = 'gplv2+'
    inputs = ['uart']
    outputs = ['mercator-origins-v1']
    tags = ['embedded/industrial', 'sensor']
    
    annotations = (
        ('message', 'Complete message'),
        ('length', 'Message length'),
        ('msgtype', 'Message type'),
        ('depth', 'Water depth'),
        ('water_pressure', 'Water pressure'),
        ('water_temperature', 'Water temperature'),
        ('enclosure_temperature', 'Enclosure temperature'),
        ('enclosure_humidity', 'Enclosure humidity'),
        ('air_pressure', 'Air pressure'),
        ('heading', 'Magnetic heading'),
        ('heading_to_target', 'Heading to target'),
        ('distance_to_target', 'Distance to target'),
        ('journey_course', 'Journey course'),
        ('journey_distance', 'Journey distance'),
        ('display_label', 'Display label'),
        ('mako_seconds_on', 'Mako seconds on'),
        ('mako_user_action', 'Mako user action'),
        ('mako_bad_checksum_msgs', 'Bad checksum messages'),
        ('mako_usb_voltage', 'USB voltage'),
        ('mako_usb_current', 'USB current'),
        ('target_code', 'Target code'),
        ('sensor_timing', 'Sensor timing data'),
        ('accelerometer', 'Accelerometer data'),
        ('gyroscope', 'Gyroscope data'),
        ('linear_acceleration', 'Linear acceleration'),
        ('rotational_acceleration', 'Rotational acceleration'),
        ('mako_good_checksum_msgs', 'Good checksum messages'),
        ('waymarker', 'Waymarker data'),
        ('waymarker_label', 'Waymarker label'),
        ('direction_metric_label', 'Direction metric label'),
        ('flags', 'Status flags'),
        ('checksum', 'Message checksum'),
        ('checksum_ok', 'Checksum valid'),
        ('checksum_error', 'Checksum error'),
    )
    
    annotation_rows = (
        ('fields', 'Message fields', tuple(range(len(annotations)))),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = b''
        self.expected_length = None
        self.start_sample = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def calc_checksum(self, data):
        checksum = 0
        words = len(data) // 2
        for i in range(words):
            word = struct.unpack('<H', data[i*2:(i*2)+2])[0]
            checksum ^= word
        return checksum

    def decode_float_from_words(self, word1, word2):
        bytes_data = struct.pack('<HH', word1, word2)
        return struct.unpack('<f', bytes_data)[0]

    def decode_message(self, data, ss, es):
        if len(data) < 114:
            return
            
        words = struct.unpack('<57H', data[:114])
        
        length = words[0]
        self.put(ss, es, self.out_ann, [1, [f'Length: {length} bytes']])
        
        msgtype = words[1]
        self.put(ss, es, self.out_ann, [2, [f'Message Type: {msgtype}']])
        
        depth = words[2] / 10.0
        self.put(ss, es, self.out_ann, [3, [f'Depth: {depth:.1f}m']])
        
        water_pressure = words[3] / 100.0
        self.put(ss, es, self.out_ann, [4, [f'Water Pressure: {water_pressure:.2f}']])
        
        water_temp = words[4] / 10.0
        self.put(ss, es, self.out_ann, [5, [f'Water Temp: {water_temp:.1f}°C']])
        
        enclosure_temp = words[5] / 10.0
        self.put(ss, es, self.out_ann, [6, [f'Enclosure Temp: {enclosure_temp:.1f}°C']])
        
        enclosure_humidity = words[6] / 10.0
        self.put(ss, es, self.out_ann, [7, [f'Humidity: {enclosure_humidity:.1f}%']])
        
        air_pressure = words[7] / 10.0
        self.put(ss, es, self.out_ann, [8, [f'Air Pressure: {air_pressure:.1f}']])
        
        heading = words[8] / 10.0
        self.put(ss, es, self.out_ann, [9, [f'Heading: {heading:.1f}°']])
        
        heading_to_target = words[9] / 10.0
        self.put(ss, es, self.out_ann, [10, [f'Heading to Target: {heading_to_target:.1f}°']])
        
        distance_to_target = words[10] / 10.0
        self.put(ss, es, self.out_ann, [11, [f'Distance to Target: {distance_to_target:.1f}m']])
        
        journey_course = words[11] / 10.0
        self.put(ss, es, self.out_ann, [12, [f'Journey Course: {journey_course:.1f}°']])
        
        journey_distance = words[12] / 100.0
        self.put(ss, es, self.out_ann, [13, [f'Journey Distance: {journey_distance:.2f}m']])
        
        display_label = chr(words[13] & 0xFF) + chr((words[13] >> 8) & 0xFF)
        self.put(ss, es, self.out_ann, [14, [f'Display: "{display_label}"']])
        
        mako_seconds_on = words[14]
        self.put(ss, es, self.out_ann, [15, [f'Uptime: {mako_seconds_on} min']])
        
        mako_user_action = words[15]
        self.put(ss, es, self.out_ann, [16, [f'User Action: {mako_user_action}']])
        
        bad_checksum_msgs = words[16]
        self.put(ss, es, self.out_ann, [17, [f'Bad Checksums: {bad_checksum_msgs}']])
        
        usb_voltage = words[17] / 1000.0
        self.put(ss, es, self.out_ann, [18, [f'USB Voltage: {usb_voltage:.3f}V']])
        
        usb_current = words[18] / 100.0
        self.put(ss, es, self.out_ann, [19, [f'USB Current: {usb_current:.2f}A']])
        
        target_code = chr(words[19] & 0xFF) + chr((words[19] >> 8) & 0xFF) + chr(words[20] & 0xFF) + chr((words[20] >> 8) & 0xFF)
        self.put(ss, es, self.out_ann, [20, [f'Target: "{target_code}"']])
        
        sensor_timings = [words[21], words[22], words[23], words[24], words[25], words[26]]
        self.put(ss, es, self.out_ann, [21, [f'Sensor Timing: {sensor_timings}']])
        
        acc_x = self.decode_float_from_words(words[27], words[28])
        acc_y = self.decode_float_from_words(words[29], words[30])
        acc_z = self.decode_float_from_words(words[31], words[32])
        self.put(ss, es, self.out_ann, [22, [f'Accel: X={acc_x:.3f}, Y={acc_y:.3f}, Z={acc_z:.3f}']])
        
        gyro_x = self.decode_float_from_words(words[33], words[34])
        gyro_y = self.decode_float_from_words(words[35], words[36])
        gyro_z = self.decode_float_from_words(words[37], words[38])
        self.put(ss, es, self.out_ann, [23, [f'Gyro: X={gyro_x:.3f}, Y={gyro_y:.3f}, Z={gyro_z:.3f}']])
        
        lin_acc_x = self.decode_float_from_words(words[39], words[40])
        lin_acc_y = self.decode_float_from_words(words[41], words[42])
        lin_acc_z = self.decode_float_from_words(words[43], words[44])
        self.put(ss, es, self.out_ann, [24, [f'Lin Accel: X={lin_acc_x:.3f}, Y={lin_acc_y:.3f}, Z={lin_acc_z:.3f}']])
        
        rot_acc_x = self.decode_float_from_words(words[45], words[46])
        rot_acc_y = self.decode_float_from_words(words[47], words[48])
        rot_acc_z = self.decode_float_from_words(words[49], words[50])
        self.put(ss, es, self.out_ann, [25, [f'Rot Accel: X={rot_acc_x:.3f}, Y={rot_acc_y:.3f}, Z={rot_acc_z:.3f}']])
        
        good_checksum_msgs = words[51]
        self.put(ss, es, self.out_ann, [26, [f'Good Checksums: {good_checksum_msgs}']])
        
        waymarker = words[52]
        self.put(ss, es, self.out_ann, [27, [f'Waymarker: {waymarker}']])
        
        waymarker_label = chr(words[53] & 0xFF) + chr((words[53] >> 8) & 0xFF)
        self.put(ss, es, self.out_ann, [28, [f'Waymarker Label: "{waymarker_label}"']])
        
        direction_metric_label = chr(words[54] & 0xFF) + chr((words[54] >> 8) & 0xFF)
        self.put(ss, es, self.out_ann, [29, [f'Direction Metric: "{direction_metric_label}"']])
        
        flags = words[55]
        self.put(ss, es, self.out_ann, [30, [f'Flags: 0x{flags:04X}']])
        
        received_checksum = words[56]
        calculated_checksum = self.calc_checksum(data[:112])
        checksum_valid = received_checksum == calculated_checksum
        
        if checksum_valid:
            self.put(ss, es, self.out_ann, [32, [f'Checksum OK: 0x{received_checksum:04X}']])
        else:
            self.put(ss, es, self.out_ann, [33, [f'Checksum ERROR: got 0x{received_checksum:04X}, expected 0x{calculated_checksum:04X}']])
        
        self.put(ss, es, self.out_ann, [0, [f'Mercator Origins V1 Message (Length: {length}, Type: {msgtype}, Checksum: {"OK" if checksum_valid else "ERROR"})']])

    def decode(self):
        while True:
            _, data = self.wait({'FRAME': ['D', 'DATA']})
            
            if self.start_sample is None:
                self.start_sample = self.samplenum
            
            if data['DATA'][0] is not None:
                byte_val = data['DATA'][0]
                self.buffer += bytes([byte_val])
                
                if self.expected_length is None and len(self.buffer) >= 2:
                    self.expected_length = struct.unpack('<H', self.buffer[:2])[0]
                
                if self.expected_length and len(self.buffer) >= self.expected_length:
                    self.decode_message(self.buffer, self.start_sample, self.samplenum)
                    self.buffer = b''
                    self.expected_length = None
                    self.start_sample = None
