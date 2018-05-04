### Script to quickly view and modify parameters of an SU2 config file ###
import sys,os
sys.path.append(os.environ['SU2_RUN'])
import SU2

from optparse import OptionParser

parser=OptionParser()
parser.add_option("-p",dest="param")
parser.add_option("-f",dest="file")
parser.add_option("-v",dest="val")

def Main():
	
	(options,args)=parser.parse_args()
	param=options.param
	file=options.file
	val=options.val

	# Read Config file
	config=SU2.io.Config(file)

	# Print Current Value
	print("Current -> {} = {}".format(param,config[param]))

	# Change Value if requested
	if val:
		if type(config[param])==int:
			val=int(val)
		config[param]=val
		# print change
		print("New -> {} = {}".format(param,config[param]))
		
		# Update Config 
		SU2.io.Config.write(config,file)

if __name__=="__main__":
	Main()
