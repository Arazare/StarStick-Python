import tkinter as tk
import misc
import time as t
import joystickapi

rootSizeX = 0
rootSizeY = 0

defaultColor = '#F0F0F0'
darkerColor = '#D0D0D0'

if misc.getSetting('fps') is None:
    fpsDelta = 1/60
else:
    fpsDelta = 1/misc.getSetting('fps')

AllowNewSettingWindow = True

testButton = False
TestDeviceSelectedIndex = 0

settingsRunning = True

TestButtonButtons = []
TestButtonNumLabels = []

TestAxisButtons = []
TestAxisNumLabels = []

GeneralWidgets = []

SetupWidgets = []

axisTypes = ['0 => 1','1 => 0','-1 <= 0 => 1','1 <= 0 => -1']

SelectedButton = {'on': False, 'btn': None, 'index': None}
misc.setSetting('configured', True)

def writeGeneralWidgets():
    global ButtonTextFrame, ConfigTextFrame, AxisTextFrame

    index = len(GeneralWidgets)
    GeneralWidgets.append(tk.Label( ButtonTextFrame , text = " ^ click on button to see its settings"))
    GeneralWidgets[index].grid(row = 0, columnspan=2, sticky = tk.W, pady = 0,padx=10)

    index += 1
    GeneralWidgets.append(tk.Label( AxisTextFrame , text = " ^ click on axis to see its settings"))
    GeneralWidgets[index].grid(row = 0, columnspan=2, sticky = tk.W, pady = 0,padx=10)

    index += 1
    GeneralWidgets.append(tk.Label( ConfigTextFrame , text = " Back up your config.json file.\n There is not way to cancel changes.", bg='#FFC787'))
    GeneralWidgets[index].pack(side = 'top',fill = 'both', expand = True)

def setupDeviceRoot():
    global settingsRunning, SetupDeviceRoot

    settingsRunning = True

    SetupDeviceRoot = tk.Toplevel(misc.root)
    SetupDeviceRoot.title("Setup Device")
    SetupDeviceRoot.geometry(f'{rootSizeX}x{rootSizeY}')

    SetupDeviceRoot.protocol("WM_DELETE_WINDOW", on_closing_Settings)



    # General Frames

    global DeviceFrame
    DeviceFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    DeviceFrame.grid(row=0, column=0, columnspan=2, sticky="ew")

    global ButtonFrame
    ButtonFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    ButtonFrame.grid(row=1, column=0, columnspan=2, sticky="ew")
   
    global ButtonTextFrame
    ButtonTextFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    ButtonTextFrame.grid(row=2, column=0, columnspan=2, sticky="ew")

    global AxisFrame
    AxisFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    AxisFrame.grid(row=3, column=0, columnspan=2, sticky="ew")
   
    global AxisTextFrame
    AxisTextFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    AxisTextFrame.grid(row=4, column=0, columnspan=2, sticky="ew")

    global ConfigTextFrame
    ConfigTextFrame = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    ConfigTextFrame.grid(row=5, column=0, columnspan=2, sticky="ew")

    writeGeneralWidgets()

    # Setup Frames

    global SetupFrame1
    SetupFrame1 = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    SetupFrame1.grid(row=6, column=0, columnspan=2, sticky="ew")

    global SetupFrame2
    SetupFrame2 = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    SetupFrame2.grid(row=7, column=0, columnspan=2, sticky="ew")

    global SetupFrame3
    SetupFrame3 = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    SetupFrame3.grid(row=8, column=0, columnspan=2, sticky="ew")

    global SetupFrame4
    SetupFrame4 = tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20)
    SetupFrame4.grid(row=9, column=0, columnspan=2, sticky="ew")

    setupDeviceFrame()
    updateWidgetsForNewDevice()




def on_closing_Settings():
    global settingsRunning, TestButtonButtons, TestButtonNumLabels,AllowNewSettingWindow, GeneralWidgets, TestAxisButtons, TestAxisNumLabels
 
    SetupDeviceRoot.destroy()
    SetupDeviceRoot.update()

    settingsRunning = False
    AllowNewSettingWindow = True

    TestButtonButtons = []
    TestButtonNumLabels = []
    TestAxisButtons = []
    TestAxisNumLabels = []
    GeneralWidgets = []



