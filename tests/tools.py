from i2cdevice import MockSMBus
import struct

I2C_SMBUS = 0x0720
I2C_SMBUS_BYTE_DATA = 2
I2C_SMBUS_WRITE = 0
I2C_SLAVE = 0x0703  # Use this slave address
I2C_SLAVE_FORCE = 0x0706  # Use this slave address, even if it is already in use by a driver!


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus)

    def write_byte_data(self, i2c_addr, register, value):
        self.regs[register] = value

    def read_word_data(self, i2c_addr, register):
        return self.regs[register]

    def write_word_data(self, i2c_addr, register, value):
        self.regs[register] = value
