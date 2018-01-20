______________________________
##### Python Modules
sudo apt-get install python-pip

pip install python-forecastio
(pip install termcolor)
(pip install pdb)
pip install requests[security]
	# (Or install them directly)
	# pip install pyopenssl ndg-httpsclient pyasn1
(pip install numpy)	#this takes a long time......

______________________________
##### WS2812 NeoPixel
sudo apt-get update
sudo apt-get install build-essential python-dev git scons swig

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
sudo python setup.py install


