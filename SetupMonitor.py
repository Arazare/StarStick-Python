import tkinter as tk
import misc
import time as t

rootSizeX = 0
rootSizeY = 0

defaultColor = '#F0F0F0'
darkerColor = '#D0D0D0'

if misc.getSetting('fps') is None:
    fpsDelta = 1/60
    misc.setSetting('fps',60)

else:
    fpsDelta = 1/misc.getSetting('fps')

AllowNewSettingWindow = True

settingsRunning = True

globalFrames = []
GeneralWidgets = []

CustomResolutionPresets = []
CustomResolutionPresetsStrings = []

def getPresets():
    global CustomResolutionPresetsStrings, CustomResolutionPresets

    if misc.getSetting('presets') is None:
        misc.setSetting('presets', {})

    if len(misc.getSetting('presets')) == 0:
        CustomResolutionPresetsStrings = ['Nothing created']
    else:

        presets = misc.getSetting('presets')
        
        for i in range(len(presets)):
            y=str(i)
            CustomResolutionPresetsStrings.append(presets[y]['str'])
            CustomResolutionPresets.append([presets[y]['w'],presets[y]['h'],presets[y]['s']])



def setupDeviceRoot():
    global settingsRunning, SetupDeviceRoot, globalFrames

    settingsRunning = True

    SetupDeviceRoot = tk.Toplevel(misc.root)
    SetupDeviceRoot.title("Setup Monitor")
    SetupDeviceRoot.geometry(f'{rootSizeX}x{rootSizeY}')

    SetupDeviceRoot.protocol("WM_DELETE_WINDOW", on_closing_Settings)

    # create frames
    for i in range(9):
        globalFrames.append(tk.Frame(SetupDeviceRoot, width= rootSizeX, height=0, pady=0,padx=20))
        globalFrames[i].grid(row=i, column=0, columnspan=2, sticky="ew")

    createGeneralWidgets()



    # General Frames

def on_closing_Settings():
    global settingsRunning, AllowNewSettingWindow, globalFrames, GeneralWidgets, CustomResolutionPresets, CustomResolutionPresetsStrings
 
    SetupDeviceRoot.destroy()
    SetupDeviceRoot.update()

    settingsRunning = False
    AllowNewSettingWindow = True

    globalFrames = []
    GeneralWidgets = []

    CustomResolutionPresets = []
    CustomResolutionPresetsStrings = []


def deletePreset():
    global CustomResolutionPresetsStrings, CustomResolutionPresets, DropMenuCurrentStr, GeneralWidgets,globalFrames

    string = DropMenuCurrentStr.get()

    for i in range(len(CustomResolutionPresetsStrings)):
        
        if CustomResolutionPresetsStrings[i] == string:
            CustomResolutionPresetsStrings.pop(i)
            CustomResolutionPresets.pop(i)

            presets = misc.getSetting('presets')
            presets.pop(str(i))

            misc.setSetting('presets',presets)

            if len(presets) == 0:
                CustomResolutionPresetsStrings.append('Nothing created')
                misc.setSetting('currentPreset', None)

            # update dropdown
            GeneralWidgets[2].destroy()

            DropMenuCurrentStr.set('<Click to select>')

            GeneralWidgets[2]= tk.OptionMenu( globalFrames[1] , DropMenuCurrentStr , *CustomResolutionPresetsStrings ) 
            GeneralWidgets[2].grid(row = 0, column = 0, sticky = tk.W, pady = 0)



    

def createPreset():
    global WidthString, HeightString, ScaleString, CustomResolutionPresetsStrings, CustomResolutionPresets

    w = int(WidthString.get())
    h = int(HeightString.get())
    s = int (ScaleString.get())

    WidthString.set('')
    HeightString.set('')
    ScaleString.set('')

    if misc.getSetting('presets') is None:
        misc.setSetting('presets',{})

    if len(misc.getSetting('presets')) == 0:
        misc.setSetting('presets',{'0': {'str': f'{w}x{h} @ {s}','w': w, 'h': h, 's':s } } )
        CustomResolutionPresetsStrings = [f'{w}x{h} @ {s}']
        CustomResolutionPresets = [w, h, s]

    else:
        
        presets = misc.getSetting('presets')
        presets[len(presets)] = {'str': f'{w}x{h} @ {s}','w': w, 'h': h, 's':s}

        misc.setSetting('presets',presets)

        CustomResolutionPresetsStrings.append([f'{w}x{h} @ {s}'])
        CustomResolutionPresets.append([w, h, s])
    
    # update dropdown
    GeneralWidgets[2].destroy()

    DropMenuCurrentStr.set('<Click to select>')

    GeneralWidgets[2] = tk.OptionMenu( globalFrames[1] , DropMenuCurrentStr , *CustomResolutionPresetsStrings ) 
    GeneralWidgets[2].grid(row = 0, column = 0, sticky = tk.W, pady = 0)




    
