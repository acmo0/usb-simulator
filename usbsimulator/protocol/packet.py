from enum import IntEnum

# module imports from python
from .field import *
from ..util import bit_mirror, to_bits, bit_stuff
from ..crc import usb_crc5, usb_crc16


class USBPacket(object):
    """
    Abstract class for USB packet.

    Implements the default function to get the bits of a USB packet and
    auto-update the CRC of the packet when an attribute is set.

    :param pid: PID of the packet
    :type pid: PidField
    :param fields: Additional fields of the usb packet
    :type fields: list[USBField] or None
    :param crc_function: the function to compute the crc of the packet
    :type crc_function: callable[list[int], list[int]] or None        
    """
    def __init__(
        self,
        pid: PidField,
        fields: list[USBField] = None,
        crc_function: callable = None
    ):

        """Init method
        """
        super().__init__()

        assert pid is not None

        self.pid = pid
        if fields is None:
            self.fields = []
        else:
            self.fields = fields
        self.crc_function = crc_function
        self.crc = self.crc_function(
            self.get_bits(with_crc=False, with_pid=False)
        ) if self.crc_function else []

    def get_bits(self, with_crc=True, with_pid=True):
        """
        Get the bits of the packet in the right order for transmission

        :param with_crc: Does the function has to return the crc
        :type with_crc: bool
        :param with_pid: Does the function has to return the pid alose
        :type with_pid: bool
        :return: All the bits of the packet, LSB first
        :rtype: list[int]
        """

        output_bits = [
            0 for _ in range(self.length_in_bits() - self.pid.size_in_bits)
        ]

        if with_pid:
            output_bits = to_bits(
                bit_mirror(
                    self.pid.val(),
                    self.pid.size_in_bits
                ),
                self.pid.size_in_bits
            ) + output_bits
        index = 0
        if with_pid:
            index = self.pid.size_in_bits

        for field in self.fields:
            field_val = field.val()

            if isinstance(field_val, IntEnum):
                field_val = field_val.value()

            field_bits = to_bits(
                bit_mirror(
                    field_val,
                    field.size_in_bits),
                field.size_in_bits
            )

            for b in field_bits:
                output_bits[index] = b
                index += 1

        if with_crc:
            output_bits += self.crc[::-1]

        return output_bits

    def length_in_bits(self):
        """
        Return the length in bits of the packet

        :return: Length in bits of the packet
        :rtype: int
        """
        length = 8
        for field in self.fields:
            length += field.size_in_bits

        return length

    def __setattr__(self, attr, value):
        if attr != "crc" and hasattr(self, "crc_function"):
            super().__setattr__(attr, value)
            self.crc = self.crc_function(
                self.get_bits(with_crc=False, with_pid=False)
            )
        else:
            super().__setattr__(attr, value)

    def __str__(self):
        out = f'{type(self).__name__}:'
        out += "\n\t"
        out += str(self.pid)
        if self.fields:
            out += "\n\t"
            out += "\n\t".join([str(f) for f in self.fields])
        if self.crc_function:
            out += "\n\t"
            out += f"CRC{len(self.crc)}:"
            out += "\t\t"
            out += str(hex(sum(
                [b*2**(len(self.crc) - i - 1) for i, b in enumerate(self.crc)]
            )))

        return out


class TokenPacket(USBPacket):
    """
    Class representing a USB Packet of type *token*.
    Please see 8.4.1 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param pid: the PID of the packet
    :type pid: PidField
    :param addr: the address in the token packet
    :type addr: AddressField
    :param endpoint: the endpoint of the token packet
    :type endpoint: EndpointField

    Example (create a *TOKEN_IN* USB packet):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import TokenPacket
        from usbsimulator.protocol.field import Pid, PidField, AddressField, EndpointField

        pid = PidField(Pid.TOKEN_IN)
        addr = AddressField(0x1ae)
        ep = EndpointField(0b101)

        tin_packet = TokenPacket(
            pid=pid,
            address=addr,
            endpoint=ep
        )
    """
    def __init__(
        self,
        pid: PidField,
        address: AddressField,
        endpoint: EndpointField
    ):
        """Init constructor
        """

        assert pid.val() == Pid.TOKEN_IN or \
            pid.val() == Pid.TOKEN_OUT or \
            pid.val() == Pid.TOKEN_SETUP, \
            "Invalid PID type for token packet"

        super().__init__(
            pid=pid,
            fields=[address, endpoint],
            crc_function=usb_crc5)


class StartOfFramePacket(USBPacket):
    """
    Class representing a USB Packet of type StartOfFrame.
    Please see 8.4.2 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param framenumber: The frame number of the packet
    :type framenumber: FramenumberField

    Example (create a *FrameNumber* USB packet):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import StartOfFramePacket
        from usbsimulator.protocol.field import FrameNumberField

        frame_nb = FramenumberField(0x0)

        p = StartOfFramePacket(frame_nb)
    """
    def __init__(self, framenumber: FramenumberField):
        """Init constructor
        """

        super().__init__(
            pid=PidField(Pid.TOKEN_SOF),
            fields=[framenumber],
            crc_function=usb_crc5
        )


class DataPacket(USBPacket):
    """
    Class representing a USB Packet of type Data.
    Please see 8.4.1 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param pid: The pid of the datapacket
    :type pid: PidField
    :param data: The data in the datapacket
    :type data: DataField

    Example (create a DATA0 packet):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import DataPacket
        from usbsimulator.protocol.field import Pid, PidField, DataField

        pid = PidField(Pid.DATA_DATA0)
        data = DataField(
            b'A very important data that I want to send on the USB bus'
        )

        data_packet = DataPacket(
            pid=pid,
            data=data
        )
    """

    def __init__(self, pid: PidField, data: DataField):
        """Init constructor
        """
        assert pid.val() == Pid.DATA_DATA0 or pid.val() == Pid.DATA_DATA1

        super().__init__(
            pid=pid,
            fields=[data],
            crc_function=usb_crc16)


class HandshakePacket(USBPacket):
    """
    Class representing a handshake USB packet.
    Please see 8.4.4 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param pid: The pid of the handshake packet. Must be Pid.HANDSHAKE_ACK, Pid.HANDSHAKE_ACK
        or Pid.HANDSHAKE_STALL.
    :type pid: PidField

    Example (create ACK and NACK packets):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import HandshakePacket
        from usbsimulator.protocol.field import Pid, PidField

        # In case of an ACK
        pid = PidField(Pid.HANDSHAKE_ACK)
        ack_packet = HandshakePacket(pid)
        
        # In case of a NACK
        pid = PidField(Pid.HANDSHAKE_NACK)
        nack_packet = HandshakePacket(pid)
    """

    def __init__(self, pid: PidField):
        assert pid.val() == Pid.HANDSHAKE_ACK or \
            pid.val() == Pid.HANDSHAKE_ACK or \
            pid.val() == Pid.HANDSHAKE_STALL

        super().__init__(pid=pid)
