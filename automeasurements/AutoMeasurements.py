import visa
import automeasurements.instrument as instrument
import automeasurements.programInstance as programInstance
import numpy
import matplotlib.pyplot as plt
import time
import configparser
import io
import automeasurements.tools as tools
from scipy import interpolate as interp
import pandas as pd
from matplotlib.widgets import SpanSelector
from collections.abc import Iterable




def getPoint(freq, chanIn, chanOutList, tEst=0.001, noiseTolerance=0.1, thisInstance=None):
    # Get settings from instance
    vClearance=thisInstance.settings["sampling"]["vClearance"]
    periods=thisInstance.settings["sampling"]["periods"]
    verbose=thisInstance.settings["console"]["verbose"]
    #freq=points[currentStep-1]
    if verbose : print("---------")
    if verbose : print("Frequency point: "+str(freq))
    thisInstance.generator.send("FREQ "+str(freq))


    # Adjust voltage range for both channels based on their Vpp values
    thisInstance.oscilloscope.send(":MEAS:VPP "+chanIn.id) 
    vRangeIn=thisInstance.oscilloscope.ask(":MEAS:VPP?")
    while numpy.abs(vRangeIn)>10000:
        range=thisInstance.oscilloscope.ask(":"+chanIn.id+":RANG?")
        thisInstance.oscilloscope.send(":"+chanIn.id+":RANG "+str(range*1.5))
        thisInstance.oscilloscope.send(":MEAS:VPP "+chanIn.id)
        vRangeIn=thisInstance.oscilloscope.ask(":MEAS:VPP?")
    vRangeIn=(1+vClearance)*vRangeIn
    thisInstance.oscilloscope.send(":"+chanIn.id+":RANG "+str(vRangeIn))
    
    if not isinstance(chanOutList, Iterable): chanOutList=[chanOutList]
    for chanOut in chanOutList:
        thisInstance.oscilloscope.send(":MEAS:VPP "+chanOut.id) 
        vRangeOut=thisInstance.oscilloscope.ask(":MEAS:VPP?")
        while numpy.abs(vRangeOut)>10000:
            range=thisInstance.oscilloscope.ask(":"+chanOut.id+":RANG?")
            thisInstance.oscilloscope.send(":"+chanOut.id+":RANG "+str(range*1.5))
            thisInstance.oscilloscope.send(":MEAS:VPP "+chanOut.id)
            vRangeOut=thisInstance.oscilloscope.ask(":MEAS:VPP?")
        vRangeOut=(1+vClearance)*vRangeOut
        thisInstance.oscilloscope.send(":"+chanOut.id+":RANG "+str(vRangeOut))

    # Adjust timebase range for both channels based on their periods 
    thisInstance.oscilloscope.send(":MEAS:FREQ "+chanIn.id) 
    tFreqIn=thisInstance.oscilloscope.ask(":MEAS:FREQ?")
    tFreqOut=[]
    for chanOut in chanOutList:
        thisInstance.oscilloscope.send(":MEAS:FREQ "+chanOut.id) 
        tFreqOut.append(thisInstance.oscilloscope.ask(":MEAS:FREQ?"))

    tRange=periods/min(tFreqIn,min(tFreqOut))
    thisInstance.oscilloscope.send(":TIM:RANG "+str(tRange))
    
    time.sleep(tEst)

    # Obtain n samples per frequency point, average and store them # TODO: implement variable sample quantity based on samples taken
    # TODO: implement these functions in a generic method
    # Measure Vpp of in signal with a standard deviation less than noiseTolerance different from the signal
    vIn=thisInstance.oscilloscope.getValue("vpp",noiseTolerance,thisInstance,chanIn.id,None,verbose)
    
    vOutList=[]
    ratio=[]
    phase=[]
   # Measuring Vpp of out signal with a deviation less than noiseTolerance different from the signal
    for chanOut in chanOutList:
        vOut=thisInstance.oscilloscope.getValue("vpp",noiseTolerance,thisInstance,chanOut.id,None,verbose)
        vOutList.append(vOut)
    # Measure phase difference with a deviation less than noiseTolerance different from the signal
        phase.append(thisInstance.oscilloscope.getValue("phase",noiseTolerance,thisInstance,chanIn.id,chanOut.id,verbose))    
    # Calculate ratio
        ratio.append(20*numpy.log10(vOut/vIn))
    
    data=[freq, vIn]+vOutList+phase+ratio
    if len(vOutList) is 1: columns=["Frequency","Vpp In","Vpp Out","Phase","Ratio"]
    elif len(vOutList) is 2: columns=["Frequency","Vpp In","Vpp Out "+chanOutList[0].id,"Vpp Out "+chanOutList[1].id,"Phase "+chanOutList[0].id,"Phase "+chanOutList[1].id,"Ratio "+chanOutList[0].id,"Ratio "+chanOutList[1].id]
    elif len(vOutList) is 3: columns=["Frequency","Vpp In","Vpp Out "+chanOutList[0].id,"Vpp Out "+chanOutList[1].id,"Vpp Out "+chanOutList[2].id,"Phase "+chanOutList[0].id,"Phase "+chanOutList[1].id,"Phase "+chanOutList[2].id,"Ratio "+chanOutList[0].id,"Ratio "+chanOutList[1].id,"Ratio "+chanOutList[2].id]
    # Generate matrix of k x 5 with data from run
    run=pd.DataFrame([data],columns=columns)

    return run
  
