# ------ Sender3.py ------

from socket import *
import sys
import math
import time
import select
import threading

# Sender implements Go-Back-N protocol with window_size passed as command line arg

# global variables
PAYLOAD_SIZE = 1024
HEADER_SIZE = 3

# initial sequence number (for pt.3 & 4 a purely incrementing sequence number is used)
next_seq_num = 0
base = 0
EoF = False
end = False
timer_start = None
cond = threading.Condition()
file_size = 0



# helper for packing pkts
def mk_pkt(seq_num, buf):

    seq = (seq_num).to_bytes(2, byteorder='big')
    eof = (0).to_bytes(1, byteorder='big')
    is_last = False

    if(len(buf) < PAYLOAD_SIZE):
        eof = (1).to_bytes(1, byteorder='big')
        is_last = True
    
    # combine payload and header
    datagram = bytearray()
    datagram[0:1] = seq
    datagram[2:3] = eof
    datagram[3:3] = bytearray(buf)

    return datagram, is_last


# threaded pkt sender
def send_data(sock, address, f, N):

    global next_seq_num
    global base
    global timer_start
    global EoF
    global file_size

    payload = f.read(PAYLOAD_SIZE)

    while(payload):

        cond.acquire()
        if(next_seq_num < base + N):

            # make pkt
            datagram, EoF = mk_pkt(next_seq_num, payload)

            # send pkt to socket
            sock.sendto(datagram, address)
            file_size += len(payload)

            if(base == next_seq_num): # if pkt is first in window, start timer
                timer_start = round(time.time()*1000)

            next_seq_num+=1

            payload = f.read(PAYLOAD_SIZE)

            #check if EoF
            if(EoF):
                cond.release()
                break
        
        cond.release()
    


def ack_thread(so):

    global num_seq_num
    global base
    global timer_start
    global end
    global EoF

    while True:
        # check if socket has data to be received
        i_avail, o_avail, err = select.select([so], [], [], 0)

        # check for ACKs
        if(i_avail):
            ack_pkt = so.recvfrom(2) # *add hang try/except*
            ack = ack_pkt[0] # extract seq num bytes
            ack_num = int.from_bytes(ack, "big")
            
            # cumlative ACKs
            if(ack_num <= next_seq_num-1):
                cond.acquire()
                if(EoF and (ack_num == next_seq_num-1)):
                    cond.release()
                    break
                
                # shift window
                base = ack_num + 1
                if(base == next_seq_num):
                    timer_start = None # make sure timeout does not occurr unitl timer start is reset
                else:
                    timer_start = time.time()*1000 # reset timer for most recently ACK pkt
                
                cond.release()

    end = True

    

# run Go-Back-N protocol
def main(argv):

    host = argv[1] # remote host address ('127.0.0.1')
    port = int(argv[2]) # for part 1 using port 9001
    address = (host,port)

    file_name = argv[3] # name of image file to be transmitted

    timeout = int(argv[4])

    # set window size
    N = int(argv[5])

    # tally retransmits
    retransmits = 0

    # globals
    global next_seq_num
    global base
    global timer_start
    global end
    global file_size

    # create socket
    so = socket(AF_INET, SOCK_DGRAM)

    # open file
    f = open(file_name,"rb")

    # thread for recv ACKs
    thread2 = threading.Thread(target=ack_thread, args=(so,))
    thread2.start()

    # thread for sending data
    thread1 = threading.Thread(target=send_data, args=(so, address, f, N))
    thread1.start()

    time.sleep(0.1) # stall while threads init

    # start transmission
    init_time = time.time()

    while True:
            # check for timeout
            timer_check = round(time.time()*1000)
            t = -1
            try:
                t = timer_check - timer_start
            except TypeError:
                continue

            cond.acquire()
            if(t >= timeout):

                f.seek(base * PAYLOAD_SIZE) # reset file pointer

                # retransmit pkts after timeout
                timer_start = time.time()*1000
                for i in range(base, next_seq_num):
                    retransmits += 1
                    payload = f.read(PAYLOAD_SIZE)
                    datagram, is_last = mk_pkt(i, payload)
                    so.sendto(datagram, address)

                payload = f.read(PAYLOAD_SIZE) # get file pointer back to prior pos
                
            if(end == True):
                cond.release()
                break

            cond.release()
            

    so.close()
    thread1.join()
    thread2.join()
    f.close()

    # calculate throughput
    final_time = time.time()
    total_time = final_time - init_time
    throughput = round((file_size/total_time)/1000)

    file_size += len(payload) # increase sent file size by leng of payload

    # print sender performance
    print(throughput)


if __name__ == "__main__":
    main(sys.argv)
