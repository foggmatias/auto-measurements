import visa
import automeasurements.instrument as instrument
import yaml


class programInstance:
    instrumentList = []
    rManager = ""
    
    

    def defaultSettings(self):
        with open("defaultConfig.yml", 'r') as configFile :
            self.settings = yaml.load(configFile)
            
    def loadSettings(self, filename):
        if not programInstance(filename,str): filename=str(filename)
        if not filename.endswith(".yml") : filename+=".yml"
        with open(filename, 'r') as configFile:
            if configFile: yaml.load(configFile)
            else: raise Exception('Config file "'+configFile+'" not found.')
    
    def changeSettings(self, settings): # Settings Format: settings=[[category][setting][value],...]
        for setting in settings:
                if self.settings[setting[0]][setting[1]] : self.settings[setting[0]][setting[1]]=setting[2]
                else: print('Invalid setting.')
    
    def saveSettings(self, filename):
        if not programInstance(filename,str): filename=str(filename)
        if not filename.endswith(".yml") : filename+=".yml"
        with open(filename,"w+") as configFile:
            if configFile: yaml.dump(self.settings, configFile)
            else: raise Exception('Config file "'+configFile+'" could not be created.')    

    def __init__(self):
        self.loadError=False
        self.rManager=visa.ResourceManager() 
        self.instrumentAddresses = self.rManager.list_resources() 
        self.configFile="defaultConfig.yml"
        
        for addr in self.instrumentAddresses:
            inst=instrument.instrument(addr,self.rManager)
            inst.instResource.write("*rst; status:preset; *cls")
            self.instrumentList.append(inst)

        for x in self.instrumentList:
            if x.type=="OSC":
                self.oscilloscope=x
                break
         
        for x in self.instrumentList:
            if x.type=="SGN":
                self.generator=x
                break
        
        if self.instrumentList :     
            print("Connected instruments:")
            for x in self.instrumentList: 
                print(x.instAddress, x.instID, x.type)
            if self.oscilloscope : print("Oscilloscope defaulted to", self.oscilloscope.instID) #TODO: add device selection support
            if self.generator : print("Signal generator defaulted to", self.generator.instID)
        else : print("No instruments detected. Check National Instruments NIMAX program for details.")

        # Load settings from config file
        self.defaultSettings()
        try: self.oscilloscope.updateSettings(self, True)
        except: 
            print("No oscilloscope was detected! Make sure it is properly connected and NI VISA software recognises it.")
            self.loadError=True
        try: self.generator.updateSettings(self, True)
        except: 
            print("No generator was detected! Make sure it is properly connected and NI VISA software recognises it.")
            self.loadError=True


