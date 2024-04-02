# ------ Sender1.py ------

from socket import *
import sys
import math
import time

def main(argv):

    payload_size = 1024
    header_size = 3

    file_name = argv[3] # name of image file to be transmitted

    host = argv[1] # remote host address ('127.0.0.1')
    port = int(argv[2]) # for part 1 using port 9001
    address = (host,port)

    so = socket(AF_INET, SOCK_DGRAM)

    f = open(file_name,"rb")
    payload = f.read(payload_size)

    # modulus and ticker for revolving sequence number
    modulus = 4
    ticker = 0

    while (payload):
        seq_num = ticker % modulus
        
        seq = (seq_num).to_bytes(2, byteorder='big')
        eof = (0).to_bytes(1, byteorder='big')

        if(len(payload) < payload_size):
            eof = (1).to_bytes(1, byteorder='big')
            print("End of file")
        
        datagram = bytearray()
        datagram[0:1] = seq
        datagram[2:3] = eof
        datagram[3:3] = bytearray(payload)

        # send datagram to socket with mini delay
        time.sleep(0.005)
        so.sendto(datagram, address)
        # print("seq_num", seq_num)

        payload = f.read(payload_size)
        ticker += 1

    print("file sent")
    so.close()
    f.close()


if __name__ == "__main__":
    main(sys.argv)
