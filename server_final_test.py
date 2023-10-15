import socket,cv2, pickle,struct
from ultralytics import YOLO
import supervision as sv
import numpy as np
import socket
import argparse
# create socket
ZONE_POLYGON=np.array([
    [0,0],
    [1280//2,0],
    [1280//2,720],
    [0,720]
])
def parse_arguments() -> argparse.Namespace:
    parser=argparse.ArgumentParser(description='YOLOv8 live')
    parser.add_argument("--webcam-resolution",
                        default=[1280,720],
                        nargs=2,
                        type=int
                        )
    args=parser.parse_args()
    return args
args=parse_arguments()
model=YOLO('yolov8l.pt')
box_annotator=sv.BoxAnnotator(thickness=2,text_thickness=2,text_scale=1)
zone=sv.PolygonZone(polygon=ZONE_POLYGON,frame_resolution_wh=tuple(args.webcam_resolution))
zone_annotator=sv.PolygonZoneAnnotator(zone=zone,color=sv.Color.red(),thickness=2,text_thickness=4,text_scale=2)
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
#host_ip = socket.gethostbyname(host_name)
host_ip='192.168.1.22'
print('HOST IP:',host_ip)
port = 8000
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)
client_socket,addr = server_socket.accept()
data = b""
payload_size = struct.calcsize("Q")
while True:
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024) # 4K
		if not packet: break
		data+=packet
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]
	msg_size = struct.unpack("Q",packed_msg_size)[0]
	
	while len(data) < msg_size:
		data += client_socket.recv(4*1024)
	frame_data = data[:msg_size]
	data  = data[msg_size:]
	frame = pickle.loads(frame_data)
	result=model(frame,agnostic_nms=True)[0]
	detections=sv.Detections.from_yolov8(result)
	labels=[f"{model.model.names[class_id]} {confidence:0.2f}" 
                for _,_,confidence,class_id,_ in detections]
	frame=box_annotator.annotate(scene=frame,detections=detections,labels=labels)
	zone.trigger(detections=detections)
	frame=zone_annotator.annotate(scene=frame)
	cv2.imshow("RECEIVING VIDEO",frame)
	key = cv2.waitKey(1) & 0xFF
	if key  == ord('q'):
		break
client_socket.close()