def buttonSetup(index):
    global SelectedButton, TestButtonButtons, TestAxisButtons, ButtonFrame, AxisFrame, SetupWidgets, SetupFrame1

    for i in range(len(SetupWidgets)):
        SetupWidgets[i].destroy()

    SetupWidgets = []
        
    if SelectedButton['btn']:
        # button setup
        SetupWidgets.append(tk.Label( SetupFrame1 , text = ' * No settings for the buttons are available yet * ')) 
        SetupWidgets[0].pack(side = 'top',fill = 'both', expand = True)


def buttonSelected(index):
    global SelectedButton, TestButtonButtons,  TestAxisButtons, darkerColor

    if SelectedButton['on'] is False:
        
        SelectedButton['on'] = True
        SelectedButton['btn'] = True
        SelectedButton['index'] = index

        TestButtonButtons[index].config(bg='yellow')

    else:

        if SelectedButton['btn']:
            TestButtonButtons[ SelectedButton['index'] ].config(bg=darkerColor)
        else:
            TestAxisButtons[ SelectedButton['index'] ].config(bg=darkerColor)

        SelectedButton['on'] = True
        SelectedButton['btn'] = True
        SelectedButton['index'] = index

        TestButtonButtons[index].config(bg='yellow')

    buttonSetup(index)

def setupTypeOfAxis(axisID):
    global axisTypes, SetupWidgets, darkerColor

    if misc.getSetting('axisType'+str(axisID)) == 2:
            
        SetupWidgets[3].config(bg=darkerColor)
        SetupWidgets[4].config(bg='yellow')
        misc.setSetting('axisType'+str(axisID),3)

    else:
            
        SetupWidgets[4].config(bg=darkerColor)
        SetupWidgets[3].config(bg='yellow')
        misc.setSetting('axisType'+str(axisID),2)    
        

def saveCurve(index, btnIndex):
    global SetupWidgets, darkerColor

    if misc.getSetting('applyCurve'+str(index)):
        SetupWidgets[btnIndex].config(bg=darkerColor)
        misc.setSetting('applyCurve'+str(index), False)
    else:
        SetupWidgets[btnIndex].config(bg='yellow')
        misc.setSetting('applyCurve'+str(index), True)

