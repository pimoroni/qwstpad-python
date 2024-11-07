def test_address_code(smbus, qwstpad):
    dev = smbus.SMBus(1)
    pad = qwstpad.QwSTPad(i2c=dev, address=qwstpad.ALT_ADDRESS_1)

    address = pad.address_code()

    assert True if address == 2 else False


def test_read_buttons(smbus, qwstpad):
    dev = smbus.SMBus(1)

    # Set the bits for button UP and X
    dev.regs[0x00] = (1 << 0x01) | (1 << 0xF)

    pad = qwstpad.QwSTPad(dev)

    buttons = pad.read_buttons()

    assert buttons['X'] == 1 and buttons['U'] == 1


def test_config_port(smbus, qwstpad):
    dev = smbus.SMBus(1)
    qwstpad.QwSTPad(dev)

    assert dev.regs[0x06] == 0b1111100100111111


def test_polarity_port(smbus, qwstpad):
    dev = smbus.SMBus(1)
    qwstpad.QwSTPad(dev)

    assert dev.regs[0x04] == 0b1111100000111111


def test_output_port(smbus, qwstpad):
    dev = smbus.SMBus(1)
    pad = qwstpad.QwSTPad(dev)

    pad.clear_leds()

    assert dev.regs[0x02] == 0b0000011011000000


def test_set_led(smbus, qwstpad):
    dev = smbus.SMBus(1)
    pad = qwstpad.QwSTPad(dev)

    pad.clear_leds()

    led_2_value = 0b0000011011000000 & ~(1 << 7)

    pad.set_led(2, True)

    assert led_2_value == dev.regs[0x02]
