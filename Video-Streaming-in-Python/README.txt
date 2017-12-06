Video Streaming with RTSP and RTP

Personally using Windows 10

Step 1: Open a terminal and start the server (server_port must be greater than 1024)
	python Server.py server_port
	python Server.py 1050

Step 2: Open another terminal and start the client
	python ClientLauncher.py server_host server_port RTP_port video_file interface_type
	  # where server_host is the name of the machine where the server is running, 
	  # RTP_port is the port where the RTP packets are received,
	  # video_file is the name of the video file you want to request
	  # interface_type is 0 or 1 depending on whether you want 4 -button or 3-button interface
	python ClientLauncher.py 127.0.0.1 1050 6000 movie.mjpeg 0

Once the interface is displayed, you can send RTSP commands to the server by pressing the buttons.

On the 4-button interface: 
	1. Client sends SETUP which is used to set up the session and transport parameters
	2. Client sends PLAY which starts the playback
	3. Client may send PAUSE to pause during playback
	4. Client sends TEARDOWN to terminate the session and close the connection

On the 3-button interface; 
	1. Client sends PLAY which is used to setup session if it has not been setup and then starts playback
	2. Client may send PAUSE to pause during playback
	3. Client sends STOP to terminate the session and close the connection