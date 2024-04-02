# ----- Receiver2.py -----

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

    f = open(filename,'wb+') # create file to write to

    data = so.recvfrom(pkt_size) # receive initial packet
    # print(data)

    # modulus and ticker for revolving sequence number
    modulus = 4
    ticker = 0

    try:
        while(data): # if data in socket, keep receiving data
            expect_seq = ticker % modulus # update expected seq num

            raw_buf = data[0]
            src_address = data[1]
            # print('receiving data from:', data[1]) # print source address of packet

            buf = bytearray(raw_buf) # cast packet as byte array

            seq = buf[0:2]
            eof = buf[2]
            payload = buf[3:]

            seq_num = int.from_bytes(seq, byteorder='big') # cast sequence num bytes as interger

            # send seq of received pkt to sender (ack)
            so.sendto(seq, src_address)
            # print("sending ACK ", seq_num)

            if(seq_num == expect_seq): # check if received pkt is in expected

                if eof == 1: # flood acks to sender
                    # print("End of file reached")
                    f.write(payload)
                    for i in range(0,20):
                        so.sendto(seq, src_address)
                    break
                
                f.write(payload)
                ticker += 1
                # print("writing payload", str(ticker))

 
            so.settimeout(10) # timeout in case of hang
            data = so.recvfrom(pkt_size)

    except timeout:
        f.close()
        so.close()
        # print("Exception timeout: File downloaded before EoF")

    f.close()
    so.close()
    # print(ticker)
    # print("File downloaded")


if __name__ == "__main__":
    main(sys.argv)
