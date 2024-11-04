#!/usr/bin/env python

import sys
import os

from PyQt6 import QtWidgets as QtW
from PyQt6 import QtCore

import configparser

from Sweep371B import Sweep
from CheckConfig371B import CheckConfig

class MainWindow( QtW.QWidget ):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Tektronix 371B GPIB Controller")

		layout = QtW.QFormLayout(self)
		self.setLayout(layout)
		
		self.settings2 = QtCore.QSettings('Tektronix 371B', 'settings2')

		self.loadFileButton = QtW.QPushButton("Open Config File")
		self.loadFileButton.clicked.connect(self.loadConfigfile)
		layout.addRow ( "Load Config File", self.loadFileButton )

		self.powerBox = QtW.QComboBox ( )
		self.powerBox.addItem ( "300 W", "300" )
		self.powerBox.addItem ( "3 kW", "3000" )
		layout.addRow ( "Maximum Power", self.powerBox )

		self.maxSupplyBox = QtW.QLineEdit("10")
		layout.addRow ( "Maximum Collector Voltage [V]", self.maxSupplyBox )

		self.HorizBox = QtW.QComboBox ( )
		self.HorizBox.addItem ("100 mV/div", "0.1")
		self.HorizBox.addItem ("200 mV/div", "0.2")
		self.HorizBox.addItem ("500 mV/div", "0.5")
		self.HorizBox.addItem ("1 V/div", "1")
		self.HorizBox.addItem ("2 V/div", "2")
		self.HorizBox.addItem ("5 V/div", "5")
		layout.addRow ( "Horizontal Scale", self.HorizBox )

		self.VertBox = QtW.QComboBox ( )
		self.VertBox.addItem ("500 mA/div", "0.5")
		self.VertBox.addItem ("1 A/div", "1")
		self.VertBox.addItem ("2 A/div", "2")
		self.VertBox.addItem ("5 A/div", "5")
		self.VertBox.addItem ("10 A/div", "10")
		self.VertBox.addItem ("20 A/div", "20")
		self.VertBox.addItem ("50 A/div", "50")
		layout.addRow ( "Vertical Scale", self.VertBox )

		self.OffsetBox = QtW.QLineEdit("2")
		layout.addRow ( "Gate Voltage Start Value [V]", self.OffsetBox )

		self.StepBox = QtW.QComboBox ( ) # note: with multi also 50 and 20 mV are possible, but it's disabled in Sweep371B for now
		self.StepBox.addItem ("200 mV", "0.2")
		self.StepBox.addItem ("500 mV", "0.5")
		self.StepBox.addItem ("1 V", "1")
		self.StepBox.addItem ("2 V", "2")
		self.StepBox.addItem ("5 V", "5")
		layout.addRow ( "Gate Voltage Step", self.StepBox )

		self.StepNumberBox = QtW.QComboBox ( )
		self.StepNumberBox.addItems (["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
		layout.addRow ( "Number of Steps", self.StepNumberBox )
		
		self.sweepBox = QtW.QCheckBox(text="Slow Sweep")
		layout.addWidget(self.sweepBox)

		button = QtW.QPushButton()
		button.setText('Save Configuration')
		button.show()
		button.clicked.connect( self.saveConfigfile )
		layout.addWidget( button )

		btn = QtW.QPushButton()
		btn.setText('Start Measurement')
		btn.move(150,200)
		btn.show()
		btn.clicked.connect( self.StartMeasurement )
		layout.addWidget( btn )
		
		#Fixed window size. Not needed, just temporarily for visualization
		self.setFixedWidth(325)
		self.setFixedHeight(321)

		self.WidgetMap = {
			'maxpower': self.powerBox,
			'maxvoltage': self.maxSupplyBox,
			'horizscale': self.HorizBox,
			'vertscale': self.VertBox,
			'gateoffset': self.OffsetBox,
			'gatestep': self.StepBox,
			'stepnumber': self.StepNumberBox,
			'slowsweep': self.sweepBox
		}

		# show the window
		self.show()
	
	def loadConfigfile( self ):
		loadConfigPath = QtW.QFileDialog.getOpenFileName(self, 'Open Config File', str(os.path.dirname(__file__) + "/Configs")) #does this work on Linux?
		print("Loading File: " + str(loadConfigPath[0]))
		loadconfigParser = configparser.RawConfigParser() 
		loadconfigParser.read(loadConfigPath)

		# Horrible, there should be a map, together with the save file section
		for name, widget in self.WidgetMap.items():
			cls = widget.__class__.__name__
			if cls == "QCheckBox":
				self.WidgetMap[name].setChecked(loadconfigParser.get('configuration', name) == "True")
			elif cls == "QLineEdit":
				self.WidgetMap[name].setText(loadconfigParser.get('configuration', name))
			elif cls == "QComboBox" and name == "stepnumber": #the step number has text=data, so it's different from other combo boxes
				self.WidgetMap[name].setCurrentText(loadconfigParser.get('configuration', name))
			elif cls == "QComboBox":
				index = self.WidgetMap[name].findData(str(loadconfigParser.get('configuration', name)))
				self.WidgetMap[name].setCurrentIndex(index)
			else:
				print("Widget not recognized")
		
		print("Configuration loaded")

	def saveConfigfile( self ):
		config = configparser.ConfigParser()
		config.add_section('configuration')

		for name, widget in self.WidgetMap.items():
			cls = widget.__class__.__name__
			if cls == "QCheckBox":
				config['configuration'][name] = str(self.WidgetMap[name].isChecked())
			elif cls == "QLineEdit":
				config['configuration'][name] = self.WidgetMap[name].text()
			elif cls == "QComboBox" and name == "stepnumber":
				config['configuration'][name] = self.WidgetMap[name].currentText()
			elif cls == "QComboBox":
				config['configuration'][name] = self.WidgetMap[name].currentData()
			else:
				print("Widget not recognized")
		
		saveConfigPath = QtW.QFileDialog.getSaveFileName(self, 'New Config File Name', str(os.path.dirname(__file__) + "/Configs")) #does this work on Linux?
		with open(saveConfigPath[0],'w') as configfile:
			config.write(configfile)

		print("Configuration saved")
	
	def GetSettings( self ):
		powerSetting = self.powerBox.currentData()
		maxSupplySetting = self.maxSupplyBox.text()
		horizSetting = self.HorizBox.currentData()
		vertSetting = self.VertBox.currentData()
		offsetSetting = self.OffsetBox.text()
		stepSetting =  self.StepBox.currentData()		
		stepNumberSetting =  self.StepNumberBox.currentText()
		slowSweep = self.sweepBox.isChecked()

		#convert maximum applied voltage in percentage of maximum voltage (30 V). In case high voltage mode is used, this should be corrected
		maxSupplyConverted = str(float(maxSupplySetting)*100./30.)

		#convert offset in units of step
		offsetConverted = str(float(offsetSetting)/ float(stepSetting))

		return powerSetting, maxSupplyConverted, horizSetting, vertSetting, stepSetting, stepNumberSetting, offsetConverted, slowSweep

	def StartMeasurement( self ):		
		settings = self.GetSettings()
		#print(settings)
		Sweep( settings[0], settings[1], settings[2], settings[3], settings[4], settings[5], settings[6], settings[7] )

if __name__ == "__main__":
	app = QtW.QApplication([])
	window = MainWindow()
	sys.exit(app.exec()) #it was exec_ but I had problems with pyqt6 with the _. No idea if there is any difference