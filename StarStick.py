import pynput.keyboard as pk
import pynput.mouse as pm
import time as t
import tkinter as tk
import tkinter.font as tkF
import misc
import os
import SetupDevice as sDevice
import SetupMonitor as sMonitor
from PIL import Image
from PIL import ImageTk
import joystickapi
import msvcrt

import cProfile
import pstats

c = pk.Controller()
k = pk.Key
m = pm.Controller()
b = pm.Button

appRunning = True
NewSettingWindow = True
defaultColor = '#F0F0F0'
darkerColor = '#D0D0D0'
fpsDelta = .5/60

testButton = False
TestDeviceSelectedIndex = 0

TestButtonLabels = []
TestButtonNumLabels = []

TestAxisLabels = []
TestAxisNumLabels = []

Pause = True

#image = Image.open("nhr_logo.png")
#image = image.resize((100, 100), Image.Resampling.LANCZOS)

misc.thisSessionDevices = {}

if misc.getSetting('configured') is None:
    misc.setSetting('configured', False)


currentMonitorPreset = {}

###########    MOUSE

Mouse_DZ_X=[1228,1332]# borders of deadzone
Mouse_DZ_Y=[668,772]
Mouse_Center=[1280,720]
Mouse_B_X=[774,1786]# borders of the whole 'C' interface
Mouse_B_Y=[214,1226]

initialMonitor = [2560,1440]
'''
Left_m = Mouse_DZ_X[0] - Mouse_B_X[0] # Actual movement range of pointer inside the interface
Right_m = Mouse_B_X[1] - Mouse_DZ_X[1]
Up_m = Mouse_DZ_Y[0] - Mouse_B_Y[0]
Down_m = Mouse_B_Y[1] - Mouse_DZ_Y[1]
'''
MouseX = Mouse_DZ_X[0] - Mouse_B_X[0] # Actual movement range of pointer inside the interface
MouseY = Mouse_DZ_Y[0] - Mouse_B_Y[0]

MouseXa = 0 # <- the same thing, but after Screen Resolution adjustments, A - means Adjusted
MouseYa = 0
MouseCen = [0,0]
MouseDZx = [0,0]
MouseDZy = [0,0]
'''
Left_mA = 0 # <- the same thing, but after Screen Resolution adjustments, A - means Adjusted
Right_mA = 0
Up_mA = 0
Down_mA = 0
'''
################ Joystick (Device Axes)
AxisCen = 32768 # 65535
AxisMax = 65535
'''
Joystick_X_left = 0 # Joystick movement range
Joystick_X_right = 0
Joystick_X_up = 0 
Joystick_X_down = 0
'''

JoystickX = 0
JoystickY = 0

Joystick_DZ_X=[-1200,1200] # Deadzones
Joystick_DZ_Y=[-1200,1200]



#misc.set_up_logger()

def pause():
    global pauseL, Pause

    if Pause:
        Pause = False
        pauseL.config(text="A C T I V E", bg='#fff', fg='#000')

    else:
        Pause = True
        pauseL.config(text="P A U S E D", bg='#f00', fg='#fff')
        

    misc.root.update_idletasks()
    misc.root.update()
    t.sleep(.5)

def getCurve (x):
    a=.9
#   a*x^{5}+(1-a)*x
    
    return (a*x*x*x*x*x + (1-a)*x)

def initMonitorPreset():
    global currentMonitorPreset, MonitorBtn

    if misc.getSetting('currentPreset') is None:
        currentMonitorPreset = misc.defaultPreset
    else:
        id = str(misc.getSetting('currentPreset'))
        
        currentMonitorPreset =  misc.getSetting('presets')[id]
    
    MonitorBtn.config(text=currentMonitorPreset['str'])

def setOthers(x,y):
    sDevice.rootSizeX = x
    sDevice.rootSizeY = y*3

    sMonitor.rootSizeX = x
    sMonitor.rootSizeY = y*2

