# ----- Receiver1.py -----

from socket import *
import sys
import math
import time

def main(argv):
    pkt_size = 1027

    host = "127.0.0.1" # identifies loopback interface
    port = int(argv[1]) # for part 1 using port 9001
    filename = argv[2] # filename to write to: 'rfile'
    address = (host, port)

    so = socket(AF_INET, SOCK_DGRAM)
    so.bind(address)

    f = open(filename,'wb') # create file to write to

    data = so.recvfrom(pkt_size) # receive initial packet

    try:
        while(data): # if data in socket, keep receiving data

            raw_buf = data[0]
            # print('receiving data from:', data[1]) # print source address of packet

            buf = bytearray(raw_buf) # cast packet as byte array

            seq_num = buf[0:2]
            eof = buf[2]
            payload = buf[3:]

            seq_num = int.from_bytes(seq_num, byteorder='big') # cast sequence num bytes as interger

            if eof == 1:
                # print("End of file reached")
                f.write(payload)
                f.close()
                break

            so.settimeout(5) # set timer in case of time out
            f.write(payload)

            data = so.recvfrom(pkt_size)

    except timeout:
        f.close()
        so.close()
        print("File downloaded without reaching End of File")


if __name__ == "__main__":
    main(sys.argv)
