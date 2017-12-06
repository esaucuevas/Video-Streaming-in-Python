import sys
from Tkinter import Tk
from Client import Client
from Client1 import Client1

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		rtpPort = sys.argv[3]
		fileName = sys.argv[4]
		she = int(sys.argv[5])   #5th argument to determine whether 4 button or 3
	except:
		print "[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n"

	root = Tk()

	# Create a new client
	#if she == 0, use four button. if she == 1, use 3 button 
	if she == 0:
                print "Four-button Interface\n"
                app = Client(root,serverAddr,serverPort,rtpPort,fileName)
        elif she == 1:
                print "Three-button Interface\n"
                app = Client1(root,serverAddr,serverPort,rtpPort,fileName)

	app.master.title("RTPClient")
	root.mainloop()
