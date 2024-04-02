# ------ Sender2.py ------

from socket import *
import sys
import math
import time
import select

def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start

def main(argv):

    payload_size = 1024
    header_size = 3

    file_name = argv[3] # name of image file to be transmitted

    host = argv[1] # remote host address ('127.0.0.1')
    port = int(argv[2]) # for part 1 using port 9001
    address = (host,port)

    t = int(argv[4])/1000 # timeout timer length (convert to timeout arg units: sec)

    # metrics for measuring throughput and total pkts sent
    pkts_sent = 0
    retransmits = 0
    file_size = 0

    so = socket(AF_INET, SOCK_DGRAM)

    f = open(file_name,"rb")
    payload = f.read(payload_size)

    # modulus and ticker for revolving sequence number
    modulus = 4
    ticker = 0

    init_time = time.time() # start time of transmission

    while (payload):
        seq_num = ticker % modulus # update seq num
        
        seq = (seq_num).to_bytes(2, byteorder='big')
        eof = (0).to_bytes(1, byteorder='big')

        if(len(payload) < payload_size):
            eof = (1).to_bytes(1, byteorder='big')
        
        # combine payload and header
        datagram = bytearray()
        datagram[0:1] = seq
        datagram[2:3] = eof
        datagram[3:3] = bytearray(payload)

        # send datagram to socket
        pkts_sent += 1
        # time.sleep(.003)
        so.sendto(datagram, address)
        timer_start = timer()
        # print("sending pkt ", seq_num)

        # wait for ack from receiver
        # - if timeout passes or received ack does not match seq --> retrans pkt
        # - if ack received and seq match --> read next payload
        while True:
            # check if socket has data to be received
            i_avail, o_avail, err = select.select([so], [], [], 0)

            if(i_avail):
                # receive from socket
                ack_pkt = so.recvfrom(2)
                ack = ack_pkt[0] # extract seq num bytes
                
                if(ack == seq): # ack and seq match, move on to next pkt
                    # print("ACK ", seq_num)
                    break
                else:
                    continue
            
            else:
                diff = next(timer_start)
                if(diff >= t): # timeout occurred, retransmit pkt
                    # print("timeout occurred,", pkts_sent + 1)
                    pkts_sent += 1
                    retransmits += 1
                    so.sendto(datagram, address)
                    timer_start = timer() # restart timer
                    # print("retrans", seq_num)
                    continue
        
        # increase sent file size by leng of payload
        file_size += len(payload)
        # print("progress: ", ((file_size)/899169))

        payload = f.read(payload_size) # read next payload from file
        ticker += 1
            
    # calculate throughput
    total_time = time.time() - init_time
    throughput = round((file_size/total_time)/1000)

    # print sender performance
    print(retransmits)
    print(throughput)

    # print("file sent")
    so.close()
    f.close()


if __name__ == "__main__":
    main(sys.argv)
