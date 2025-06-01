def bit_stuff(data: list[int]):
    """
    Perform bit stuffing for USB packet

    :param data: the data to apply the bit stuffing on
    :type data: list[int]
    :return: the bit stuffed packet
    :rtype: list[int]
    """
    stuffed = []
    ones = 0
    for b in data:
        stuffed.append(b)
        if b:
            ones += 1
        else:
            ones = 0

        if ones == 6:
            ones = 0
            stuffed.append(0)

    return stuffed


def bit_mirror(data: int, size: int = None):
    """Perform bit mirroring on `data` assuming a `size` bits long integer

    :param data: the integer to perform the bit mirroring on.
    :type data: int
    :param size: The size to assume to perform the bit mirroring. If 
        the size is None, then the actual size in bits is taken.
    :type size: int or None

    :returns: the integer, bit mirrored
    :rtype: int
    """

    output = 0
    if not size:
        size = data.bit_length()
    assert size >= data.bit_length()
    for i in range(size):
        output <<= 1
        output += (data >> i) & 1
    return output


def to_bits(data: int, size: int):
    """Returns the bits of the int assuming a `size` bits number

    :param data: The integer to convert
    :type data: int
    :param size: The size of the integer in bits
    :type size: int

    :return: A list of bits, MSB first
    :rtype: list[int]
    """

    output_bits = [0 for _ in range(size)]
    for i in range(size - 1, -1, -1):
        output_bits[size - i - 1] = (data & (1 << i)) >> i

    return output_bits
