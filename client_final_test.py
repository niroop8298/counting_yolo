import socket, cv2, pickle,struct

# Socket Create
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.1.22' 
port = 8000
client_socket.connect((host_ip,port)) 

# Socket Accept
while True:
	if client_socket:
		vid = cv2.VideoCapture(0)
		
		while(vid.isOpened()):
			img,frame = vid.read()
			a = pickle.dumps(frame)
			message = struct.pack("Q",len(a))+a
			client_socket.sendall(message)
			
			cv2.imshow('TRANSMITTING VIDEO',frame)
			key = cv2.waitKey(1) & 0xFF
			if key ==ord('q'):
				client_socket.close()