Examples
========

This is a basic example of how to is this module. A more elaborated example is available under this one.

Send a connection signal on the USB bus, send a SOF packet and then send the disconnect signal
**********************************************************************************************

.. code-block:: python
  :linenos:

  from usbsimulator.signal.electrical import USBBus
  from usbsimulator.protocol.packet import StartOfFramePacket
  from usbsimulator.protocol.field import FramenumberField

  # Init the bus and send the connection signal
  bus = USBBus()
  bus.connect()

  # Create the SOF packet
  sof_packet = StartOfFramePacket(
    FramenumberField(0x7)
  )

  # Send it on the bus
  bus.send_packet(sof_packet)

  # Send the disconnect signal
  bus.disconnect()

  # Export the generated signal as npy file
  # Must be a dir
  bus.save_exchange("./exported_files")


A complete example
******************

This example is the code used to generate the two challenges for the 404CTF.

.. code-block:: python
  :linenos:

  from usbsimulator.protocol.field import *
  from usbsimulator.protocol.packet import *
  from usbsimulator.protocol.usb_request import *

  from usbsimulator.signal.electrical import USBBus
  from usbsimulator.signal.noise import f

  import random as rd


  CLIENT_ADDR = 31
  VENDOR_ID = 'e71a'
  DEVICE_CLASS = '81'
  PRODUCT_ID = "3f9c"
  DATA = b'Le flag est : 404CTF{9f993d54e688927dbfad50d6980c4b3dbf61991ba06fbe707409d699c724116b}'


  CLIENT_ERR_RATE = 1e-1
  HOST_ERR_RATE = 1e-4

  # Setup the client ADDR
  packets = [
    StartOfFramePacket(FramenumberField(0x0)),
    # Setup
    TokenPacket(
      pid=PidField(Pid.TOKEN_SETUP),
      address=AddressField(0x00),
      endpoint=EndpointField(0x00)
    ),
    # Set client add
    DataPacket(
      pid=PidField(Pid.DATA_DATA0),
      data=SET_ADDRESS(CLIENT_ADDR).get_bytes()),
    # Client ACK
    HandshakePacket(PidField(Pid.HANDSHAKE_ACK)),
    # Host 
    TokenPacket(
      pid=PidField(Pid.TOKEN_IN),
      address=AddressField(0x00),
      endpoint=EndpointField(0x00)),
    DataPacket(
      pid=PidField(Pid.DATA_DATA1),
      data=DataField(b'')),
    HandshakePacket(PidField(Pid.HANDSHAKE_ACK))
  ]

  # Information exchange
  packets += [
    StartOfFramePacket(FramenumberField(0x7)),
    # Setup
    TokenPacket(
      pid=PidField(Pid.TOKEN_SETUP),
      address=AddressField(CLIENT_ADDR),
      endpoint=EndpointField(0x00)
    ),
    DataPacket(
      pid=PidField(Pid.DATA_DATA0),
      data=GET_DESCRIPTOR(
        descriptor_type=b'\x01',
        language_id=b'\x00\x00',
        descriptor_length=b'\x12\x00',
        descriptor=b''
      ).get_bytes()
    ),
    HandshakePacket(PidField(Pid.HANDSHAKE_ACK)),
    TokenPacket(
      pid=PidField(Pid.TOKEN_IN),
      address=AddressField(CLIENT_ADDR),
      endpoint=EndpointField(0x00)
    ),
    HandshakePacket(PidField(Pid.HANDSHAKE_NACK)),
    TokenPacket(
      pid=PidField(Pid.TOKEN_IN),
      address=AddressField(CLIENT_ADDR),
      endpoint=EndpointField(0x00)
    ),
    DataPacket(
      pid=PidField(Pid.DATA_DATA1),
      data=DataField(bytes.fromhex('12010002' + DEVICE_CLASS + '020140' + VENDOR_ID + PRODUCT_ID + '000101020301'))
    ),
    HandshakePacket(PidField(Pid.HANDSHAKE_ACK)),
    TokenPacket(
      pid=PidField(Pid.TOKEN_OUT),
      address=AddressField(CLIENT_ADDR),
      endpoint=EndpointField(0x00)),
    DataPacket(
      pid=PidField(Pid.DATA_DATA1),
      data=DataField(b'')),
    HandshakePacket(PidField(Pid.HANDSHAKE_ACK))
  ]


  bus = USBBus()
  bus.SYNC_PATTERN = [0] * 15 + [1]
  bus.connect()
  for packet in packets:
    bus.send_packet(packet)
  bus.disconnect()
  bus.simulate_noise(f)

  bus.save_exchange("chall1/")


  # Data transmission
  client_err_nb = 0
  host_err_nb = 0

  for i, char in enumerate(DATA):
    transmitted = False

    while not transmitted:
      packets.append(
        TokenPacket(
          pid=PidField(Pid.TOKEN_IN),
          address=AddressField(CLIENT_ADDR),
          endpoint=EndpointField(0x00)
        )
      )

      client_err = (
        rd.uniform(0, 1) <= CLIENT_ERR_RATE
      )

      if client_err:
        client_err_nb += 1
        packets.append(HandshakePacket(PidField(Pid.HANDSHAKE_NACK)))
      else:
        if i % 2:
          packets.append(
            DataPacket(
              pid=PidField(Pid.DATA_DATA1),
              data=DataField(bytes([char])))
          )
        else:
          packets.append(
            DataPacket(
              pid=PidField(Pid.DATA_DATA0),
              data=DataField(bytes([char])))
          )
        transmitted = True

    packets.append(HandshakePacket(PidField(Pid.HANDSHAKE_ACK)))

  print(f"""
  Total transmitted packets : {len(packets)}
  Total errors : {client_err_nb}
  """)

  bus = USBBus()
  bus.SYNC_PATTERN = [0] * 15 + [1]
  bus.connect()
  for packet in packets:
    bus.send_packet(packet)
  bus.disconnect()
  bus.simulate_noise(f)

  bus.save_exchange("chall2/")