def axisSetup(index):
    global SelectedButton, TestButtonButtons, TestAxisButtons, ButtonFrame, AxisFrame, SetupWidgets, SetupFrame1, SetupFrame2, darkerColor, axisTypes, SetupFrame3, SetupFrame4, defaultColor

    for i in range(len(SetupWidgets)):
        SetupWidgets[i].destroy()

    SetupWidgets = []
        
    if not SelectedButton['btn']:
        
        # axis setup
        if misc.getSetting('axisType'+str(index)) is not None:
            axisType = 2 # 2 ==  '-1 <= 0 => 1'
            misc.setSetting('axisType'+str(index), axisType)

        else:
            axisType = misc.getSetting('axisType'+str(index))
            
        
        # Type of axis
        SetupWidgets.append(tk.Label( SetupFrame1 , text = ' Choose the type of axis: ')) 
        SetupWidgets[0].grid(row = 0, column = 0, sticky = tk.W, pady = 0, padx = 10)
        
        for i in range(len(axisTypes)):

            if i == axisType:

                SetupWidgets.append(tk.Button( SetupFrame2 , bg='yellow', text = axisTypes[i], command = lambda: setupTypeOfAxis(index))) 
                SetupWidgets[i+1].grid(row = 0, column = i, sticky = tk.W, pady = 0, padx = 2)

            else:
                if i == 2 or i == 3:
                    btncolor = darkerColor
                else:
                    btncolor = defaultColor

                SetupWidgets.append(tk.Button( SetupFrame2 , bg=btncolor, text = axisTypes[i], command = lambda: setupTypeOfAxis(index))) 
                SetupWidgets[i+1].grid(row = 0, column = i, sticky = tk.W, pady = 0, padx = 2)


        # Curve
        if misc.getSetting('applyCurve'+str(index)) is not None:
            applyCurve = misc.getSetting('applyCurve'+str(index))
        else:
            applyCurve = True
            misc.setSetting('applyCurve'+str(index), applyCurve)

        
        if applyCurve:
            color = 'yellow'
        else:
            color = darkerColor

        i=len(SetupWidgets)
        SetupWidgets.append(tk.Button( SetupFrame3 , bg=color, text = ' Apply Curve to this axis (a=0.9): a*x^{5}+(1-a)*x', command = lambda: saveCurve(index,i))) 
        SetupWidgets[i].grid(row = 0, column = 0, sticky = tk.W, pady = 0, padx = 2)



        # Mouse XY

        if misc.getSetting('mouseXaxis') is not None:
            mouseXaxis = misc.getSetting('mouseXaxis')
        else:
            mouseXaxis = 0
            misc.setSetting('mouseXaxis', mouseXaxis)

        if misc.getSetting('mouseYaxis') is not None:
            mouseYaxis = misc.getSetting('mouseYaxis')
        else:
            mouseYaxis = 1
            misc.setSetting('mouseYaxis', mouseYaxis)

        if mouseXaxis == index:
            colorX = 'yellow'
        else:
            colorX = darkerColor

        if mouseYaxis == index:
            colorY = 'yellow'
        else:
            colorY = darkerColor

        SetupWidgets.append(tk.Button( SetupFrame4 , bg=colorX, text = 'Use this axis for mouse X axis', command = lambda: setMouseXY(index, i+1, True))) 
        SetupWidgets[i+1].grid(row = 0, column = 0, sticky = tk.W, pady = 2, padx = 2)

        SetupWidgets.append(tk.Button( SetupFrame4 , bg=colorY, text = 'Use this axis for Mouse Y axis', command = lambda: setMouseXY(index, i+2, False))) 
        SetupWidgets[i+2].grid(row = 1, column = 0, sticky = tk.W, pady = 2, padx = 2)



def setMouseXY( axisId, widgetId, mouseAxisX):

    if mouseAxisX:
        misc.setSetting( 'mouseXaxis', axisId )
        SetupWidgets[widgetId].config( bg='yellow' )

    else:
        misc.setSetting( 'mouseYaxis', axisId )
        SetupWidgets[widgetId].config( bg='yellow' )

    


def axisSelected(index):
    global SelectedButton, TestButtonButtons, TestButtonNumLabels, TestAxisButtons, TestAxisNumLabels, ButtonFrame, AxisFrame, darkerColor

    if SelectedButton['on'] is False:
        
        SelectedButton['on'] = True
        SelectedButton['btn'] = False
        SelectedButton['index'] = index

        TestAxisButtons[index].config(bg='yellow')

    else:

        if SelectedButton['btn']:
            TestButtonButtons[ SelectedButton['index'] ].config(bg=darkerColor)
        else:
            TestAxisButtons[ SelectedButton['index'] ].config(bg=darkerColor)

        SelectedButton['on'] = True
        SelectedButton['btn'] = False
        SelectedButton['index'] = index

        TestAxisButtons[index].config(bg='yellow')

    axisSetup(index)

def updateWidgetsForNewDevice():
    global TestButtonButtons, TestButtonNumLabels, TestAxisButtons, TestAxisNumLabels, ButtonFrame, AxisFrame

    TestButtonNumLabels = []
    TestButtonButtons = []
    TestAxisButtons = []
    TestAxisNumLabels = []

    caps=misc.thisSessionDevices[TestDeviceSelectedIndex]['caps']

     # Create Labels for buttons
    for n in range(caps.wNumButtons):

        #btn index
        TestButtonNumLabels.append(tk.Label( ButtonFrame , text = str(n))) 
        TestButtonNumLabels[n].grid(row = 0, column = n, sticky = tk.W, pady = 1, padx=2)

        #btn value
        TestButtonButtons.append(tk.Button( ButtonFrame , text = "", bg= darkerColor, command = lambda m=n: buttonSelected(m) ))
        TestButtonButtons[n].grid(row = 1, column = n, sticky = tk.W, pady = 1, padx=1 )

    # Create Labels for Axes
    for n in range(6):

        #axis index
        TestAxisNumLabels.append(tk.Label( AxisFrame , text = str(n))) 
        TestAxisNumLabels[n].grid(row = 0, column = n, sticky = tk.W, pady = 1, padx = 8)

        #axis value
        TestAxisButtons.append(tk.Button( AxisFrame , text = "", bg= darkerColor,  command = lambda m=n: axisSelected(m) )) 
        TestAxisButtons[n].grid(row = 1, column = n, sticky = tk.W, pady = 1,padx = 4)


