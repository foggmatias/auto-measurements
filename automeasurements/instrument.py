import visa
import pyvisa
import time
import automeasurements.tools as tools
import numpy
import automeasurements.programInstance as programInstance

class instrument:
     
    def __init__(self, address, rm):
        self.delay=0.0001
        self.instResource=rm.open_resource(address)
        self.instAddress=address
        self.instID = self.instResource.query('*IDN?')
        
        if ("DSO" in self.instID):
            self.type="OSC"
        else:
            self.type="SGN"

    def updateSettings(self, thisInstance, init=False):
        self.delay=thisInstance.settings["instrument"]["delay"]
        if self.type == "OSC":
            # Probe 1
            if init or thisInstance.oscilloscope.ask(":CHAN1:DISP?"):
                probe1=thisInstance.settings["probe1"]
                if probe1["coupling"] == "DC" or probe1["coupling"] == "AC": thisInstance.oscilloscope.send(":CHAN1:COUP "+probe1["coupling"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe1["coupling"]))
                if probe1["ratio"] == "X1" or probe1["ratio"] == "X10": thisInstance.oscilloscope.send(":CHAN1:PROB "+probe1["ratio"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe1["ratio"]))
                if probe1["vernier"] == "0" or probe1["vernier"] == "1": thisInstance.oscilloscope.send(":CHAN1:VERN "+probe1["vernier"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe1["vernier"]))
                if probe1["invert"] == "0" or probe1["invert"] == "1": thisInstance.oscilloscope.send(":CHAN1:INV "+probe1["invert"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe1["vernier"]))
                if probe1["BWL"] == "0" or probe1["BWL"] == "1": thisInstance.oscilloscope.send(":CHAN1:BWL "+probe1["BWL"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe1["vernier"]))
            # Probe 2
            if init or thisInstance.oscilloscope.ask(":CHAN2:DISP?"):
                probe2=thisInstance.settings["probe2"]
                if probe2["coupling"] == "DC" or probe2["coupling"] == "AC": thisInstance.oscilloscope.send(":CHAN2:COUP "+probe2["coupling"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe2["coupling"]))
                if probe2["ratio"] == "X1" or probe2["ratio"] == "X10": thisInstance.oscilloscope.send(":CHAN2:PROB "+probe2["ratio"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe2["ratio"]))
                if probe2["vernier"] == "0" or probe2["vernier"] == "1": thisInstance.oscilloscope.send(":CHAN2:VERN "+probe2["vernier"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe2["vernier"]))
                if probe2["invert"] == "0" or probe2["invert"] == "1": thisInstance.oscilloscope.send(":CHAN2:INV "+probe2["invert"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe2["invert"]))
                if probe2["BWL"] == "0" or probe2["BWL"] == "1": thisInstance.oscilloscope.send(":CHAN2:BWL "+probe2["BWL"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe2["BWL"]))
            # Probe 3
            if init or thisInstance.oscilloscope.ask(":CHAN3:DISP?"):
                probe3=thisInstance.settings["probe3"]
                if probe3["coupling"] == "DC" or probe3["coupling"] == "AC": thisInstance.oscilloscope.send(":CHAN3:COUP "+probe3["coupling"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe3["coupling"]))
                if probe3["ratio"] == "X1" or probe3["ratio"] == "X10": thisInstance.oscilloscope.send(":CHAN3:PROB "+probe3["ratio"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe3["ratio"]))
                if probe3["vernier"] == "0" or probe3["vernier"] == "1": thisInstance.oscilloscope.send(":CHAN3:VERN "+probe3["vernier"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe3["vernier"]))
                if probe3["invert"] == "0" or probe3["invert"] == "1": thisInstance.oscilloscope.send(":CHAN3:INV "+probe3["invert"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe3["invert"]))
                if probe3["BWL"] == "0" or probe3["BWL"] == "1": thisInstance.oscilloscope.send(":CHAN3:BWL "+probe3["BWL"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe3["BWL"]))
             # Probe 4
            if init or thisInstance.oscilloscope.ask(":CHAN4:DISP?"):
                probe4=thisInstance.settings["probe4"]
                if probe4["coupling"] == "DC" or probe4["coupling"] == "AC": thisInstance.oscilloscope.send(":CHAN4:COUP "+probe4["coupling"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe4["coupling"]))
                if probe4["ratio"] == "X1" or probe4["ratio"] == "X10": thisInstance.oscilloscope.send(":CHAN4:PROB "+probe4["ratio"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe4["ratio"]))
                if probe4["vernier"] == "0" or probe4["vernier"] == "1": thisInstance.oscilloscope.send(":CHAN4:VERN "+probe4["vernier"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe4["vernier"]))
                if probe4["invert"] == "0" or probe4["invert"] == "1": thisInstance.oscilloscope.send(":CHAN4:INV "+probe4["invert"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe4["invert"]))
                if probe4["BWL"] == "0" or probe4["BWL"] == "1": thisInstance.oscilloscope.send(":CHAN4:BWL "+probe4["BWL"])
                else: raise Exception("Settings file == corrupt. Invalid setting: "+str(probe4["BWL"]))
            # Acquire
            acquire=thisInstance.settings["acquire"]
            if acquire["mode"] == "NORM" or acquire["mode"] == "AVER" or acquire["mode"] == "HRES" or acquire["mode"] == "PEAK": thisInstance.oscilloscope.send(":ACQ:TYPE "+acquire["mode"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(acquire["mode"]))
            # Trigger
            trigger=thisInstance.settings["trigger"]
            if trigger["source"] == "CHAN1" or trigger["source"] == "CHAN2" or trigger["source"] == "CHAN3" or trigger["source"] == "CHAN4": thisInstance.oscilloscope.send(":TRIG:SOUR "+trigger["source"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(trigger["source"]))
            if trigger["mode"] == "NORM" or trigger["mode"] == "AUTO" : thisInstance.oscilloscope.send(":TRIG:MODE "+trigger["mode"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(trigger["mode"]))
            if trigger["HFReject"] == "0" or trigger["HFReject"] == "1" : thisInstance.oscilloscope.send(":TRIG:HFR "+trigger["HFReject"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(trigger["HFReject"]))
            if trigger["coupling"] == "DC" or trigger["coupling"] == "AC" : thisInstance.oscilloscope.send(":TRIG:COUP "+trigger["coupling"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(trigger["coupling"]))
            if trigger["noiseReject"] == "0" or trigger["noiseReject"] == "1" : thisInstance.oscilloscope.send(":TRIG:NREJ "+trigger["noiseReject"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(trigger["noiseReject"]))
        elif self.type == "SGN":
            generator=thisInstance.settings["generator"]
            if generator["impedance"] == "50" or generator["impedance"] == "INF" : thisInstance.generator.send("OUTP:LOAD "+generator["impedance"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(generator["impedance"]))
            if generator["waveform"] == "SIN" or generator["waveform"] == "SQU" or generator["waveform"] == "TRI" : thisInstance.generator.send("FUNC "+generator["waveform"])
            else: raise Exception("Settings file == corrupt. Invalid setting: "+str(generator["waveform"]))

    def send(self, string) :
        self.instResource.write(string)
        time.sleep(self.delay)
    
        
    def ask(self, string) :
        returnValue=self.instResource.query(string)
        time.sleep(self.delay)
        returnValue=float(returnValue.replace('\n',''))
        return returnValue

    def getValue(self, value, noiseTolerance, thisInstance, chanInId, chanOutId=None, verbose=True): # ChanOut only required for phase calculation
        minSamples=thisInstance.settings["sampling"]["minSamples"]
        maxSamples=thisInstance.settings["sampling"]["maxSamples"]
        measTimeSpacing=thisInstance.settings["sampling"]["measTimeSpacing"]
        returnArray=[]
        
        if value is "vpp" : # Measure Vpp
            thisInstance.oscilloscope.send(":MEAS:VPP "+chanInId)
            for n in range(minSamples) : 
                returnArray.append(thisInstance.oscilloscope.ask(":MEAS:VPP?"))
                time.sleep(measTimeSpacing*numpy.random.rand())
            while numpy.std(returnArray) > (numpy.mean(returnArray, dtype=numpy.float64)*noiseTolerance) :
                returnArray.append(thisInstance.oscilloscope.ask(":MEAS:VPP?"))
                time.sleep(measTimeSpacing*numpy.random.rand())
                if len(returnArray) > maxSamples :
                    break
            if verbose: print("Peak-to-peak voltage samples taken for "+chanInId+": "+str(len(returnArray)))
        elif value is "phase" : # Measure phase
            thisInstance.oscilloscope.send(":MEAS:PHAS "+chanInId+","+chanOutId)
            for n in range(minSamples) :   
                ph=thisInstance.oscilloscope.ask("MEAS:PHAS?")
            
                if ph > 180 : ph = ph-180 
                elif ph < -180 : ph = ph+180

                returnArray.append((-1)*ph)
            while numpy.std(returnArray) > numpy.abs((numpy.mean(returnArray, dtype=numpy.float64)*noiseTolerance)) :
                returnArray.append(-1*(thisInstance.oscilloscope.ask(":MEAS:PHAS?")))
                time.sleep(measTimeSpacing*numpy.random.rand())
                if len(returnArray) > maxSamples :
                    break
            if verbose: print("Phase samples taken: "+str(len(returnArray)))
        else : raise Exception('getValue: Unrecognised value type: "'+value+'". Try Vpp or phase.')
        
        if verbose :
            print("Values are:")
            print(returnArray)
        returnArray=tools.reject_outliers(returnArray)
        meanReturnValue=numpy.mean(returnArray, dtype=numpy.float64)
        if verbose :
            print("Values after filtering outliers are:")
            print(returnArray)
            print("Mean= "+str(meanReturnValue)+", standard deviation= "+str(numpy.std(returnArray)))
        
        return meanReturnValue

class channel :
     def __init__(self, idn) :
         self.id=idn
         if idn is 1 : self.id="CHAN1"
         if idn is 2 : self.id="CHAN2"
         if idn is 3 : self.id="CHAN3"
         if idn is 4 : self.id="CHAN4"

      

                
        



    


