# 3D Models automaton

## Requirements
* [Windows](https://www.microsoft.com/windows)
* [TF2](https://store.steampowered.com/app/440/Team_Fortress_2)
* HLMV (included as a part of TF2)
    * (optionally) [HLMV++](https://github.com/ImguRandom/HLMVPlusPlus#installation)
* [Python 3.7.9](https://www.python.org/downloads/release/python-379)
* [This repository](https://github.com/jbzdarkid/3D-Models-automaton/releases/latest/download/3D-Models-automaton.zip)

## Installation steps
1. Install Windows
2. Install TF2
3. Extract `3D-Models-automaton.zip` to an easily accessible folder.
4. Follow the [HLMV setup instructions](https://wiki.teamfortress.com/wiki/Help:Model_Viewer)
    * Be sure to set up the VMT replacement textures (Program limitations) or you can find the files included in this zip file.
5. Launch TF2 so that it maps your custom folders (for material overrides) and generates `gameinfo.txt`.
6. Set up Python
    a. Install [Python 3.7.9](https://www.python.org/downloads/release/python-379)
    b. Open Powershell
    c. `cd` to the extracted `3D-Models-automaton` folder
    d. Run `python -3 -m venv venv` (may take a few seconds)
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
### Unable to activate the virtual environment in (6e) because "the execution of scripts is disabled on this system"
For your safety, Windows by default does not allow execution of non-Microsoft powershell scripts (such as python's virtual environment).

To disable this for the current powershell session, run:
`Set-ExecutionPolicy Unrestricted -Scope Process`
To disable this forever, run:
`Set-ExecutionPolicy Unrestricted -Force`

Note that you may need to run Powershell as an administrator to execute these commands.

### The 3D image is not removing the HLMV window borders
The `imageprocessor.py` script will attempt to automatically detect the bounds of the HLMV viewport. This is not bulletproof and may fail.

If you have having trouble, you can manually edit the `bounds_override` variable in `automate.py`. For example, on my 3840x2100 monitor, I use these bounds:
`bounds_override = (2, 70, 3838, 1730)`
You can open this file in any text editor and simply change the code. It may take some trial and error to find the correct values.

If you would like to remove the override, simply set all the values to 0:
`bounds_override = (0, 0, 0, 0)`
