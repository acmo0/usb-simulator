import numpy as np
import random as rd

from ..protocol.packet import USBPacket
from ..util import bit_stuff


class USBBus(object):
    """Object representing an USB Bus at physical level.

    :param sym_duration: the duration of a symbol,
                         default 83ns to comply with FS devices spec
    :type symb_duration: float
    :param FE: the sampling frequency to work with,
               must be >= 2 * 1/symb_duration, default to 240MHz
    :type FE: float

    Example (connect to the bus, create packet, send it on the USB bus, then disconnect):

    .. code-block:: python
        :linenos:
        
        import random as rd

        from usbsimulator.protocol.packet import StartOfFramePacket
        from usbsimulator.protocol.field import FramenumberField
        
        # Create the packet to send
        p = StartOfFramePacket(
            FramenumberField(0x0)
        )

        bus = USBBus()
        
        bus.connect()
        bus.send_packet(p)
        bus.disconnect()
        
        # Simulate noise
        noise_function = lambda x: [i + rd.random() for i in x] 
        bus.simulate_noise(noise_function)

        # Dump the data
        bus.save_exchange("./dump_directory")
    """

    #: The voltage for a line at `LOW` state.
    LOW = 0.1
    #: The voltage for a line at `HIGH` state.
    HIGH = 3.3

    #: IDLE duration at connection, default 250ns.
    CONNECT_DURATION = 2.5e-7
    #: Disconnect signal duration.
    DISCONNECT_DURATION = 4e-6

    #: The average duration of the IDLE state between
    #: each packets if no precise duration is given.
    IDLE_FACTOR = 1e-7

    #: Synchronisation pattern before each packet
    #: as described in USB1.1 about *full-speed* devices.
    SYNC_PATTERN = [0, 0, 0, 0, 0, 0, 0, 1]

    def __init__(self, symb_duration: float = 1/12e6, FE: float = 240e6):
        """Init constructor
        """
        super().__init__()

        assert symb_duration != 0
        assert 2/symb_duration <= FE

        self.symb_duration = symb_duration
        self.FE = FE

        self.last_state = "J"

        self.signal = {
            "+": [],
            "-": []
        }

        self.connected = False

    def _j_state(self, duration: float = None):
        """
        Send a J state on the USB bus for a given duration
        (or by default for one symbol duration).

        :param duration: the duration of the state (in s)
        :type duration: float or None
        """
        if not duration:
            duration = self.symb_duration

        self.signal['+'] += [
            self.HIGH for _ in range(int(duration * self.FE))
        ]
        self.signal['-'] += [
            self.LOW for _ in range(int(duration * self.FE))
        ]

    def _k_state(self, duration: float = None):
        """
        Send a K state on the USB bus for a given duration
        (or by default for one symbol duration).

        :param duration: the duration of the state (in s)
        :type duration: float or None
        """
        if not duration:
            duration = self.symb_duration

        self.signal['+'] += [
            self.LOW for _ in range(int(duration * self.FE))
        ]
        self.signal['-'] += [
            self.HIGH for _ in range(int(duration * self.FE))
        ]

    def _se0(self, duration: float = None):
        """
        Send a se0 signal on the USB bus for a given duration
        (or by default for one symbol duration).

        :param duration: the duration of the state (in s)
        :type duration: float
        """
        if not duration:
            duration = self.symb_duration

        self.signal['+'] += [
            self.LOW for _ in range(int(duration * self.FE))
        ]
        self.signal['-'] += [
            self.LOW for _ in range(int(duration * self.FE))
        ]

    def _send_bit(self, bit: int):
        """
        Send a bit on the USB bus with NRZI encoding.

        :param bit: the bit to send
        :type bit: int
        """
        assert bit in [0, 1], f"Invalid bit value {bit}"

        if bit == 0:
            if self.last_state == "J":
                self.last_state = "K"
                self._k_state()
            else:
                self.last_state = "J"
                self._j_state()
        else:
            if self.last_state == "J":
                self._j_state()
            else:
                self._k_state()

    def _send_bits(self, bits: list[int]):
        """
        Send a list of bits on the USB bus.

        :param bits: the bits to send
        :type bits: list[int]
        """
        for bit in bits:
            self._send_bit(bit)

    def connect(self):
        """Send on the USB bus the signal of connection.
        """
        if self.connected:
            print("Already connected, please deconnect before")
        else:
            self._j_state(self.CONNECT_DURATION)
            self.connected = True

    def disconnect(self):
        """Send on the USB bus the signal of disconnection.
        """
        if not self.connected:
            print("Already deconnected, please connect before")
        else:
            self._se0(self.DISCONNECT_DURATION)
            self.connected = False

    def idle(
        self,
        duration: float = None,
        min_duration: float = None,
        max_duration: float = None
    ):
        """
        Output on the USB bus the IDLE state.

        :param duration: the duration of the IDLE state (in s)
        :type duration: float or None
        :param min_duration: the min duration of the random
                             IDLE duration (ignored if duration given)
        :type min_duration: float or None
        :param max_duration: the max duration of the random
                             IDLE duration (ignored if duration given)
        :type max_duration: float or None
        """
        assert duration or (min_duration and max_duration)

        # Generate random duration time of IDLE state
        if not duration:
            duration = rd.gauss(mu=1, sigma=1)
            duration *= self.IDLE_FACTOR
            duration = max(min_duration, min(max_duration, duration))

        duration = self.symb_duration * (duration // self.symb_duration)

        self._j_state(duration)

    def _sync(self):
        """Send the synchronisation signal on the USB bus.
        """
        self.last_state = "J"

        self._send_bits(
            bits=self.SYNC_PATTERN
        )

    def _eop(self):
        """
        Send the EOP signal on the USB bus.
        """
        self._se0(2 * self.symb_duration)
        self._j_state()
        self.last_state = "J"

    def _bit_stuff(self, data: list[int]):
        """Perform bit stuffing on the data according USB1.1 spec.

        :param data: the data to perform bit stuffing on
        :type data: list[int]
        :return: the bit stuffed data
        :rtype: list[int]
        """
        return bit_stuff(data)

    def send_packet(self, packet: USBPacket, idle_duration: float = None):
        """Send a packet on the USB bus

        :param packet: the USB packet to send
        :type packet: USBPacket
        :param idle_duration: precise time of IDLE
                              state after sending the packet
        :type idle_duration: float or None
        """
        if not self.connected:
            print("Unable to send packet, bus not connected")
            return

        # Get packet bits MSB first + bit stuff
        packet_bits = packet.get_bits()
        packet_bits = self._bit_stuff(packet_bits)

        # Send sync signal before sending the USB packet
        self._sync()
        # Send USB packet
        self._send_bits(packet_bits)
        # Send EOP
        self._eop()
        # Go to IDLE state
        self.idle(
            min_duration=self.symb_duration * 10,
            max_duration=self.symb_duration * 100
        )

    def save_exchange(self, path: str = "./"):
        """Save the signal generated in two separate files

        :param path: the path to save the data
        :type path: str
        """

        d_plus = np.array(
            self.signal["+"],
            dtype=np.float32
        )
        d_minus = np.array(
            self.signal['-'],
            dtype=np.float32
        )

        d_plus.astype(np.float32).tofile(path + "D_plus" + ".raw")
        d_minus.astype(np.float32).tofile(path + "D_neg" + ".raw")
        d_signal = np.zeros(len(d_plus) + len(d_minus))
        d_signal[::2] = d_minus
        d_signal[1::2] = d_plus
        d_signal.astype(np.float32).tofile(path+"signal.raw")

    def simulate_noise(self, noise: callable):
        """
        Simulate noise on the USB bus

        :param noise: the function that will simulate the noise on the bus
        :type noise: Callable
        """
        self.signal['+'] = noise(self.signal['+'])
        self.signal['-'] = noise(self.signal['-'])
