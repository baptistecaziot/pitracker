
# netstat
# kill -9 PID

from psutil import process_iter
from signal import SIGKILL # or SIGTERM

def freeport(port):
    processesClosed = 0
    for proc in process_iter():
        for conns in proc.connections(kind='inet'): # inet, inet4 tcp, tcp4, unix (both tcp and udp)
            if conns.laddr.port==port:
                print("Killing process %s" % proc.name())
                proc.kill() #proc.send_signal(SIGKILL)
                processesClosed+=1
    return processesClosed
