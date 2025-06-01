from .util import to_bits, bit_mirror


def usb_crc5(data: list[int]):
    """Compute the CRC5 of a USB packet according to USB1.1 spec

    :param data: The data to compute the CRC5 on, LSB first for each field
    :type data: list[int]

    :returns: the CRC5 of the bits passed in `data`
    :rtype: list[int]
    """
    size = len(data)

    rv = 0x02 if size == 11 else 0x1d

    lookup = [
        0x1e, 0x15, 0x03, 0x06, 0x0c, 0x18, 0x19, 0x1b,
        0x1f, 0x17, 0x07, 0x0e, 0x1c, 0x11, 0x0b, 0x16,
        0x05, 0x0a, 0x14
    ]
    for i in range(0, size):
        if data[i]:
            rv ^= lookup[(19-size + i) % 19]

    return to_bits(rv, 5)


def usb_crc16(data: list[int]):
    """Compute the CRC16 of a USB packet according to USB1.1 spec

    :param data: The data to compute tje CRC16 on, LSB first for each field
    :type data: list[int]

    :returns: the CRC16 of the bits passed in `data`
    :rtype: list[int]
    """
    rv = 0xffff

    for i in range(0, len(data), 8):
        for j in range(8):
            rv ^= (data[i + j] << j)
        for j in range(8):
            rv = (rv >> 1) ^ 0xa001 if (rv & 1) else (rv >> 1)

    return to_bits(rv ^ 0xffff, 16)