def tKroot():

    misc.root

    global rootSizeX, rootSizeY
    rootSizeX = 470
    rootSizeY = 220

    setOthers(rootSizeX,rootSizeY)

    misc.root = tk.Tk()
    misc.root.title("StarStick")
    misc.root.geometry(f"{rootSizeX}x{rootSizeY}")

    menu = tk.Menu(misc.root)
    item = tk.Menu(menu)

    item.add_command(label='Setup Device', command=sDevice.start)
    item.add_command(label='Setup Monitor', command=sMonitor.start)    
    item.add_command(label='Bind Buttons', command=sDevice.start)
    item.add_command(label='_Actions -notWorking', command=sDevice.start)
    item.add_command(label='_Bind Axises -notWorking', command=sDevice.start)

    menu.add_cascade(label='Settings', menu=item)
    misc.root.config(menu=menu)
    misc.root.protocol("WM_DELETE_WINDOW", on_closing)

    DeviceFrame = tk.Frame(misc.root, width= rootSizeX, height=rootSizeY/4, pady=3)
    DeviceFrame.grid(row=0, column=0,columnspan=2, sticky="ew")

    global TestFrameBtn
    TestFrameBtn = tk.Frame(misc.root, width= rootSizeX, height=0, pady=3,padx=20)
    TestFrameBtn.grid(row=1, column=0, columnspan=2, sticky="ew")
    
    global TestFrameAx
    TestFrameAx = tk.Frame(misc.root, width= rootSizeX, height=0, pady=3,padx=20)
    TestFrameAx.grid(row=2, column=0, columnspan=2, sticky="ew")


    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=misc.font)

    # region Device Selector

    # Create Label 
    DeviceLabel = tk.Label( DeviceFrame , text = "Selected Device: ") 
    DeviceLabel.grid(row = 0, column = 0, sticky = tk.W, pady = 2,padx=10)

    detectDevices()

    NoDevDet='No Devices Detected'

    # Dropdown menu options
    if misc.thisSessionDevices is None:
        misc.DevicesDropList = [NoDevDet]
    else:
        misc.DevicesDropList = []
        for device in misc.thisSessionDevices:
            misc.DevicesDropList.append(misc.thisSessionDevices[device]['name'])
    
    global clicked
    # datatype of menu text 
    clicked = tk.StringVar()
    

    print(misc.thisSessionDevices)


    # initial menu text
    if misc.thisSessionDevices is None:
        clicked.set(NoDevDet)
    # CHANGE TO 1 isntead of 3
    elif misc.thisSessionDevices[0] == NoDevDet:
        clicked.set(NoDevDet)
    else:
        clicked.set(misc.thisSessionDevices[0]['name'])

    
    # Create Dropdown menu 
    drop = tk.OptionMenu( DeviceFrame , clicked , *misc.DevicesDropList ) 
    drop.grid(row = 0, column = 1, sticky = tk.W, pady = 2)

    # Create button
    testDeviceButton = tk.Button ( DeviceFrame , text = "Test Device" , command = testDeviceBtn )
    testDeviceButton.grid(row = 0, column = 2, sticky = tk.W, pady = 2)

    


    ButtonsFrame = tk.Frame(misc.root, width= rootSizeX*2/3, height=rootSizeY*2/3)
    ButtonsFrame.grid(row=3, column=0, sticky = tk.W)

    global MonitorBtn
    MonitorBtn = tk.Button ( ButtonsFrame , text = "" , command = changeMonitor )
    MonitorBtn.grid(row = 0, column = 0, sticky = tk.W, pady = 2,padx=10)
    initMonitorPreset()

    global buttonFPS
    buttonFPS = tk.Button ( ButtonsFrame , text = "FPS 30" , command = changeFPS )
    buttonFPS.grid(row = 0, column = 1, sticky = tk.W, pady = 2)
    getFPS()    


    global pauseL
    pauseL = tk.Label( ButtonsFrame , text="P A U S E D", bg='#f00', fg='#fff', pady=10, padx=100, font=misc.font*10) 
    pauseL.grid(row = 1, columnspan=2, sticky = tk.W, pady = 2)

    # Create Label 
    mainPageText = tk.Label( ButtonsFrame , text = "Script does the binds only when Active.\nWatch YT Video, it's not obvious to setup.\nDeveloped by [NHR] Erador") 
    mainPageText.grid(row = 2, columnspan=2, sticky = tk.W, pady = 2,padx=10)



    LoggoFrame = tk.Frame(misc.root, width= rootSizeX*1/3, height=rootSizeY*2/3)
    LoggoFrame.grid(row=3, column=1, sticky = tk.W, padx=20)
    '''
    global logo_image
    logo_image = ImageTk.PhotoImage(image)
    image_label = tk.Label(LoggoFrame, image=logo_image)
    image_label.grid(row = 0, column=0, sticky = tk.W, pady = 2)
    '''
    # endregion