def math(dataframe, operation, chanOutList):
    
    description=operation+" of "
    for string in chanOutList:
            description+=string
            description+=" "
    if operation == "+":
       if len(chanOutList) is 2: dataframe[description]=dataframe["Vpp Out "+chanOutList[0]]+dataframe["Vpp Out "+chanOutList[1]]
       elif len(chanOutList) is 3: dataframe[description]=dataframe["Vpp Out "+chanOutList[0]]+dataframe["Vpp Out "+chanOutList[1]]+dataframe["Vpp Out "+chanOutList[2]]
    elif operation == "-":
       if len(chanOutList) is 2: dataframe[description]=dataframe["Vpp Out "+chanOutList[1]]-dataframe["Vpp Out "+chanOutList[0]]
       elif len(chanOutList) is 3: dataframe[description]=dataframe["Vpp Out "+chanOutList[2]]-dataframe["Vpp Out "+chanOutList[1]]-dataframe["Vpp Out "+chanOutList[0]]
    elif operation == "*":
       if len(chanOutList) is 2: dataframe[description]=dataframe["Vpp Out "+chanOutList[1]]*dataframe["Vpp Out "+chanOutList[0]]
       elif len(chanOutList) is 3: dataframe[description]=dataframe["Vpp Out "+chanOutList[2]]*dataframe["Vpp Out "+chanOutList[1]]*dataframe["Vpp Out "+chanOutList[0]]
    dataframe["Ratio of "+description]=20*numpy.log10(dataframe[description]/dataframe["Vpp In"])
    return dataframe

def exportData(dataframe, format="csv", filename=""):
    timestr = time.strftime("%d%m%Y-%H%M%S")
    if filename=="":filename="BodeData-"+timestr
    try:
        if format == "csv": dataframe.to_csv(filename+"."+format, encoding='utf-8', index=False, sep="\t")
        elif format == "xlsx": 
            if not isinstance(dataframe, list): dataframe.to_excel(filename+"."+format)
            else:
                with pd.ExcelWriter(filename+"."+format) as writer:
                    for df in dataframe:
                        df.to_excel(writer, sheet_name=df.name, sep="\t")
        elif format == "clipboard": dataframe.to_clipboard(excel=False)
        elif format == "clipboard": dataframe.to_clipboard(excel=True)
    except: print("Could not export data to "+filename+"."+format)
    else: print("Data exported to "+filename+"."+format)

def addToFigure(dataframe, figure=None, phase=True, ratio=True, separately=False, kind="line", color=None):
   plt.legend(loc="best")
   
   frequency=dataframe["Frequency"].tolist()
   ratio=dataframe["Ratio"].tolist()
   phase=dataframe["Phase"].tolist()
   
   if not figure: figure=plt.figure()
   ax1 = figure.add_subplot(1,1,1)
   ax1.set_title("Bode Diagram")
   if not color: color1 = 'tab:red'
   else: color1 ='tab:'+color
   ax1.set_xlabel('Frequency [Hz]')
   ax1.set_ylabel('Phase [deg]', color=color1)
   ax1.set_xscale('log')
   ax1.plot(frequency, phase, color=color1, marker="o")
   ax1.tick_params(axis='y', labelcolor=color1)
   ax1.grid(True,"both")
   
   ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
   
   if not color: color2 = 'tab:blue'
   else: color2 ='tab:'+color
   ax2.set_ylabel('Ratio [dB]', color=color2)  # we already handled the x-label with ax1
   ax2.plot(frequency, ratio, color=color2, marker="o")
   ax2.tick_params(axis='y', labelcolor=color2)
   ax2.grid(True,"both")     
   
   figure.tight_layout()  # otherwise the right y-label is slightly clipped
   
   return figure
         
