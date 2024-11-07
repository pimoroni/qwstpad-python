from collections import OrderedDict

__version__ = '0.0.1'

# Constants
NUM_LEDS = 4
NUM_BUTTONS = 10

DEFAULT_ADDRESS = 0x21
ALT_ADDRESS_1 = 0x23
ALT_ADDRESS_2 = 0x25
ALT_ADDRESS_3 = 0x27
ADDRESSES = (DEFAULT_ADDRESS, ALT_ADDRESS_1, ALT_ADDRESS_2, ALT_ADDRESS_3)


class QwSTPad:
    # Registers
    INPUT_PORT0 = 0x00
    INPUT_PORT1 = 0x01
    OUTPUT_PORT0 = 0x02
    OUTPUT_PORT1 = 0x03
    POLARITY_PORT0 = 0x04
    POLARITY_PORT1 = 0x05
    CONFIGURATION_PORT0 = 0x06
    CONFIGURATION_PORT1 = 0x07

    # Mappings
    BUTTON_MAPPING = OrderedDict({'A': 0xE, 'B': 0xC, 'X': 0xF, 'Y': 0xD,
                                  'U': 0x1, 'D': 0x4, 'L': 0x2, 'R': 0x3,
                                  '+': 0xB, '-': 0x5})

    LED_MAPPING = (0x6, 0x7, 0x9, 0xA)

    def __init__(self, i2c=None, address=DEFAULT_ADDRESS):
        self.__i2c = i2c

        if self.__i2c is None:
            import smbus2
            self.__i2c = smbus2.SMBus(1)

        if address not in ADDRESSES:
            raise ValueError("address is not valid. Expected: 0x21, 0x23, 0x25, or 0x27")

        self.__address = address

        # Set up the TCA9555 with the correct input and output pins
        self.__i2c.write_word_data(self.__address, self.CONFIGURATION_PORT0, 0b11111001_00111111)
        self.__i2c.write_word_data(self.__address, self.POLARITY_PORT0, 0b11111000_00111111)
        self.__i2c.write_word_data(self.__address, self.OUTPUT_PORT0, 0b00000110_11000000)

        self.__button_states = OrderedDict({})
        for key, _ in self.BUTTON_MAPPING.items():
            self.__button_states[key] = False

        self.__led_states = 0b0000
        self.set_leds_from_addr()

    def address_code(self):
        return self.__change_bit(0x0000, ADDRESSES.index(self.__address), True)

    def read_buttons(self):
        state = self.__i2c.read_word_data(self.__address, self.INPUT_PORT0)
        for key, value in self.BUTTON_MAPPING.items():
            self.__button_states[key] = self.__get_bit(state, value)
        return self.__button_states

    def set_leds(self, states):
        self.__led_states = states & 0b1111
        self.__update_leds()

    def set_leds_from_addr(self):
        self.__led_states = self.__change_bit(0b0000, ADDRESSES.index(self.__address), True)
        self.__update_leds()

    def set_led(self, led, state):
        if led < 1 or led > NUM_LEDS:
            raise ValueError(f"'led' out of range. Expected 1 to {NUM_LEDS}")

        self.__led_states = self.__change_bit(self.__led_states, led - 1, state)
        self.__update_leds()

    def clear_leds(self):
        self.__led_states = 0b0000
        self.__update_leds()

    def __update_leds(self):
        output = 0
        for i in range(NUM_LEDS):
            output = self.__change_bit(output, self.LED_MAPPING[i], not self.__get_bit(self.__led_states, i))
        self.__i2c.write_word_data(self.__address, self.OUTPUT_PORT0, output)

    def __get_bit(self, num, bit_pos):
        return (num & (1 << bit_pos)) != 0

    def __change_bit(self, num, bit_pos, state):
        return num | (1 << bit_pos) if state else num & ~(1 << bit_pos)
