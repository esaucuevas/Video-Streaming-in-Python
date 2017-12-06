import random, math
import time
from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'

	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	
	jitcount = 0   #To keep track of jitter
	
	clientInfo = {}

	def __init__(self, clientInfo):
		self.clientInfo = clientInfo

	def run(self):
		threading.Thread(target=self.recvRtspRequest).start()

	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:
			data = connSocket.recv(256)  ###
			if data:
				#print "\nData received: "
				print "\n"
				self.processRtspRequest(data)

	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number
		seq = request[1].split(' ')

		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print "processing SETUP\n"

				try:

					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY
					
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)

				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				print "RTSP/1.0 200 OK\nCSeq: " + seq[1] + "\nSession: " + str(self.clientInfo['session'])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]
				

		# Process PLAY request
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print "\nprocessing PLAY\n"
				self.state = self.PLAYING

				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

				self.replyRtsp(self.OK_200, seq[1])  
				print "\nRTSP/1.0 200 OK\nCSeq: " + seq[1] + "\nSession: " + str(self.clientInfo['session'])+ "\n"
				
				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
				self.clientInfo['worker'].start()
		
		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				self.state = self.READY
				print "\nprocessing PAUSE\n"
				self.clientInfo['event'].set()

				self.replyRtsp(self.OK_200, seq[0])
				print "\nRTSP/1.0 200 OK\nCSeq: " + seq[0] + "\nSession: " + str(self.clientInfo['session'])+ "\n"

				
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print "\nprocessing TEARDOWN\n"

			self.clientInfo['event'].set()

			self.replyRtsp(self.OK_200, seq[0])
			print "\nRTSP/1.0 200 OK\nCSeq: " + seq[0] + "\nSession: " + str(self.clientInfo['session'])+ "\n"
			
			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()
			
			#calc and display avg. jitter
			frameNumber = self.clientInfo['videoStream'].frameNbr()
			rate = float(self.jitcount)/frameNumber
			print("Jitter: %.6f" % rate) + " s"
			
	def sendRtp(self):
		"""Send RTP packets over UDP."""

		while True:
		#implement process emulating network impairments with settable jitter
			jitter = (math.floor(random.uniform(-4,7)))/1000
			self.jitcount += jitter  
			self.clientInfo['event'].wait(0.05 +jitter)

			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break

			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])

					#simulates packet loss
					loss = random.uniform(1,100)
					if loss > 10.0:   	# choose the RTP Packet Loss Rate ratio
						self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
						time.sleep(jitter+.01)
				except:
					print "Connection Error"
					traceback.print_exc(file=sys.stdout)
				
	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0

		rtpPacket = RtpPacket()

		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)

		return rtpPacket.getPacket()

	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply)

		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print "404 NOT FOUND"
		elif code == self.CON_ERR_500:
			print "500 CONNECTION ERROR"