def createGeneralWidgets():
    global globalFrames, GeneralWidgets, darkerColor, CustomResolutionPresetsStrings

    getPresets()
    
    # widget Index
    w = 0
    # frame
    f = 0

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Go to Windows 'Display Settings' to get\nyour 'Screen Resolution' and 'Scale'.")) 
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 5, padx = 10)
    w+=1

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Select preset to delete:")) 
    GeneralWidgets[w].grid(row = 1, column = 0, sticky = tk.W, pady = 0, padx = 10)
    w+=1
    f+=1

    global DropMenuCurrentStr
    DropMenuCurrentStr = tk.StringVar()
    DropMenuCurrentStr.set('<Click to select>')
    
    # Create Dropdown menu
    GeneralWidgets.append( tk.OptionMenu( globalFrames[f] , DropMenuCurrentStr , *CustomResolutionPresetsStrings ) )
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 0)
    # w = 2, f = 2 here. It's needed to update the list data in createPreset() and deletePreset()
    w+=1

    GeneralWidgets.append(tk.Button( globalFrames[f] , bg=darkerColor, text = 'Delete', command = deletePreset)) 
    GeneralWidgets[w].grid(row = 0, column = 1, sticky = tk.W, pady = 2, padx = 2)
    w+=1
    f+=1


    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Create Custom Resolution:"))
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 10, padx = 10)
    w+=1
    f+=1

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Screen Width: "))
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 0, padx = 10)
    w+=1

    global WidthString
    WidthString = tk.StringVar()
    GeneralWidgets.append(tk.Entry( globalFrames[f] , textvariable = WidthString,font=(misc.font*1.5)))
    GeneralWidgets[w].grid(row = 0, column = 1, sticky = tk.W, pady = 0, padx = 10)
    w+=1
    f+=1

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Screen Height: "))
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 0, padx = 10)
    w+=1

    global HeightString
    HeightString = tk.StringVar()
    GeneralWidgets.append(tk.Entry( globalFrames[f] , textvariable = HeightString,font=(misc.font*1.5)))
    GeneralWidgets[w].grid(row = 0, column = 1, sticky = tk.W, pady = 0, padx = 10)
    w+=1
    f+=1

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Screen Scale: "))
    GeneralWidgets[w].grid(row = 0, column = 0, sticky = tk.W, pady = 0, padx = 10)
    w+=1

    global ScaleString
    ScaleString = tk.StringVar()
    GeneralWidgets.append(tk.Entry( globalFrames[f] , textvariable = ScaleString,font=(misc.font*1.5)))
    GeneralWidgets[w].grid(row = 0, column = 1, sticky = tk.W, pady = 0, padx = 10)
    w+=1
    f+=1

    GeneralWidgets.append(tk.Button( globalFrames[f] , bg=darkerColor, text = 'Create', command = createPreset)) 
    GeneralWidgets[w].grid(row = 0, column = 1, sticky = tk.W, pady = 2, padx = 2)
    w+=1
    f+=1

    GeneralWidgets.append(tk.Label( globalFrames[f] , text = "Make sure you entered only Numbers.\nIf something went wrong - restart app.\n Scale examples: 100, 125, 150, etc.", bg='#FFBC82'))
    GeneralWidgets[w].pack(fill='both',side = 'top')
    w+=1
    f+=1

    




def setupDeviceMain():
    global settingsRunning, fpsDelta, SetupDeviceRoot

    while settingsRunning:

        SetupDeviceRoot.update_idletasks()
        SetupDeviceRoot.update()
            
        t.sleep(fpsDelta*3)

def start():
    global AllowNewSettingWindow

    if AllowNewSettingWindow:
        AllowNewSettingWindow = False

        setupDeviceRoot()
        setupDeviceMain()
        '''
        try:
            setupDeviceRoot()
        except Exception as e:
            misc.myException("Monitor Root crashed. Error: %s", e)

        try:
            setupDeviceMain()
        except Exception as e:
            misc.myException("Monitor Main. Error: %s", e)


        '''







