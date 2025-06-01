from .field import DataField


class DeviceRequest(object):
    """
    Abstract class representing a Device Request as defined in USB1.1 spec.
    Please consider reading 9.3 from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param bmRequestType: the code of the bmRequestType
    :type bmRequestType: bytes
    :param bRequest: the code of the bRquest
    :type bRequest: bytes
    :param wValue: the code of the wValue
    :type wValue: bytes
    :param wIndex: the value of the wIndex
    :type wIndex: bytes
    :param wLength: the value of wLength
    :type wLength: bytes
    """

    def __init__(
        self,
        bmRequestType: bytes = b'\x00',
        bRequest: bytes = b'\x00',
        wValue: bytes = b'\x00',
        wIndex: bytes = b'\x00',
        wLength: bytes = b'\x00',
        data: bytes = None
    ):

        super().__init__()

        self.bmRequestType = bmRequestType
        self.bRequest = bRequest
        self.wValue = wValue
        self.wIndex = wIndex
        self.wLength = wLength
        self.data = data

    def get_bytes(self):
        """Get the DataField object using the fields of this object.

        :returns: the DataField object from the DeviceRequests
        :rtype: DataField
        """
        out = self.bmRequestType + \
            self.bRequest + \
            self.wValue + \
            self.wIndex + \
            self.wLength

        if self.data:
            out += self.data

        return DataField(out)


class SET_ADDRESS(DeviceRequest):
    """SET_ADDRESS device request.
    Please consider reading 9.4.6
    from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param device_address: the device address
    :type wValue: int

    Example (create a SET_ADDRESS device request):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import DataPacket
        from usbsimulator.protocol.field import Pid, PidField
        from usbsimulator.protocol.device_request import SET_ADDRESS

        device_address = 31

        pid = PidField(Pid.DATA_DATA0)
        device_request = SET_ADDRESS(device_address)

        set_add_device_rq = DataPacket(
            pid=pid
            data=device_request.get_bytes()
        )
    """
    def __init__(self, device_address: int):
        super().__init__(
            bmRequestType=b'\x00',
            bRequest=b'\x05',
            wValue=device_address.to_bytes(),
        )


class SET_DESCRIPTOR(DeviceRequest):
    """SET_DESCRIPTOR request

    Please consider reading 9.4.8
    from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.
    """
    def __init__(
        self,
        descriptor_type: bytes,
        language_id: bytes,
        descriptor_length: bytes,
        descriptor: bytes
    ):

        super().__init__(
            bmRequestType=b'\x00',
            bRequest=b'\x07',
            wValue=descriptor_type,
            wIndex=language_id,
            wLength=descriptor_length,
            data=descriptor,
        )


class GET_DESCRIPTOR(DeviceRequest):
    """GET_DESCRIPTOR request

    Please consider reading 9.4.3
    from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param descriptor_type: the type of the descriptor (p.e DEVICE descriptor)
    :type wValue: bytes
    :param language_id: the language ID for the descriptor
        (usefull for string descriptors only)
    :type language_id: bytes
    :param descriptor_length: the length of the descriptor
    :type descriptor_length: bytes

    Example (create a GET_DESCRIPTOR device request for device descriptor):

    .. code-block:: python
        :linenos:

        from usbsimulator.protocol.packet import DataPacket
        from usbsimulator.protocol.field import Pid, PidField
        from usbsimulator.protocol.device_request import GET_DESCRIPTOR

        device_address = 31

        pid = PidField(Pid.DATA_DATA0)
        # GET_DESCRIPTOR for device descriptor 
        device_request = GET_DESCRIPTOR(
            descriptor_type=b'\\x01',
            language_id=b'\\x00\\x00',
            descriptor_length=b'\\x12\\x00',
            descriptor=b''
        )

        get_desc_device_rq = DataPacket(
            pid=pid
            data=device_request.get_bytes()
        )

    """
    def __init__(
        self,
        descriptor_type: bytes,
        language_id: bytes,
        descriptor_length: bytes,
        descriptor: bytes = b''
    ):

        super().__init__(
            bmRequestType=b'\x80',
            bRequest=b'\x06',
            wValue=descriptor_type,
            wIndex=language_id,
            wLength=descriptor_length,
            data=descriptor,
        )


class GET_DESCRIPTOR_RESPONSE(DeviceRequest):
    """GET_DESCRIPTOR response

    Please consider reading 9.6
    from `USB1.1 specification <http://esd.cs.ucr.edu/webres/usb11.pdf>`_.

    :param descriptor_type: the type of the descriptor
    :type descriptor_type: bytes
    :param language_id: the ID of the language
    :type language_id: bytes
    :descript_length: the length of the descriptor
    :type descriptor_length: bytes
    :param descriptor: bytes
    """
    def __init__(
        self,
        descriptor_type: bytes,
        language_id: bytes,
        descriptor_length: bytes,
        descriptor: bytes
    ):

        super().__init__(
            bmRequestType=b'\x80',
            bRequest=b'\x06',
            wValue=descriptor_type,
            wIndex=language_id,
            wLength=descriptor_length,
            data=descriptor,
        )
