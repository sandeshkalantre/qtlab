
#module import
try:
    import gtk
except:
    print "Gtk not found."
    sys.exit(0)

try:
    import pygtk
    pygtk.require('2.0')
except:
    print "PyGtk not found."
    sys.exit(0)

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('AWG')
import Waveform_PresetAmp as Wav
import qt

import os
import visa



class Window:
    def __init__(self):
        if 'AWG' in locals():
            AWG._ins._visainstrument.close()   # Trying to close previous AWG session. 

        global AWG
        try:
            AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', address="10.21.64.117")
        except Exception,e:
            print "Failed to connect to AWG."
            raise e

        #initializing the variables
        #default values
        #also change the set_active values to make change in GUI if changing the default values
        self.num_seg = 3
        self.time_units = "ms"
        self.amp_units = "mV"
        self.awg_clock = 1e8
        self.max_amp = 1   # Maximum amplitude in Volts
        #the hard variables denote the ones that go on the hardware, the non-hard variables are used in the waveform object
        self.awg_clock_hard = 1e8
        self.max_amp_hard = 1   # Maximum amplitude in Volts
        self.num_ele = 10   #number of elements in a sequence

        #default run mode for AWG
        self.runmode = "SEQ"

        #temporary variable to store the max_amp during sequence generation
        self.max_amp_tmp = 1

        self.init_AWG()
      
        #gui initialization from the glade file
        self.gladefile = "AWG/awg_gui.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)

        self.window = self.builder.get_object("window1")
        self.statusbar = self.builder.get_object("statusbar1")
        self.context_id = self.statusbar.get_context_id("status")
        self.treeview = self.builder.get_object("treeview1")
        #self.window.show()

        self.builder.connect_signals(self)

        
     
        
        label = self.builder.get_object("awg_settings_label")
        label.set_text("AWG Settings \n\n" + "AWG Clock : " + str(self.awg_clock_hard/1e6) + " MHz\n" + "Maximum Amplitude : " + str(self.max_amp_hard) + " V\n" + "Run Mode : " + str(self.runmode) + "\n")
        #create a waveform object
        self.wav_obj = Wav.Waveform(waveform_name = 'WAV1', AWG_clock = self.awg_clock, TimeUnits = self.time_units , AmpUnits = self.amp_units)

        self.wav_obj_begin = Wav.Waveform(waveform_name = 'WAV1', AWG_clock = self.awg_clock, TimeUnits = self.time_units , AmpUnits = self.amp_units)
        self.wav_obj_end = Wav.Waveform(waveform_name = 'WAV1', AWG_clock = self.awg_clock, TimeUnits = self.time_units , AmpUnits = self.amp_units)  


        #treeview model
        self.treeview_list = gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str,str,str)
        self.treeview.set_model(self.treeview_list)
        #note that this has only 13 columns, the first column since depends on the segment number has to inserted at the first position manually
        self.default_treeview_list = [0.001,0,'L','L',0,'L','L',0,'L','L',0,'L','L']
        for i in range(self.num_seg):
            self.treeview_list.append([i+1] + self.default_treeview_list)
        
        self.renderer_text = gtk.CellRendererText()
        self.column_text = gtk.TreeViewColumn("Segment",self.renderer_text,text=0)
        self.column_text.set_expand(True)
        self.treeview.append_column(self.column_text)

        self.renderer_time = gtk.CellRendererText()
        self.renderer_time.set_property("editable",True)
        self.column_time = gtk.TreeViewColumn("Time",self.renderer_time,text=1)
        self.column_time.set_expand(True)
        self.treeview.append_column(self.column_time)
        
        self.renderer_ch1_a = gtk.CellRendererText()
        self.renderer_ch1_a.set_property("editable",True)
        self.renderer_ch1_a.set_property("background","red")
        self.column_ch1_a = gtk.TreeViewColumn("Analog",self.renderer_ch1_a,text=2)
        self.column_ch1_a.set_expand(True)
        self.treeview.append_column(self.column_ch1_a)
        
        self.renderer_ch1_m1 = gtk.CellRendererText()
        self.renderer_ch1_m1.set_property("editable",True)
        self.renderer_ch1_m1.set_property("background","red")
        self.column_ch1_m1 = gtk.TreeViewColumn("M1",self.renderer_ch1_m1,text=3)
        self.column_ch1_m1.set_expand(True)
        self.treeview.append_column(self.column_ch1_m1)

        self.renderer_ch1_m2 = gtk.CellRendererText()
        self.renderer_ch1_m2.set_property("editable",True)
        self.renderer_ch1_m2.set_property("background","red")
        self.column_ch1_m2 = gtk.TreeViewColumn("M2",self.renderer_ch1_m2,text=4)
        self.column_ch1_m2.set_expand(True)
        self.treeview.append_column(self.column_ch1_m2)

        self.renderer_ch2_a = gtk.CellRendererText()
        self.renderer_ch2_a.set_property("editable",True)
        self.renderer_ch2_a.set_property("background","green")
        self.column_ch2_a = gtk.TreeViewColumn("Analog",self.renderer_ch2_a,text=5)
        self.column_ch2_a.set_expand(True)
        self.treeview.append_column(self.column_ch2_a)
        
        self.renderer_ch2_m1 = gtk.CellRendererText()
        self.renderer_ch2_m1.set_property("editable",True)
        self.renderer_ch2_m1.set_property("background","green")
        self.column_ch2_m1 = gtk.TreeViewColumn("M1",self.renderer_ch2_m1,text=6)
        self.column_ch2_m1.set_expand(True)
        self.treeview.append_column(self.column_ch2_m1)

        self.renderer_ch2_m2 = gtk.CellRendererText()
        self.renderer_ch2_m2.set_property("editable",True)
        self.renderer_ch2_m2.set_property("background","green")
        self.column_ch2_m2 = gtk.TreeViewColumn("M2",self.renderer_ch2_m2,text=7)
        self.column_ch2_m2.set_expand(True)
        self.treeview.append_column(self.column_ch2_m2)
        
        self.renderer_ch3_a = gtk.CellRendererText()
        self.renderer_ch3_a.set_property("editable",True)
        self.renderer_ch3_a.set_property("background","blue")
        self.column_ch3_a = gtk.TreeViewColumn("Analog",self.renderer_ch3_a,text=8)
        self.column_ch3_a.set_expand(True)
        self.treeview.append_column(self.column_ch3_a)
        
        self.renderer_ch3_m1 = gtk.CellRendererText()
        self.renderer_ch3_m1.set_property("editable",True)
        self.renderer_ch3_m1.set_property("background","blue")
        self.column_ch3_m1 = gtk.TreeViewColumn("M1",self.renderer_ch3_m1,text=9)
        self.column_ch3_m1.set_expand(True)
        self.treeview.append_column(self.column_ch3_m1)

        self.renderer_ch3_m2 = gtk.CellRendererText()
        self.renderer_ch3_m2.set_property("editable",True)
        self.renderer_ch3_m2.set_property("background","blue")
        self.column_ch3_m2 = gtk.TreeViewColumn("M2",self.renderer_ch3_m2,text=10)
        self.column_ch3_m2.set_expand(True)
        self.treeview.append_column(self.column_ch3_m2)

        self.renderer_ch4_a = gtk.CellRendererText()
        self.renderer_ch4_a.set_property("editable",True)
        self.renderer_ch4_a.set_property("background","cyan")
        self.column_ch4_a = gtk.TreeViewColumn("Analog",self.renderer_ch4_a,text=11)
        self.column_ch4_a.set_expand(True)
        self.treeview.append_column(self.column_ch4_a)
        
        self.renderer_ch4_m1 = gtk.CellRendererText()
        self.renderer_ch4_m1.set_property("editable",True)
        self.renderer_ch4_m1.set_property("background","cyan")
        self.column_ch4_m1 = gtk.TreeViewColumn("M1",self.renderer_ch4_m1,text=12)
        self.column_ch4_m1.set_expand(True)
        self.treeview.append_column(self.column_ch4_m1)

        self.renderer_ch4_m2 = gtk.CellRendererText()
        self.renderer_ch4_m2.set_property("editable",True)
        self.renderer_ch4_m2.set_property("background","cyan")
        self.column_ch4_m2 = gtk.TreeViewColumn("M2",self.renderer_ch4_m2,text=13)
        self.column_ch4_m2.set_expand(True)
        self.treeview.append_column(self.column_ch4_m2)

        self.renderer_time.connect("edited",self.text_edited,1)
        self.renderer_ch1_a.connect("edited",self.text_edited,2)
        self.renderer_ch1_m1.connect("edited",self.text_edited,3)
        self.renderer_ch1_m2.connect("edited",self.text_edited,4)
        self.renderer_ch2_a.connect("edited",self.text_edited,5)
        self.renderer_ch2_m1.connect("edited",self.text_edited,6)
        self.renderer_ch2_m2.connect("edited",self.text_edited,7)
        self.renderer_ch3_a.connect("edited",self.text_edited,8)
        self.renderer_ch3_m1.connect("edited",self.text_edited,9)
        self.renderer_ch3_m2.connect("edited",self.text_edited,10)
        self.renderer_ch4_a.connect("edited",self.text_edited,11)
        self.renderer_ch4_m1.connect("edited",self.text_edited,12)
        self.renderer_ch4_m2.connect("edited",self.text_edited,13)


        #initialization of the list for time and amplitude units
        self.time_units_list = gtk.ListStore(int,str)
        self.time_units_list.append([0,"s"])
        self.time_units_list.append([1,"ms"])
        self.time_units_list.append([2,"us"])
    

        self.amp_units_list = gtk.ListStore(int,str)
        self.amp_units_list.append([0,"V"])
        self.amp_units_list.append([1,"mV"])
        self.amp_units_list.append([2,"uV"])

        self.runmode_list = gtk.ListStore(int,str)
        self.runmode_list.append([0,"TRIG"])
        self.runmode_list.append([0,"CONT"])
        self.runmode_list.append([0,"SEQ"])
        self.runmode_list.append([0,"GATE"])

        #initialization of the comboboxes for time and amplitude units
        self.time_units_box = self.builder.get_object("time_units_box")
        self.time_units_box.set_model(self.time_units_list)
        self.amp_units_box = self.builder.get_object("amp_units_box")
        self.amp_units_box.set_model(self.amp_units_list)
        self.cell = gtk.CellRendererText()
        self.time_units_box.pack_start(self.cell,True)
        self.time_units_box.add_attribute(self.cell, 'text', 1)
        #set_active sets the default value
        self.time_units_box.set_active(1)
        self.amp_units_box.pack_start(self.cell,True)
        self.amp_units_box.add_attribute(self.cell, 'text', 1)
        self.amp_units_box.set_active(1)

        self.runmode_box = self.builder.get_object('runmode_box')
        self.runmode_box.set_model(self.runmode_list)
        self.runmode_box.pack_start(self.cell,True)
        self.runmode_box.add_attribute(self.cell,'text',1)
        self.runmode_box.set_active(2)

        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 

    #set AWG parameters
    def init_AWG(self):
        
         #channel status
        self.ch1_status = AWG.get_ch1_status()
        self.ch2_status = AWG.get_ch2_status()
        self.ch3_status = AWG.get_ch3_status()
        self.ch4_status = AWG.get_ch4_status()

        AWG.set_ch1_amplitude(self.max_amp_hard)  # Setting maximum needed amp on all AWG channels
        AWG.set_ch2_amplitude(self.max_amp_hard) 
        AWG.set_ch3_amplitude(self.max_amp_hard) 
        AWG.set_ch4_amplitude(self.max_amp_hard) 

        #AWG.set_ch1_skew(0.0)
        #AWG.set_ch2_skew(0.0)
        #AWG.set_ch3_skew(0.0)
        #AWG.set_ch4_skew(0.0)
   
        
        AWG.del_waveform_all()  # Clear all waveforms in waveform list
        AWG.set_clock(self.awg_clock_hard)  # Set AWG clock
        AWG.set_runmode(self.runmode)

    def set_channel_status(self,status="off",channel=1):
        #the default is off for security
        if channel == 1:
            AWG.set_ch1_status(status)
            print "Channel 1 set to",status
        elif channel == 2:
            AWG.set_ch2_status(status)
            print "Channel 2 set to",status
        elif channel == 3:
            AWG.set_ch3_status(status)
            print "Channel 3 set to",status
        elif channel == 4:
            AWG.set_ch4_status(status)
            print "Channel 4 set to",status
        else:
            print "Invalid Channel"
        label = self.builder.get_object('ch' + str(channel) + '_status_label')
        toggle_button = self.builder.get_object('ch' + str(channel) + '_status_button')
        if(status.upper() == "OFF"):
            label.set_markup("<span background='#808080'>Channel " + str(channel) + "</span>")
            #toggle_button.set_active(False)
        else:
            label.set_markup("<span background='#00FF00'>Channel " + str(channel) + "</span>")
            #toggle_button.set_active(True)

    def on_ch1_status_button_toggled(self,button,data=None):
        toggle_button = self.builder.get_object('ch1_status_button')
        if toggle_button.get_active() == True:
            self.set_channel_status("ON",1)
        else:
            self.set_channel_status("OFF",1)
    def on_ch2_status_button_toggled(self,button,data=None):
        toggle_button = self.builder.get_object('ch2_status_button')
        if toggle_button.get_active() == True:
            self.set_channel_status("ON",2)
        else:
            self.set_channel_status("OFF",2)
    def on_ch3_status_button_toggled(self,button,data=None):
        toggle_button = self.builder.get_object('ch3_status_button')
        if toggle_button.get_active() == True:
            self.set_channel_status("ON",3)
        else:
            self.set_channel_status("OFF",3)
    def on_ch4_status_button_toggled(self,button,data=None):
        toggle_button = self.builder.get_object('ch4_status_button')
        if toggle_button.get_active() == True:
            self.set_channel_status("ON",4)
        else:
            self.set_channel_status("OFF",4)

    def on_skew_set1_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry1")
        val = float(skew_entry.get_text())
        if AWG.set_ch1_skew(val):
            print "CH1 skew set to",val,"ps."

    def on_skew_set2_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry2")
        val = float(skew_entry.get_text())
        if AWG.set_ch2_skew(val):
            print "CH2 skew set to",val,"ps."

    def on_skew_set3_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry3")
        val = float(skew_entry.get_text())
        if AWG.set_ch3_skew(val):
            print "CH3 skew set to",val,"ps."

    def on_skew_set4_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry4")
        val = float(skew_entry.get_text())
        if AWG.set_ch4_skew(val):
            print "CH4 skew set to",val,"ps."

    def on_skew_get1_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry1")
        val = AWG.get_ch1_skew()
        skew_entry.set_text(str(val))  
        
    def on_skew_get2_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry2")
        val = AWG.get_ch2_skew()
        skew_entry.set_text(str(val))    

    def on_skew_get3_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry3")
        val = AWG.get_ch3_skew()
        skew_entry.set_text(str(val))    

    def on_skew_get4_clicked(self,button,data=None):
        skew_entry = self.builder.get_object("skew_entry4")
        val = AWG.get_ch4_skew()
        skew_entry.set_text(str(val))          

    def on_window1_destroy(self, object, data=None):
        AWG._ins._visainstrument.clear()
        AWG._ins._visainstrument.close()   # Trying to close previous AWG session. 
        print "AWG GUI closed with cancel button."
        self.window.destroy()
        #gtk.main_quit()

    def on_num_seg_set_clicked(self, button, data=None):
        self.num_seg_entry = self.builder.get_object("num_seg_entry")
        self.num_seg = int(self.num_seg_entry.get_text())
        print "Number of segments set to",self.num_seg
        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        self.treeview_list.clear()
        for i in range(self.num_seg):
            self.treeview_list.append([i+1] + self.default_treeview_list)

    def on_time_units_box_changed(self,widget,data=None):
        index = widget.get_active()
        model = widget.get_model()
        self.time_units = model[index][1]
        print "Time units set to",self.time_units
        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        self.wav_obj.Change_time_units(self.time_units)
       

    def on_amp_units_box_changed(self,widget,data=None):
        index = widget.get_active()
        model = widget.get_model()
        self.amp_units = model[index][1]
        print "Amplitide units units set to",self.amp_units
        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        self.wav_obj.Change_amp_units(self.amp_units) 


    def on_awg_clock_set_clicked(self,button,data=None):
        self.awg_clock_entry = self.builder.get_object("awg_clock_entry")
        self.awg_clock = float(self.awg_clock_entry.get_text())
        self.wav_obj.setAWG_clock(self.awg_clock)
        #print "AWG Clock set to",self.awg_clock
        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        #only the set hard buttons change on the hardware
        #AWG.set_clock(self.awg_clock)  # Set AWG clock
    
    def on_max_amp_set_clicked(self,button,data=None):
        self.max_amp_entry = self.builder.get_object("max_amp_entry")
        self.max_amp = float(self.max_amp_entry.get_text())
        #print "Maximum Amplitude set to",self.max_amp
        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        
        #only the set hard buttons change on the hardware
        #AWG.set_ch1_amplitude(self.max_amp)  # Setting maximum needed amp on all AWG channels
        #AWG.set_ch2_amplitude(self.max_amp) 
        #AWG.set_ch3_amplitude(self.max_amp) 
        #AWG.set_ch4_amplitude(self.max_amp) 
        
    def on_awg_clock_set_hard_clicked(self,button,data=None):
        self.awg_clock_entry_hard = self.builder.get_object("awg_clock_entry_hard")
        self.awg_clock_hard = float(self.awg_clock_entry_hard.get_text())
        print "AWG Clock set to",self.awg_clock_hard
        if AWG.set_clock(self.awg_clock_hard):  # Set AWG clock
            label = self.builder.get_object("awg_settings_label")
            label.set_text("AWG Settings \n\n" + "AWG Clock : " + str(self.awg_clock_hard/1e6) + " MHz\n" + "Maximum Amplitude : " + str(self.max_amp_hard) + " V\n" + "Run Mode : " + str(self.runmode) + "\n")
    
    def on_max_amp_set_hard_clicked(self,button,data=None):
        self.max_amp_entry_hard = self.builder.get_object("max_amp_entry_hard")
        self.max_amp_hard = float(self.max_amp_entry_hard.get_text())
        print "Maximum Amplitude set to",self.max_amp_hard
        AWG.set_ch1_amplitude(self.max_amp_hard)  # Setting maximum needed amp on all AWG channels
        AWG.set_ch2_amplitude(self.max_amp_hard) 
        AWG.set_ch3_amplitude(self.max_amp_hard) 
        AWG.set_ch4_amplitude(self.max_amp_hard) 
        label = self.builder.get_object("awg_settings_label")
        label.set_text("AWG Settings \n\n" + "AWG Clock : " + str(self.awg_clock_hard/1e6) + " MHz\n" + "Maximum Amplitude : " + str(self.max_amp_hard) + " V\n" + "Run Mode : " + str(self.runmode) + "\n")

    def set_marker_from_input_m1(self,i,index):
        #i is the segment index along column
        #index is index along the row
        if self.treeview_list[i][index] == 'L':
            self.seg_list_m1 += [0.0]
        elif self.treeview_list[i][index] == 'H':
            self.seg_list_m1 += [1.0]
        else:
            raise Exception('Error in setting markers - input value must be L or H')

    def convert_marker(self,val):
        if val == 'L':
            return 0.0
        elif val == 'H':
            return 1.0
        else:
            raise Exception('Error in setting markers - input value must be L or H')
    
    def set_marker_from_input_m2(self,i,index):
        #i is the segment index along column
        #index is index along the row
        if self.treeview_list[i][index] == 'L':
            self.seg_list_m2 += [0.0]
        elif self.treeview_list[i][index] == 'H':
            self.seg_list_m2 += [1.0]
        else:
            raise Exception('Error in setting markers - input value must be L or H')

    def text_edited(self,widget,path,text,index):

        self.treeview_list[path][index] = text
        if 2 <=index <= 4:
            self.seg_list_a = []
            self.seg_list_m1 = []
            self.seg_list_m2 = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][2])]]
                self.set_marker_from_input_m1(i,3)
                self.set_marker_from_input_m2(i,4)

            self.wav_obj.setValuesCH1(*self.seg_list_a)
            self.wav_obj.setMarkersCH1(self.seg_list_m1,self.seg_list_m2)

        elif 5 <=index <= 7:
            self.seg_list_a = []
            self.seg_list_m1 = []
            self.seg_list_m2 = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][5])]]
                self.set_marker_from_input_m1(i,6)
                self.set_marker_from_input_m2(i,7)

            self.wav_obj.setValuesCH2(*self.seg_list_a)
            self.wav_obj.setMarkersCH2(self.seg_list_m1,self.seg_list_m2)
        elif 8 <=index <= 10:
            self.seg_list_a = []
            self.seg_list_m1 = []
            self.seg_list_m2 = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][8])]]
                self.set_marker_from_input_m1(i,9)
                self.set_marker_from_input_m2(i,10)
            
            self.wav_obj.setValuesCH3(*self.seg_list_a)
            self.wav_obj.setMarkersCH3(self.seg_list_m1,self.seg_list_m2)
        elif 11 <=index <= 13:
            self.seg_list_a = []
            self.seg_list_m1 = []
            self.seg_list_m2 = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][11])]]
                self.set_marker_from_input_m1(i,12)
                self.set_marker_from_input_m2(i,13)
              
            self.wav_obj.setValuesCH4(*self.seg_list_a)
            self.wav_obj.setMarkersCH4(self.seg_list_m1,self.seg_list_m2)
        #user only changes the time
        else:
            self.seg_list_a = []
            #channel 1
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][2])]]
            self.wav_obj.setValuesCH1(*self.seg_list_a)
            #channel 2
            self.seg_list_a = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][5])]]
            self.wav_obj.setValuesCH2(*self.seg_list_a)
            #channel 3
            self.seg_list_a = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][8])]]
            self.wav_obj.setValuesCH3(*self.seg_list_a)
            #channel 4
            self.seg_list_a = []
            for i in range(self.num_seg):
                self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][11])]]
            self.wav_obj.setValuesCH4(*self.seg_list_a)

    def convert_marker_to_float(self,val):
        if val == 'H':
            return 1.0
        else:
            return 0.0 

    def on_plot1_clicked(self,widget,data=None):

        points_list_a = [(0,float(self.treeview_list[0][2]))]
        points_list_m1 = [(0,self.convert_marker_to_float(self.treeview_list[0][3]))]
        points_list_m2 = [(0,self.convert_marker_to_float(self.treeview_list[0][4]))]
        t = 0
        for i in range(self.num_seg-1):
            t = t + float(self.treeview_list[i][1])
            points_list_a.append((t,float(self.treeview_list[i][2])))
            points_list_a.append((t,float(self.treeview_list[i+1][2])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i][3])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i+1][3])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i][4])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i+1][4])))
        t = t + float(self.treeview_list[self.num_seg - 1][1])
        points_list_a.append((t,float(self.treeview_list[self.num_seg - 1][2])))
        points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][3])))
        points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][4])))


        f, axarr = plt.subplots(3, sharex=True)
        for item in axarr:
            item.spines['top'].set_visible(False)
            item.spines['bottom'].set_visible(False)
        axarr[0].set_title("Channel 1")
        axarr[0].plot(*zip(*points_list_a),color='r',linewidth=1.0,label="Analog")
        axarr[0].legend()
        axarr[0].set_ylabel("Amplitide[" + self.amp_units + "]")
        axarr[1].plot(*zip(*points_list_m1),color='r',linewidth=1.0,label="Marker 1")
        axarr[1].legend()
        axarr[1].set_ylim([-0.1,1.1])
        axarr[2].plot(*zip(*points_list_m2),color='r',linewidth=1.0,label="Marker 2")
        axarr[2].set_ylim([-0.1,1.1])
        axarr[2].legend()
        axarr[2].set_xlabel("Time[" + self.time_units + "]")
        plt.show()

    def on_plot2_clicked(self,widget,data=None):
        points_list_a = [(0,float(self.treeview_list[0][5]))]
        points_list_m1 = [(0,self.convert_marker_to_float(self.treeview_list[0][6]))]
        points_list_m2 = [(0,self.convert_marker_to_float(self.treeview_list[0][7]))]
        t = 0
        for i in range(self.num_seg-1):
            t = t + float(self.treeview_list[i][1])
            points_list_a.append((t,float(self.treeview_list[i][5])))
            points_list_a.append((t,float(self.treeview_list[i+1][5])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i][6])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i+1][6])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i][7])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i+1][7])))
        t = t + float(self.treeview_list[self.num_seg - 1][1])
        points_list_a.append((t,float(self.treeview_list[self.num_seg - 1][5])))
        points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][6])))
        points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][7])))


        f, axarr = plt.subplots(3, sharex=True)
        for item in axarr:
            item.spines['top'].set_visible(False)
        axarr[0].set_title("Channel 2")
        axarr[0].plot(*zip(*points_list_a),color='g',linewidth=1.0,label="Analog")
        axarr[0].legend()
        axarr[0].set_ylabel("Amplitide[" + self.amp_units + "]")
        axarr[1].plot(*zip(*points_list_m1),color='g',linewidth=1.0,label="Marker 1")
        axarr[1].legend()
        axarr[1].set_ylim([-0.1,1.1])
        axarr[2].plot(*zip(*points_list_m2),color='g',linewidth=1.0,label="Marker 2")
        axarr[2].set_ylim([-0.1,1.1])
        axarr[2].legend()
        axarr[2].set_xlabel("Time[" + self.time_units + "]")
        plt.show()

    def on_plot3_clicked(self,widget,data=None):
        points_list_a = [(0,float(self.treeview_list[0][8]))]
        points_list_m1 = [(0,self.convert_marker_to_float(self.treeview_list[0][9]))]
        points_list_m2 = [(0,self.convert_marker_to_float(self.treeview_list[0][10]))]
        t = 0
        for i in range(self.num_seg-1):
            t = t + float(self.treeview_list[i][1])
            points_list_a.append((t,float(self.treeview_list[i][8])))
            points_list_a.append((t,float(self.treeview_list[i+1][8])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i][9])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i+1][9])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i][10])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i+1][10])))
        t = t + float(self.treeview_list[self.num_seg - 1][1])
        points_list_a.append((t,float(self.treeview_list[self.num_seg - 1][8])))
        points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][9])))
        points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][10])))


        f, axarr = plt.subplots(3, sharex=True)
        for item in axarr:
            item.spines['top'].set_visible(False)
        axarr[0].set_title("Channel 3")
        axarr[0].plot(*zip(*points_list_a),color='b',linewidth=1.0,label="Analog")
        axarr[0].legend()
        axarr[0].set_ylabel("Amplitide[" + self.amp_units + "]")
        axarr[1].plot(*zip(*points_list_m1),color='b',linewidth=1.0,label="Marker 1")
        axarr[1].legend()
        axarr[1].set_ylim([-0.1,1.1])
        axarr[2].plot(*zip(*points_list_m2),color='b',linewidth=1.0,label="Marker 2")
        axarr[2].set_ylim([-0.1,1.1])
        axarr[2].legend()
        axarr[2].set_xlabel("Time[" + self.time_units + "]")
        plt.show()

    def on_plot4_clicked(self,widget,data=None):
        points_list_a = [(0,float(self.treeview_list[0][11]))]
        points_list_m1 = [(0,self.convert_marker_to_float(self.treeview_list[0][12]))]
        points_list_m2 = [(0,self.convert_marker_to_float(self.treeview_list[0][13]))]
        t = 0
        for i in range(self.num_seg-1):
            t = t + float(self.treeview_list[i][1])
            points_list_a.append((t,float(self.treeview_list[i][11])))
            points_list_a.append((t,float(self.treeview_list[i+1][11])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i][12])))
            points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[i+1][12])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i][13])))
            points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[i+1][13])))
        t = t + float(self.treeview_list[self.num_seg - 1][1])
        points_list_a.append((t,float(self.treeview_list[self.num_seg - 1][11])))
        points_list_m1.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][12])))
        points_list_m2.append((t,self.convert_marker_to_float(self.treeview_list[self.num_seg - 1][13])))


        f, axarr = plt.subplots(3, sharex=True)
        for item in axarr:
            item.spines['top'].set_visible(False)
        axarr[0].set_title("Channel 4")
        axarr[0].plot(*zip(*points_list_a),color='c',linewidth=1.0,label="Analog")
        axarr[0].legend()
        axarr[0].set_ylabel("Amplitide[" + self.amp_units + "]")
        axarr[1].plot(*zip(*points_list_m1),color='c',linewidth=1.0,label="Marker 1")
        axarr[1].legend()
        axarr[1].set_ylim([-0.1,1.1])
        axarr[2].plot(*zip(*points_list_m2),color='c',linewidth=1.0,label="Marker 2")
        axarr[2].set_ylim([-0.1,1.1])
        axarr[2].legend()
        axarr[2].set_xlabel("Time[" + self.time_units + "]")
        plt.show()

    def on_awg_upload_clicked(self,button,data=None):

        AWG.set_clock(self.awg_clock)  # Set AWG clock
        AWG.set_ch1_amplitude(self.max_amp)  # Setting maximum needed amp on all AWG channels
        AWG.set_ch2_amplitude(self.max_amp) 
        AWG.set_ch3_amplitude(self.max_amp) 
        AWG.set_ch4_amplitude(self.max_amp) 
        print "AWG Clock set to",self.awg_clock
        print "Maximum Amplitude set to",self.max_amp

        AWG.send_waveform_object(Wav = self.wav_obj.CH4, path = 'C:\SEQwav\\')
        AWG.import_waveform_object(Wav = self.wav_obj.CH4, path = 'C:\SEQwav\\')
        AWG.import_waveform_object(Wav = self.wav_obj.CH4, path = 'C:\SEQwav\\')
        AWG.load_waveform(1, self.wav_obj.CH1.waveform_name, drive='C:', path='C:\SEQwav\\')
        AWG.load_waveform(2, self.wav_obj.CH2.waveform_name, drive='C:', path='C:\SEQwav\\')
        AWG.load_waveform(3, self.wav_obj.CH3.waveform_name, drive='C:', path='C:\SEQwav\\')
        AWG.load_waveform(4, self.wav_obj.CH4.waveform_name, drive='C:', path='C:\SEQwav\\')

    def on_save_waveform_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Save waveform",self.window,gtk.FILE_CHOOSER_ACTION_SAVE,(gtk.STOCK_SAVE,gtk.RESPONSE_ACCEPT,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_property("do-overwrite-confirmation",True)
        dialog.set_current_folder("~/")

        response = dialog.run()

        if response == gtk.RESPONSE_ACCEPT:
            #note that filename also contains the path
            filename = dialog.get_filename()
            #safety first
            if not filename.endswith(".txt"):
                filename += ".txt"
            f = open(filename,'w')
            #write the settings
            f.write("num_seg " + str(self.num_seg) + "\n")
            f.write("time_units " + str(self.time_units) + "\n")
            f.write("amp_units " + str(self.amp_units) + "\n")
            f.write("awg_clock " + str(self.awg_clock) + "\n")
            f.write("max_amp " +  str(self.max_amp) + "\n")
            
            #write the segments in the same format it is visible on the GUI
            for i in range(self.num_seg):
                line = ""
                for j in range(len(self.treeview_list[0])):
                    line += str(self.treeview_list[i][j]) + " "
                line += "\n"
                f.write(line)
            f.close()
        dialog.destroy()
    def on_load_waveform_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Open waveform",self.window,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_OPEN,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_current_folder("~/")

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filepath = dialog.get_filename()
            self.load_waveform(filepath,self.wav_obj)
            wav_label = self.builder.get_object("load_waveform_label")
            wav_label.set_text(filepath)
        dialog.destroy()

    def on_open_waveform1_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Open waveform",self.window,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_OPEN,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_current_folder("~/")

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filepath = dialog.get_filename()
            f = open(filepath)
            wav1_label = self.builder.get_object("wav1_label")
            wav1_label.set_text(filepath)
            print f
            f.close()
        dialog.destroy()

    def on_open_waveform2_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Open waveform",self.window,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_OPEN,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_current_folder("~/")

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filepath = dialog.get_filename()
            f = open(filepath)
            wav2_label = self.builder.get_object("wav2_label")
            wav2_label.set_text(filepath)
            print f
            f.close()
        dialog.destroy()


    #helper function
    #load a waveform from a txt file and stores the data in wav
    def load_waveform(self,filepath,wav):
        f = open(filepath,"r")
        #hard coded
        #DONT CHANGE 
        lines = f.readlines()
        #num_seg
        self.num_seg = int(lines[0].split()[1])
        print "Number of segments set to",self.num_seg
        
        #time and amp units
        self.time_units = lines[1].split()[1]
        self.amp_units = lines[2].split()[1]
        wav.Change_time_units(self.time_units)
        wav.Change_amp_units(self.amp_units) 
        print "Time units set to",self.time_units
        print "Amplitide units units set to",self.amp_units

        #awg_clock and max_amp
        self.awg_clock = float(lines[3].split()[1])
        self.max_amp = float(lines[4].split()[1])
        self.max_amp_tmp = float(lines[4].split()[1])
        #change the AWG_clock in the waveform object which determines the number of points
        wav.setAWG_clock(self.awg_clock)

        self.statusbar.push(self.context_id, "No. of Segments: " + str(self.num_seg) + " | Time Units: " + str(self.time_units) +  " | Amplitude Units: " + str(self.amp_units) + " | AWG Clock: " + str(self.awg_clock) + " | Max. Amplitude: " + str(self.max_amp)) 
        self.treeview_list.clear()

        for line in lines[5:]:
            self.treeview_list.append(line.split())

        self.seg_list_a = []
        self.seg_list_m1 = []
        self.seg_list_m2 = []
        for i in range(self.num_seg):
            self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][2])]]
            self.set_marker_from_input_m1(i,3)
            self.set_marker_from_input_m2(i,4)

        wav.setValuesCH1(*self.seg_list_a)
        wav.setMarkersCH1(self.seg_list_m1,self.seg_list_m2)
        self.seg_list_a = []
        self.seg_list_m1 = []
        self.seg_list_m2 = []
        for i in range(self.num_seg):
            self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][5])]]
            self.set_marker_from_input_m1(i,6)
            self.set_marker_from_input_m2(i,7)

        wav.setValuesCH2(*self.seg_list_a)
        wav.setMarkersCH2(self.seg_list_m1,self.seg_list_m2)

        self.seg_list_a = []
        self.seg_list_m1 = []
        self.seg_list_m2 = []
        for i in range(self.num_seg):
            self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][8])]]
            self.set_marker_from_input_m1(i,9)
            self.set_marker_from_input_m2(i,10)
        
        wav.setValuesCH3(*self.seg_list_a)
        wav.setMarkersCH3(self.seg_list_m1,self.seg_list_m2)
        self.seg_list_a = []
        self.seg_list_m1 = []
        self.seg_list_m2 = []
        for i in range(self.num_seg):
            self.seg_list_a += [[float(self.treeview_list[i][1]),float(self.treeview_list[i][11])]]
            self.set_marker_from_input_m1(i,12)
            self.set_marker_from_input_m2(i,13)
          
        wav.setValuesCH4(*self.seg_list_a)
        wav.setMarkersCH4(self.seg_list_m1,self.seg_list_m2)
    
    def load_waveform_seq_gen(self,filepath,wav):
        f = open(filepath,"r")
        #hard coded
        #DONT CHANGE 
        lines = f.readlines()
        #num_seg
        num_seg = int(lines[0].split()[1])
                #time and amp units
        time_units = lines[1].split()[1]
        amp_units = lines[2].split()[1]
        wav.Change_time_units(time_units)
        wav.Change_amp_units(amp_units) 

        #awg_clock and max_amp
        awg_clock = float(lines[3].split()[1])
        max_amp = float(lines[4].split()[1])

        #change the AWG_clock in the waveform object which determines the number of points
        wav.setAWG_clock(awg_clock)
        
        #max_amp_tmp stores it globally for use in sequence generation
        self.max_amp_tmp = float(lines[4].split()[1])

        #remove the header
        lines = lines[5:]
        seg_list_a = []
        seg_list_m1 = []
        seg_list_m2 = []
        for seg_no in range(num_seg):
            dat = lines[seg_no].split()
            seg_list_a += [[float(dat[1]),float(dat[2])]]
            seg_list_m1 += [self.convert_marker(dat[3])]
            seg_list_m2 += [self.convert_marker(dat[4])]
        wav.setValuesCH1(*seg_list_a)
        wav.setMarkersCH1(seg_list_m1,seg_list_m2)

        seg_list_a = []
        seg_list_m1 = []
        seg_list_m2 = []
        for seg_no in range(num_seg):
            dat = lines[seg_no].split()
            seg_list_a += [[float(dat[1]),float(dat[5])]]
            seg_list_m1 += [self.convert_marker(dat[6])]
            seg_list_m2 += [self.convert_marker(dat[7])]
        wav.setValuesCH2(*seg_list_a)
        wav.setMarkersCH2(seg_list_m1,seg_list_m2)

        seg_list_a = []
        seg_list_m1 = []
        seg_list_m2 = []
        for seg_no in range(num_seg):
            dat = lines[seg_no].split()
            seg_list_a += [[float(dat[1]),float(dat[8])]]
            seg_list_m1 += [self.convert_marker(dat[9])]
            seg_list_m2 += [self.convert_marker(dat[10])]
        wav.setValuesCH3(*seg_list_a)
        wav.setMarkersCH3(seg_list_m1,seg_list_m2)

        seg_list_a = []
        seg_list_m1 = []
        seg_list_m2 = []
        for seg_no in range(num_seg):
            dat = lines[seg_no].split()
            seg_list_a += [[float(dat[1]),float(dat[11])]]
            seg_list_m1 += [self.convert_marker(dat[12])]
            seg_list_m2 += [self.convert_marker(dat[13])]
        wav.setValuesCH4(*seg_list_a)
        wav.setMarkersCH4(seg_list_m1,seg_list_m2)

    def on_open_waveform1_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Open waveform",self.window,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_OPEN,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_current_folder("~/")

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filepath = dialog.get_filename()
            self.load_waveform_seq_gen(filepath,self.wav_obj_begin)
            wav_label = self.builder.get_object("wav1_label")
            wav_label.set_text(filepath)
        dialog.destroy()

    def on_open_waveform2_clicked(self,widget,data=None):
        dialog = gtk.FileChooserDialog("Open waveform",self.window,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_OPEN,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        dialog.set_current_folder("~/")

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filepath = dialog.get_filename()
            self.load_waveform_seq_gen(filepath,self.wav_obj_end)
            wav_label = self.builder.get_object("wav2_label")
            wav_label.set_text(filepath)
        dialog.destroy()
    def on_gen_seq_clicked(self,button,data=None):
        seq = self.wav_obj_begin.interpolate_to(self.num_ele,self.wav_obj_end)

        #the AWG clock and max amp are derived from the last waveform loaded, i.e. the end waveform generally
        AWG.set_clock(self.wav_obj_end.AWG_clock)
        self.awg_clock_hard = AWG.get_clock()
        self.max_amp_hard = self.max_amp_tmp
        

        AWG.set_ch1_amplitude(self.max_amp_hard)  # Setting maximum needed amp on all AWG channels
        AWG.set_ch2_amplitude(self.max_amp_hard) 
        AWG.set_ch3_amplitude(self.max_amp_hard) 
        AWG.set_ch4_amplitude(self.max_amp_hard) 
           
        for ch_num in xrange(len(seq)):
            for seq_elem in seq[ch_num]:
                #decide what max_amp to use
                seq_elem.rescaleAmplitude(self.max_amp_hard)
                AWG.send_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
                AWG.import_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')

         ## SET AWG
        AWG.set_sequence_mode_on()  # Tell the device to run in sequence mode (run_mode_sequence)
        AWG.set_seq_length(0)   # Clear all elements of existing sequence   
        AWG.set_seq_length(self.num_ele)  # Set wanted sequence length
        for ch in xrange(len(seq)):   # Iterating trough channels

            
            if 'CH1' in seq[ch][0].waveform_name:   # Checking to which channel sequence elements needs to be uploaded
                channel = 1                         # by checking the name of first element dedicated to specified channel
            elif 'CH2' in seq[ch][0].waveform_name:
                channel = 2
            elif 'CH3' in seq[ch][0].waveform_name:
                channel = 3
            elif 'CH4' in seq[ch][0].waveform_name:
                channel = 4

            for elem_num, seq_elem in enumerate(seq[ch]):   # Iterating trough sequence elements
                
                #if elem_num == 0: # If it is the FIRST element set TWAIT = 1 - wait for trigger
                    #AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name, TWAIT = 1)


                

                if elem_num == (len(seq[ch])-1): # If it is the last element set GOTOind=1 - return to first elem
                    AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name, GOTOind=1)
                    
                else:
                    AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name)
        

        label = self.builder.get_object("awg_settings_label")
        label.set_text("AWG Settings \n\n" + "AWG Clock : " + str(self.awg_clock_hard/1e6) + " MHz\n" + "Maximum Amplitude : " + str(self.max_amp_hard) + " V\n" + "Run Mode : " + str(self.runmode) + "\n")
    
    def on_set_num_ele_clicked(self,button,data=None):
        self.num_ele_entry = self.builder.get_object('num_ele_entry')
        self.num_ele = int(self.num_ele_entry.get_text())
        print "Number of elements in sequence set to",self.num_ele 

    def on_awg_run_hard_clicked(self,button,data=None):
            AWG.run()
            print "AWG on."
    def on_awg_stop_hard_clicked(self,button,data=None):
            AWG.stop()
            print "AWG off."

    def on_set_awg_runmode_hard_clicked(self,button,data=None):
        index = self.runmode_box.get_active()
        model = self.runmode_box.get_model()
        self.runmode = model[index][1]
        
        AWG.set_runmode(self.runmode)
        print "AWG Runmode set to",self.runmode

        label = self.builder.get_object("awg_settings_label")
        label.set_text("AWG Settings \n\n" + "AWG Clock : " + str(self.awg_clock_hard/1e6) + " MHz\n" + "Maximum Amplitude : " + str(self.max_amp_hard) + " V\n" + "Run Mode : " + str(self.runmode) + "\n")

         