def on_closing():
    global appRunning
        
    appRunning = False
    
    misc.root.destroy()

def showTestData():
    global TestDeviceSelectedIndex, TestButtonLabels,TestAxisLabels,TestAxisNumLabels
    
    startinfo = misc.thisSessionDevices[TestDeviceSelectedIndex]['startinfo']
    caps = misc.thisSessionDevices[TestDeviceSelectedIndex]['caps']

    ret, info = joystickapi.joyGetPosEx(TestDeviceSelectedIndex)
    if ret:
        btns = [(1 << i) & info.dwButtons != 0 for i in range(caps.wNumButtons)]
        axisXYZ = [info.dwXpos-startinfo.dwXpos, info.dwYpos-startinfo.dwYpos, info.dwZpos-startinfo.dwZpos]
        axisRUV = [info.dwRpos-startinfo.dwRpos, info.dwUpos-startinfo.dwUpos, info.dwVpos-startinfo.dwVpos]

        # Update Labels for buttons
        i=0
        for btn in btns:

            if btn:
                TestButtonLabels[i]['text'] = '1'
            else:
                TestButtonLabels[i]['text'] = '0'
            i+=1
        
        # Update Labels for axisXYZ
        i=0
        for axis in axisXYZ:

            TestAxisLabels[i]['text'] = axis
            i+=1

        # Update Labels for axisRUV
        i=len(axisXYZ)
        for axis in axisRUV:

            TestAxisLabels[i]['text'] = axis
            i+=1


        '''if info.dwButtons:
            print("buttons: ", btns)
        if any([abs(v) > 10 for v in axisXYZ]):
            print("axis:", axisXYZ)
        if any([abs(v) > 10 for v in axisRUV]):
            print("roation axis:", axisRUV)'''

def testDeviceBtn():
    global testButton, TestFrameAx, TestFrameBtn, TestDeviceSelectedIndex, TestButtonLabels, TestButtonNumLabels,TestAxisLabels,TestAxisNumLabels
    global rootSizeX, rootSizeY

    caps=misc.thisSessionDevices[TestDeviceSelectedIndex]['caps']

    if testButton:
        testButton = False

        # Remove Labels for buttons
        for n in range(len(TestButtonLabels)):

            TestButtonLabels[n].destroy()
            TestButtonNumLabels[n].destroy()

        # Remove Labels for axes
        for n in range(len(TestAxisLabels)):

            TestAxisLabels[n].destroy()
            TestAxisNumLabels[n].destroy()

        TestButtonLabels = []
        TestButtonNumLabels = []

        TestAxisLabels = []
        TestAxisNumLabels = []

        TestFrameBtn['height'] = 0
        TestFrameAx['height'] = 0

        misc.root.geometry("%dx%d" % (rootSizeX, rootSizeY))


    else:
        testButton = True

        # Create Labels for buttons
        for n in range(caps.wNumButtons):

            #btn index
            TestButtonNumLabels.append(tk.Label( TestFrameBtn , text = str(n))) 
            TestButtonNumLabels[n].grid(row = 0, column = n, sticky = tk.W, pady = 4)

            #btn value
            TestButtonLabels.append(tk.Label( TestFrameBtn , text = "", bg= darkerColor)) 
            TestButtonLabels[n].grid(row = 1, column = n, sticky = tk.W, pady = 4, padx=4 )

        # Create Labels for Axes
        for n in range(6):

            #axis index
            TestAxisNumLabels.append(tk.Label( TestFrameAx , text = str(n))) 
            TestAxisNumLabels[n].grid(row = 0, column = n, sticky = tk.W, pady = 4, padx = 4)

            #axis value
            TestAxisLabels.append(tk.Label( TestFrameAx , text = "", bg= darkerColor)) 
            TestAxisLabels[n].grid(row = 1, column = n, sticky = tk.W, pady = 4,padx = 4)

        misc.root.geometry("%dx%d" % (rootSizeX, rootSizeY+rootSizeY*3/4))

