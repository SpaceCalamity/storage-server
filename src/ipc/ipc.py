import queue
import socket
import threading

class IPC:
  created = False
  def __init__(self, port):
    if IPC.created:
      raise Exception('IPC already created')
    IPC.created = True
    self.port = port
    self.ipc_active = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.comm_queue = queue.Queue()

  def ipc_connect(self, port):
    self.active = True
    try:
      self.sock.connect(('localhost', port))
      try:
        self.sock.sendall(IPC.__flush('storage'))
        data = self.__read_data()
        if data == 'failed':
          print('IPC Error: Server did not expect this client')
          return
        elif data != 'connected':
          print('IPC Error: Assertion error (unexpected message <%s>)' % data)
          return
        thread = threading.Thread(target=self.__pipe)
        thread.start()
      except Exception as e:
        print('IPC Error: Failed to create receive thread')
        raise
    except Exception as e:
      print('IPC Error: Failed to connect to game server')

  def close(self):
    self.ipc_active = False
    try:
      self.sock.close()
    except:
      pass

  def __handle(self, data):
    data_parsed = data.split()
    size = len(data_parsed)
    #TODO

  def __pipe_out(self):
    try:
      while self.ipc_active:
        while not self.comm_queue.empty():
          try:
            comm = self.comm_queue.get()
          except:
            print('IPC Error: Queue is empty on get')
            comm = ''
          if comm:
            self.sock.sendall(__flush(comm))
    except Exception as e:
      print('IPC Error: Pipe connection failed (out thread)')
      print(e)
      self.close()

  def __pipe_in(self):
    try:
      while self.ipc_active:
        data = self.__read_data()
        self.__handle(data)
    except Exception e:
      print('IPC Error: Pipe connection failed (in thread)')
      print(e)
      self.close()

  def __read_data(self):
    data = ''
    while (byte := self.sock.recv(1)) != b'\n':
      data += byte.decode()
    return data

def __flush(message):
  return ('%s\n' % message).encode()
