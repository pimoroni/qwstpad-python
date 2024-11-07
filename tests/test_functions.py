TEST_STEP_COUNT = 1365


def test_address_code(smbus, qwstpad):
    dev = smbus.SMbus(1)
    pad = qwstpad.QwSTPad(i2c=dev, address=qwstpad.ALT_ADDRESS_1)

    address = pad.address_code()

    assert True if address == 2 else False


def test_read_buttons(smbus, qwstpad):
    dev = smbus.SMbus(1)

    INPUT_PORT0 = 0x00
    INPUT_PORT1 = 0x01

    dev.regs[INPUT_PORT0] = 0b00000000
    dev.regs[INPUT_PORT1] = 0b00000000

    pad = qwstpad.QwSTPad(dev)

    buttons = pad.read_buttons()

    for key, value in buttons.items():
        print(f"{key} = {value:n}", end=", ")

    assert False