def changeMonitor():
    global currentMonitorPreset, MonitorBtn
    
    

    if misc.getSetting('presets') is None:
        misc.setSetting('presets', {})
    
    
    if len(misc.getSetting('presets')) > 0:
                                                    
        length = len(misc.getSetting('presets'))
        
        if misc.getSetting('currentPreset') is None:
            misc.setSetting('currentPreset','0')

        id = int(misc.getSetting('currentPreset'))+1
        if id > length-1:
            id=0

        id = str(id)
        currentMonitorPreset = misc.getSetting('presets')[id]
        misc.setSetting('currentPreset',id)
    
    else:
        currentMonitorPreset = misc.defaultPreset
    
    MonitorBtn.config(text=currentMonitorPreset['str'])

def changeFPS():
    global buttonFPS
    global fpsDelta
    
    if buttonFPS['text'] == "FPS 30":
        buttonFPS['text'] = "FPS 60"
        fpsDelta = .5/60
        misc.setSetting('fps',60)
        return
    
    if buttonFPS['text'] == "FPS 60":
        buttonFPS['text'] = "FPS 120"
        fpsDelta = .5/120
        misc.setSetting('fps',120)
        return
    
    if buttonFPS['text'] == "FPS 120":
        buttonFPS['text'] = "FPS 30"
        fpsDelta = .5/30
        misc.setSetting('fps',30)
        return

def getFPS():
    global buttonFPS
    global fpsDelta

    fps = misc.getSetting('fps')

    if fps is not None:        
        if fps == 30:
            buttonFPS['text'] = "FPS 30"
            fpsDelta = .5/fps
        if fps == 60:
            buttonFPS['text'] = "FPS 60"
            fpsDelta = .5/fps
        else:
            buttonFPS['text'] = "FPS 120"
            fpsDelta = .5/120
    else:
        buttonFPS['text'] = "FPS 60"
        misc.setSetting('fps',60)
        fpsDelta = .5/60

def detectDevices():

    num = joystickapi.joyGetNumDevs()
    ret, caps, startinfo = False, None, None
    deviceIndex = 0

    for id in range(num):
        ret, caps = joystickapi.joyGetDevCaps(id)
                
        if ret:
            #print("gamepad detected: " + caps.szPname)
            ret, startinfo = joystickapi.joyGetPosEx(id)

            #misc.logger.debug('Found Device: Name: {caps.szPname} | Mid: {caps.wMid} | Pid: {caps.wPid}' )

            print(f'Found Device: Name: {caps.szPname} | Mid: {caps.wMid} | Pid: {caps.wPid}')
            print()
            print('caps:')
            print(startinfo.SIZE)
            print(startinfo.dwButtonNumber)
            print(startinfo.dwButtons)
            print(startinfo.dwFlags)
            print(startinfo.dwPOV)
            print(startinfo.dwReserved1)
            print(startinfo.dwReserved2)
            print(startinfo.dwRpos)
            print(startinfo.dwSize)
            print(startinfo.dwUpos)
            print(startinfo.dwVpos)
            print(startinfo.dwXpos)
            print(startinfo.dwYpos)
            print(startinfo.dwZpos)
            
            print()
            print(caps.OFFSET_V)
            print(caps.SIZE_W)
            print(caps.wCaps)
            print(caps.wMaxAxes)
            print(caps.wMaxButtons)
            print(caps.wMid)
            print(caps.wNumAxes)
            print(caps.wNumButtons)
            print(caps.wPeriodMax)
            print(caps.wPeriodMin)
            print(caps.wPid)
            print(caps.wRmax)
            print(caps.wRmin)
            print(caps.wUmax)
            print(caps.wUmin)
            print(caps.wVmax)
            print(caps.wVmin)
            print(caps.wXmax)
            print(caps.wXmin)
            print(caps.wZmax)
            print(caps.wZmin)
            print(caps.wYmax)
            print(caps.wYmin)
            

            misc.thisSessionDevices= {deviceIndex:{}}
            misc.thisSessionDevices[deviceIndex]['mid'] = caps.wMid
            misc.thisSessionDevices[deviceIndex]['pid'] = caps.wPid
            misc.thisSessionDevices[deviceIndex]['caps'] = caps
            misc.thisSessionDevices[deviceIndex]['name'] = misc.getHidDevicesName(caps.wMid,caps.wPid)
            misc.thisSessionDevices[deviceIndex]['startinfo'] = startinfo
            misc.thisSessionDevices[deviceIndex]['id'] = id
            
            deviceIndex += 1
    if deviceIndex == 0:
        #print("no devices detected")
        misc.thisSessionDevices = None

