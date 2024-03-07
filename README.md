# 3D Models automaton
This repository houses the scripts to create pseudo-3D images for the TF2 wiki. For more information, see the [3D Models project page](https://wiki.teamfortress.com/wiki/Team_Fortress_Wiki:3D_Models).

## Requirements
* [Windows](https://www.microsoft.com/windows)
* [TF2](https://store.steampowered.com/app/440/Team_Fortress_2)
* HLMV (included as a part of TF2)
    * (optionally) [HLMV++](https://github.com/ImguRandom/HLMVPlusPlus#installation)
* [Python 3.7.9](https://www.python.org/downloads/release/python-379)
* [This repository](https://github.com/jbzdarkid/3D-Models-automaton/releases/latest/download/3D-Models-automation.zip)

## Installation steps
1. Install Windows
2. Install TF2
3. Extract `3D-Models-automation.zip` to an easily accessible folder.
4. Follow the [HLMV setup instructions](https://wiki.teamfortress.com/wiki/Help:Model_Viewer)  
    * Be sure to set up the VMT replacement textures (linked in the Program limitations section) or you can find the files in this repository.
5. Launch TF2 so that it maps your custom folders (for material overrides) and generates `gameinfo.txt`.
6. Set up Python  
    a. Install [Python 3.7.9](https://www.python.org/downloads/release/python-379/#:~:text=7083fed513c3c9a4ea655211df9ade27)  
    b. Open Powershell  
    c. `cd` to the extracted `3D-Models-automaton` folder  
    d. Run `python -m venv venv` (may take a few seconds)  
    e. Run `./venv/scripts/activate`  
    f. Run `pip install -r requirements.txt`  
7. Run the automate script  
    a. Open HLMV (or HLMV++)  
    b. Load your model, center view, and zoom until it is a reasonable size  
    c. Run `python automate.py`  
    d. Wait for the script to rotate and screenshot the model. Do not switch away from HLMV during this time.  
    e. Wait for the script to blend the images.  
    f. Enter the name of your file. When testing, you should prefix your images with `User Username`, e.g. `User Darkid Test`  
    g. Enter your username.  
    h. Enter your password. Even though no characters will appear, the terminal is still reading your inputs.  
    i. Wait for your file to upload.  
    j. If login or upload fails, the script will save your image (and the template) to `temp.jpg` and `temp.txt`. You can upload them manually if you wish.  

For further instructions, see [TFW:3D Models](https://wiki.teamfortress.com/wiki/Team_Fortress_Wiki:3D_Models#Workflow)

## Troubleshooting
### Unable to create a virtual environment in (6d) because "the command [...] returned non-zero exit status 1."
This usually indicates that python has been installed improperly. Please uninstall python (search for "Add or remove programs") and then reinstall it using the link in (6a).
If possible, install python for all users, and if you still encounter this issue, try running Powershell again using an administrator.

### Unable to activate the virtual environment in (6e) because "the execution of scripts is disabled on this system"
For your safety, Windows by default does not allow execution of non-Microsoft powershell scripts (such as python's virtual environment).

To disable this for the current powershell session, run:
```ps1
Set-ExecutionPolicy Unrestricted -Scope Process
```
To disable this forever, run:
```ps1
Set-ExecutionPolicy Unrestricted -Force
```

Note that you may need to run Powershell as an administrator to execute these commands.

### Unable to install requirements in (6f) because "No matching distribution found for numpy==1.21.6"
Unfortunately, this codebase requires a specific, older version of python. Please uninstall python (search for "Add or remove programs") and then reinstall it using the link in (6a).

### The 3D image is not removing the HLMV window borders
The `imageprocessor.py` script will attempt to automatically detect the bounds of the HLMV viewport. This is not bulletproof and may fail with an error like "IndexError: index 0 is out of bounds for axis 0 with size 0"

If you have having trouble, you can manually edit the `bounds_override` variable in `automate.py`. For example, on my 3840x2100 monitor, I use these bounds:
```py
bounds_override = (2, 70, 3838, 1730)
```
You can open this file in any text editor and simply change the code. It may take some trial and error to find the correct values.

If you would like to remove the override, simply set all the values to 0:
```py
bounds_override = (0, 0, 0, 0)
```

### The automate script fails during (7c) with an error like "Couldn't find HLMV, is it open with a model loaded?"
The script relies on the window title to identify HLMV (or HLMV++).  
If HLMV is open and you've loaded a model, the title should be something like `models\weapons\w_models\w_bonesaw.mdl`  
If your models are hosted somewhere else (or, for some reason, your title is different), open `automate.py` in a text editor and change this line:
```py
     if GetWindowText(hwnd).startswith('models\\'):
```
to something which matches your window's title, e.g.:
```py
    if GetWindowText(hwnd).startswith('D:\\Modelling'):
```
Note: You *must* use `\\` to represent a single `\`.  
Note: You *must* preserve the 4 leading spaces before the `if`.  

### Further questions
If you are experiencing issues with the model itself (the way it looks or rotates), please take a look at the [notes on the TFW:3D Models page](https://wiki.teamfortress.com/wiki/Team_Fortress_Wiki:3D_Models#Workflow).

If you are still having trouble, you can [leave me a message on the TF2 wiki](https://wiki.teamfortress.com/w/index.php?title=User_talk:Darkid&action=edit&section=new), [add me on steam](https://steamcommunity.com/id/jbzdarkid), [open a GitHub issue](https://github.com/jbzdarkid/3D-Models-automaton/issues/new), or send a message by carrier pigeon (they know where I live).
