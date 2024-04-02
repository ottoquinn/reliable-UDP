# ----- Receiver3.py -----

from socket import *
import sys
import math
import time

PACKET_SIZE = 1027

def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start

def main(argv):

    host = "127.0.0.1" # identifies loopback interface
    port = int(argv[1]) # for part 1 using port 9001
    filename = argv[2] # filename to write to: 'rfile'
    address = (host, port)

    file_size = 0

    so = socket(AF_INET, SOCK_DGRAM)
    so.bind(address)

    f = open(filename,'wb+') # create file to write to

    data = so.recvfrom(PACKET_SIZE) # receive initial packet
    # print(data)

    # sequence number to be expected
    expect_seq = 0
    try:
        while(data): # if data in socket, keep receiving data

            raw_buf = data[0]
            src_address = data[1]
            # print('receiving data from:', data[1]) # print source address of packet

            buf = bytearray(raw_buf) # cast packet as byte array

            seq = buf[0:2]
            eof = buf[2]
            payload = buf[3:]

            seq_num = int.from_bytes(seq, byteorder='big') # cast sequence num bytes as int

            if(seq_num == expect_seq): # check if received pkt is in expected
                 # send seq of received pkt to sender (ack)
                so.sendto(seq, src_address)

                if eof == 1: # flood acks to sender
                    f.write(payload)
                    file_size += len(payload)
                    for i in range(0,30):
                        so.sendto(seq, src_address)
                    break
                
                expect_seq += 1
                f.write(payload)
                file_size += len(payload)

            else:
                # send seq of last in order pkt
                if(expect_seq == 0):
                    ack = (0).to_bytes(2, byteorder='big')
                    so.sendto(ack, src_address)
                else:
                    ack = (expect_seq-1).to_bytes(2, byteorder='big')
                    so.sendto(ack, src_address)


            so.settimeout(10) # if don't recv next pkt in 10s --> terminate
            data = so.recvfrom(PACKET_SIZE)

    except timeout:
        f.close()
        so.close()

    f.close()
    so.close()



if __name__ == "__main__":
    main(sys.argv)
