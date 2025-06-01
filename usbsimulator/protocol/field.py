from enum import IntEnum


class USBField(object):
    """
    Abstract class representing an USB field.
    """
    def val(self):
        return self.value

    def __init__(self, size_in_bits):
        super().__init__()
        self.size_in_bits = size_in_bits

    def __str__(self):
        base = type(self).__name__ + ":\t"
        if type(self.value) is int or type(self.value) is Pid:
            return base + hex(self.value)
        else:
            return base + str(self.value)


class Pid(IntEnum):
    """Valid PID values for a USB packet, values are MSB first.

    Please see 8.3.1 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_. 
    """
    TOKEN_OUT = 0b11100001
    TOKEN_IN = 0b01101001
    TOKEN_SOF = 0b10100101
    TOKEN_SETUP = 0b00101101
    DATA_DATA0 = 0b11000011
    DATA_DATA1 = 0b01001011
    HANDSHAKE_ACK = 0b11010010
    HANDSHAKE_NACK = 0b01011010
    HANDSHAKE_STALL = 0b00011110
    SPECIAL_PRE = 0b00111100


class EndpointField(USBField):
    """
    Endpoint field, values are MSB first

    :param endpoint: The endpoint value must be on 3 bits max
    :type endpoint: int

    Example:

    .. code-block:: python
        :linenos:

        my_endpoint_value = 3
        f = EndpointField(my_endpoint_value)
    """
    def __init__(self, endpoint: int):
        """Init constructor
        """
        super().__init__(size_in_bits=4)
        assert endpoint.bit_length() <= 4

        self.value = endpoint


class PidField(USBField):
    """Pid field for a USB packet.

    :param pid: The value of the Pid
    :type pid: Pid

    Example:

    .. code-block:: python
        :linenos:

        my_pid = Pid.TOKEN_SOF
        f = PidField(my_pid)
    """

    def __init__(self, pid: Pid):
        """Init constructor
        """
        super().__init__(size_in_bits=8)
        assert isinstance(pid, Pid)
        self.value = pid


class AddressField(USBField):
    """
    Address field, values are MSB first

    :param address: The address value must be on 6 bits max
    :type address: int

    Example:

    .. code-block:: python
        :linenos:

        my_addr = 0b101101
        f = AddressField(my_addr)
    """
    def __init__(self, address: int):
        """Init constructor
        """
        super().__init__(size_in_bits=7)
        assert address.bit_length() <= 7

        self.value = address

    def __str__(self):
        return type(self).__name__ + ":\t" + str(self.value)


class FramenumberField(USBField):
    """Field containing the frame number of a USB packet.

    :param framenumber: the number of the frame
    :type framenumber: int

    Example:

    .. code-block:: python
        :linenos:

        frame_nb = 0x1ea
        f = FramenumberField(frame_nb)
    """

    def __init__(self, framenumber: int):
        """Init constructor
        """
        assert 0 <= framenumber <= 0x7ff

        super().__init__(size_in_bits=11)
        self.value = framenumber


class DataField(USBField):
    """Data field for a USB packet.

    :param data: the data to be stored in the field, MSB first
    :type data: bytes

    Example:

    .. code-block:: python
        :linenos:

        my_data = b'Very important data to send by USB !'
        f = DataField(my_data)
    """

    def __init__(self, data: bytes):
        """Init constructor
        """

        assert len(data) <= 1023, \
            "Bytes per data packet can't exceed 1023 bytes"

        super().__init__(size_in_bits=8 * len(data))
        super().__setattr__("value", int.from_bytes(data, 'little'))

    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        if attr == "value":
            # Update size
            self.size_in_bits = 8 * len(self.value)