def setupAxesAndMouse():
    global AxisCen, AxisMax, JoystickX, JoystickY, Joystick_DZ_X, Joystick_DZ_Y
    global MouseX, MouseY, MouseXa, MouseYa, currentMonitorPreset, initialMonitor
    global Mouse_Center, MouseCen, MouseDZx, MouseDZy, Mouse_DZ_X, Mouse_DZ_Y
    '''
    Left_mA = Left_m * currentMonitorPreset['w']/initialMonitor[0] * currentMonitorPreset['s']/100
    Right_mA = Right_m * currentMonitorPreset['w']/initialMonitor[0] * currentMonitorPreset['s']/100
    Up_mA = Up_m * currentMonitorPreset['h']/initialMonitor[0] * currentMonitorPreset['s']/100
    Down_mA = Down_m * currentMonitorPreset['h']/initialMonitor[0] * currentMonitorPreset['s']/100
    '''
    MouseXa = MouseX * (currentMonitorPreset['w']/initialMonitor[0]) / (currentMonitorPreset['s']/100)
    MouseYa = MouseY * (currentMonitorPreset['h']/initialMonitor[1]) / (currentMonitorPreset['s']/100)
    
    MouseCen[0] = Mouse_Center[0] / (currentMonitorPreset['s']/100)
    MouseCen[1] = Mouse_Center[1] / (currentMonitorPreset['s']/100)
    
    MouseDZx[0] = Mouse_DZ_X[0] / (currentMonitorPreset['s']/100)
    MouseDZx[1] = Mouse_DZ_X[1] / (currentMonitorPreset['s']/100)

    MouseDZy[0] = Mouse_DZ_Y[0] / (currentMonitorPreset['s']/100)
    MouseDZy[1] = Mouse_DZ_Y[1] / (currentMonitorPreset['s']/100)

    JoystickX = AxisCen - Joystick_DZ_X[1]
    JoystickY = AxisCen - Joystick_DZ_Y[1]


    global ButtonsAmount
    ButtonsAmount = misc.thisSessionDevices[TestDeviceSelectedIndex]['caps'].wNumButtons

    global xAxis, yAxis
    xAxis = misc.getSetting('mouseXaxis')
    yAxis = misc.getSetting('mouseYaxis')

    global applyCurveX, applyCurveY
    applyCurveX = misc.getSetting(f'applyCurve{xAxis}')
    applyCurveY = misc.getSetting(f'applyCurve{yAxis}')

    global invertXaxis, invertYaxis
    
    if misc.getSetting(f'axisType{xAxis}') == 3:
        invertXaxis = True
    else:
        invertXaxis = False

    if misc.getSetting(f'axisType{yAxis}') == 3:
        invertYaxis = True
    else:
        invertYaxis = False
    

    '''
    axisTypes = [
    '0 => 1',
    '1 => 0',
    '-1 <= 0 => 1',
    '1 <= 0 => -1']
    '''

