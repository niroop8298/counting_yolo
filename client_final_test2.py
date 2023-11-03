import socket, cv2, pickle,struct

# Socket Create
f1=open('f1.txt','w+')
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = 'localhost' 
port = 8000
client_socket.connect((host_ip,port)) 

# Socket Accept
while True:
    if client_socket:
        video_file = 'IMG_0222.mov'
        vid=cv2.VideoCapture(video_file)
        
        while(vid.isOpened()):
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            cv2.imshow('TRANSMITTING VIDEO',frame)
            '''
            msg=client_socket.recv(4096)
            print(msg.decode())
            f1.write(msg.decode()+'\n')
            '''
            key = cv2.waitKey(1) & 0xFF
            if key ==ord('q'):
                client_socket.close()
    f1.close()