def showDeviceData():
    global TestButtonButtons, TestButtonNumLabels, TestAxisButtons, TestAxisNumLabels, TestDeviceSelectedIndex, settingsRunning
    
    startinfo = misc.thisSessionDevices[TestDeviceSelectedIndex]['startinfo']
    caps = misc.thisSessionDevices[TestDeviceSelectedIndex]['caps']

    ret, info = joystickapi.joyGetPosEx(TestDeviceSelectedIndex)
    if ret & settingsRunning:
        btns = [(1 << i) & info.dwButtons != 0 for i in range(caps.wNumButtons)]
        axisXYZRUV = [info.dwXpos-startinfo.dwXpos, info.dwYpos-startinfo.dwYpos, info.dwZpos-startinfo.dwZpos,info.dwRpos-startinfo.dwRpos, info.dwUpos-startinfo.dwUpos, info.dwVpos-startinfo.dwVpos]

        # Update Labels for buttons
        i=0
        for btn in btns:

            if btn:
                TestButtonButtons[i]['text'] = '1'
            else:
                TestButtonButtons[i]['text'] = '0'
            i+=1
        
        # Update Labels for axisXYZRUV
        i=0
        for axis in axisXYZRUV:

            TestAxisButtons[i]['text'] = axis
            i+=1

def setupDeviceFrame():

    # Create Label 
    GeneralWidgets.append( tk.Label( DeviceFrame , text = "Selected Device: ")  )
    GeneralWidgets[0].grid(row = 0, column = 0, sticky = tk.W, pady = 1,padx=10)

    # Dropdown menu options
    if misc.thisSessionDevices is None:
        misc.DevicesDropList = ['No Devices Detected']
    else:
        misc.DevicesDropList = []
        for device in misc.thisSessionDevices:
            misc.DevicesDropList.append(misc.thisSessionDevices[device]['name'])

    global clicked
    # datatype of menu text 
    clicked = tk.StringVar()

    # initial menu text
    if misc.thisSessionDevices is None:
        clicked.set('No Devices Detected')
    else:
        clicked.set(misc.thisSessionDevices[0]['name'])

    # Create Dropdown menu 
    drop = tk.OptionMenu( DeviceFrame , clicked , *misc.DevicesDropList ) 
    drop.grid(row = 0, column = 1, sticky = tk.W, pady = 1)

def setupDeviceMain():
    global settingsRunning, fpsDelta, SetupDeviceRoot,clicked,TestDeviceSelectedIndex

    while settingsRunning:

        SetupDeviceRoot.update_idletasks()
        SetupDeviceRoot.update()
        
        deviceStr = clicked.get()
        
        if deviceStr != misc.thisSessionDevices[TestDeviceSelectedIndex]['name']:
            for i in range(len(misc.thisSessionDevices)):
                if deviceStr == misc.thisSessionDevices[i]:
                    TestDeviceSelectedIndex = i
                    clicked.set(misc.thisSessionDevices[TestDeviceSelectedIndex])

                    updateWidgetsForNewDevice()

        showDeviceData()

            
        t.sleep(fpsDelta*3)



def start():
    global AllowNewSettingWindow

    if AllowNewSettingWindow:
        AllowNewSettingWindow = False

        try:
            setupDeviceRoot()
        except Exception as e:
            misc.myException("Setup Device Root crashed. Error: %s", e)

        try:
            setupDeviceMain()
        except Exception as e:
            misc.myException("Setup Device Main. Error: %s", e)



































