def mainLoop():
    global TestDeviceSelectedIndex, Pause, AxisCen, ButtonsAmount
    global Joystick_DZ_X, Joystick_DZ_Y, JoystickX, JoystickY
    global MouseXa, MouseYa, Mouse_DZ_X, Mouse_DZ_Y, MouseCen, MouseDZx, MouseDZy
    global applyCurveX, applyCurveY,invertXaxis, invertYaxis, xAxis, yAxis
    
    

    ret, info = joystickapi.joyGetPosEx(TestDeviceSelectedIndex)
    
    if ret:
        btns = [(1 << i) & info.dwButtons != 0 for i in range(ButtonsAmount)]
        axes = [info.dwXpos, info.dwYpos, info.dwZpos, info.dwRpos, info.dwUpos, info.dwVpos]
        
        if btns[9]:
            pause()

        if not Pause:
            
            ####     X axis on Device
            
            
            axisXvalue = axes[xAxis] - AxisCen

            # Check for DZ
            if Joystick_DZ_X[0] < axisXvalue and axisXvalue < Joystick_DZ_X[1]:
                axisXvalue = 0

            else:
                if invertXaxis:
                    axisXvalue *= -1   
                

            ####     Y axis on Device

            axisYvalue = axes[yAxis] - AxisCen

            # Check for DZ
            if Joystick_DZ_Y[0] < axisYvalue and axisYvalue < Joystick_DZ_Y[1]:
                axisYvalue = 0

            else:
                if invertYaxis:
                    axisYvalue *= -1


            ###     Calculate to Mouse X
            if axisXvalue == 0:
                MouseToX = MouseCen[0]

            elif axisXvalue > 0:

                # Removing DeadZone
                axisXvalue -= Joystick_DZ_X[1]

                if applyCurveX:
                    MouseToX = MouseDZx[1] + MouseXa * getCurve(axisXvalue/JoystickX)
                else:
                    MouseToX = MouseDZx[1] + MouseXa * axisXvalue/JoystickX
            else:
                
                # Removing DeadZone
                axisXvalue += Joystick_DZ_X[1]

                if applyCurveX:
                    MouseToX = MouseDZx[0] + MouseXa * getCurve(axisXvalue/JoystickX)
                else:
                    MouseToX = MouseDZx[0] + MouseXa * axisXvalue/JoystickY

            ###     Calculate to Mouse Y
            if axisYvalue == 0:
                MouseToY = MouseCen[1]

            elif axisYvalue > 0:

                # Removing DeadZone
                axisYvalue -= Joystick_DZ_Y[1]

                if applyCurveY:
                    MouseToY = MouseDZy[1] + MouseYa * getCurve(axisYvalue/JoystickY)
                else:
                    MouseToY = MouseDZy[1] + MouseYa * axisYvalue/JoystickY
            else:

                # Removing DeadZone
                axisYvalue += Joystick_DZ_Y[1]

                if applyCurveY:
                    MouseToY = MouseDZy[0] + MouseYa * getCurve(axisYvalue/JoystickY)
                else:
                    MouseToY = MouseDZy[0] + MouseYa * axisYvalue/JoystickY

            ###    Apply to Mouse
            m.position=(MouseToX,MouseToY)



            ####         BINDS

            if btns[0]:
                # sometime the game takes my russian keyboard layout for no reason, 
                # so I double the key by adding russian analog on the same key ']' is the same key as 'ъ'
                c.press('[')
                c.press('х')
            else:
                c.release('[')
                c.release('х')

            if btns[1]:
                c.press('p')
                c.press('з')
            else:
                c.release('p')
                c.release('з')

            
            
            
            

def main():
    global appRunning, fpsDelta, testButton, Pause

    if misc.getSetting('configured') is True:
        setupAxesAndMouse()


    #start_time = t.time()
    #counter = 0

    while appRunning:
        t.sleep(fpsDelta)


        misc.root.update_idletasks()
        misc.root.update()

        if testButton:
            showTestData()

        else:
            testButton = False


        mainLoop()      


        '''counter+=1
        if (t.time() - start_time) > 1 :
            print("FPS: ", counter / (t.time() - start_time))
            counter = 0
            start_time = t.time()'''

tKroot()
main()
'''
try:
    tKroot()
except Exception as e:
    a = "tKroot crashed. Error: %s", e
    misc.myException("tKroot crashed. Error: %s", e)

try:
    main()
except Exception as e:
    misc.myException("Main crashed. Error: %s", e)
'''


'''    
if __name__ == "__main__":
    with cProfile.Profile() as profile:

        try:
            tKroot()
        except Exception as e:
            a = "tKroot crashed. Error: %s", e
            misc.myException("tKroot crashed. Error: %s", e)

        try:
            main()
        except Exception as e:
            misc.myException("Main crashed. Error: %s", e)

    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()'''
