def measureBode(dataframe=None, startfreq=100, stopfreq=100000, center=None, span=None, samp=10, points=None, waveform=None, mode="Normal", vpp=2, tEst=0.001, cIn=1, cOutList=[3], noiseTolerance=0.1, thisInstance=None, autoOff=False, scale="Logarithmic"):
    
    # Get necessary settings from instance
    vClearance=2*thisInstance.settings["sampling"]["vClearance"]
    periods=thisInstance.settings["sampling"]["periods"]
    maxTries=thisInstance.settings["sampling"]["maxTries"]
    verbose=thisInstance.settings["console"]["verbose"]
    

    # Set channels for transfer function
    chanIn=instrument.channel(cIn)
    chanOutList=[]
    for cOut in cOutList:
        chanOutList.append(instrument.channel(cOut))
    
    # Only display channels that are to be used
    allChannels=["CHAN1","CHAN2","CHAN3","CHAN4"]
    for chanOut in chanOutList:
        thisInstance.oscilloscope.send(":"+chanOut.id+":DISP ON")
        for chan in allChannels: 
            if chan==chanOut.id: allChannels.remove(chan)
    for chan in allChannels: thisInstance.oscilloscope.send(":"+chan+":DISP OFF")

    # Set array of frequency points to measure
    if not points: # If point values are not passed as argument
        if span and not center: stopfreq=startfreq+span
        if span and center:
            startfreq=center-span
            stopfreq=center+span
        if scale == "Logarithmic": points=numpy.logspace(numpy.log10(startfreq),numpy.log10(stopfreq),samp)
        elif scale == "Linear": points=numpy.linspace(startfreq,stopfreq,samp)
    points=points.tolist()
    

    # Set generator waveform type 
    if waveform is not None: thisInstance.generator.send("FUNC "+waveform)
        

    # Set initial generator values
    thisInstance.generator.send("VOLT "+str(vpp)+" VPP")
    thisInstance.generator.send("FREQ "+str(points[0]))
    thisInstance.generator.send(":OUTP ON")
  
    time.sleep(0.5)
    #thisInstance.oscilloscope.send("TRIG:LIFIF")

    # Autoscale
    #thisInstance.oscilloscope.send(":AUT")
    
   
    # Set vertical offsets to zero
    thisInstance.oscilloscope.send(":"+chanIn.id+":OFFS 0")
    for chanOut in chanOutList:
        thisInstance.oscilloscope.send(":"+chanOut.id+":OFFS 0")
    time.sleep(1)
    # Set trigger to generator channel
    thisInstance.oscilloscope.send(":TRIG:SOUR "+chanIn.id)
    
    # Set oscilloscope vertical range. WARNING! This will not work for amplifying circuits. TO-DO: Maybe take as reference the greatest vpp after autoscale?
    vRangeIn=thisInstance.generator.ask("VOLT?")
    vRangeIn=(1+vClearance)*vRangeIn
    thisInstance.oscilloscope.send(":"+chanIn.id+":RANG "+str(vRangeIn))
     
    vRangeOut=thisInstance.generator.ask("VOLT?")
    vRangeOut=(1+vClearance)*vRangeOut
    for chanOut in chanOutList:
        thisInstance.oscilloscope.send(":"+chanOut.id+":RANG "+str(vRangeOut))

    tRange=periods/thisInstance.generator.ask("FREQ?")
    thisInstance.oscilloscope.send(":TIM:RANG "+str(tRange))
    
    time.sleep(0.2)
  
    
    currentStep=0
    
    # Perform a frequency sweep and obtain the measurements for each frequency point
    while mode == "Normal":
        freq=points[currentStep]
        
        if verbose : 
            print("-----------------------------")
            print("Run "+str(currentStep))
        
        run=getPoint(freq, chanIn, chanOutList, tEst, noiseTolerance, thisInstance)
        
        if dataframe is None: dataframe=run # Create a dataframe is none is passed as argument
        else : dataframe=dataframe.append(run,ignore_index=True)
        
        currentStep=currentStep+1
        if currentStep>=len(points): break

    if autoOff : thisInstance.generator.send(":OUTP OFF")

    dataframe.sort_values(by=["Frequency"],inplace=True)
    
    return dataframe.copy()




#thisInstance = programInstance.programInstance()
##plt.style.use('ggplot')
#if thisInstance.generator and thisInstance.oscilloscope : 
#    thisInstance.oscilloscope.updateSettings(thisInstance, init=True)
#    thisInstance.generator.updateSettings(thisInstance, init=True)
#    global measuredDF
#    measuredDF=measureBode()
#    figure=addToFigure(measuredDF)
#    exportData(measuredDF)
#    
#    def onselect(xmin, xmax):
#        global measuredDF
#        measuredDF=measureBode(measuredDF,startfreq=xmin,stopfreq=xmax)
#        figure=addToFigure(measuredDF)
#        plt.show()
#    cursor = MultiCursor(figure.get_axes(), useblit=True, color='red', linewidth=2)
#    span = SpanSelector(figure.gca(), onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))
#    plt.show()
#    
#
#
#time.sleep(1)
#
    #bodedata=bode()
    #phase=[]
    #ratio=[]
    #frequency=[]
    #for vector in bodedata :
    #    frequency.append(vector[0])
    #    phase.append(vector[3])
    #    ratio.append(vector[4])
    #plt.semilogx(frequency, ratio,label="Ratio")
    #plt.semilogx(frequency, phase,label="Phase")
    #plt.title("Bode Diagram")
    #plt.xlabel("Frequency [Hz]")
    #plt.legend(loc="best")
    #plt.show()
    #time.sleep(1)

