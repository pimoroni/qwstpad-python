import time
from qwstpad import ADDRESSES, QwSTPad

"""
How to detect multiple QwSTPads and handle their unexpected connection and disconnection.
"""

# Constants
SLEEP = 0.2                                 # The time between each check of connected pads

# Variables
pads = {}                                   # The dictionary to store QwSTPad objects
active = False                              # The state to set the controlled LEDs to

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    while True:
        print("QwSTPads: ", end="")

        # Go through each valid QwSTPad address
        for addr in ADDRESSES:

            # Is the pad already registered?
            if addr in pads:
                try:
                    # Do some action to confirm it is still connected
                    if active:
                        pads[addr].set_leds(pads[addr].address_code())
                    else:
                        pads[addr].clear_leds()
                except OSError:
                    # If that fails, unregister it
                    del pads[addr]

            # The pad is not registered
            else:
                try:
                    # Attempt to connect to and register it
                    pads[addr] = QwSTPad(address=addr)
                except OSError:
                    # If that fails, carry on
                    pass

            # Print out the connected state of the current pad
            print(f"{hex(addr)}" if addr in pads else "----", end=" ")
        print()

        # Toggle the LED state for next time
        active = not active

        time.sleep(SLEEP)

# Turn off the LEDs of any connected QwSTPads
finally:
    for addr in pads:
        try:
            pads[addr].clear_leds()
        except OSError:
            pass
