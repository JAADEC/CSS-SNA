# CSS-SNA
Social Network Analysis code for the Computational Social Science course of the Research Master Social Science

## Structure
Below the structure of the CSS SNA project is defined:
```
CSS-SNA
├── .venv                   Virtual environment
├── build                   Build info (unimportant)
├── css_sna.egg-info        Dependencies info (unimportant)
├── css-sna                 Main folder
│   ├── __pycache__         Cache (unimportant)
│   ├── __init__.py         (unimportant)
│   ├── graph.py            Python file (imported in main)
│   └── main.py             Main python file (importent)
├── .gitignore              Specifies files to ignore on git
├── README                  This guide
├── requirements.txt        Requirement specification
└── setup.py                Setup project with pip
```
As can be read above, the python files in the `css-sna` folder are the most important part. The other present files are just there to setup the project and install the necessary dependencies. If you want to run the project, go to the `main.py` file and run it. It should import all the other necessary files, like the `graph.py` file in this case.

## Setup
#### Download git and clone project
First [download git](https://git-scm.com/downloads) and then run the following command to clone this project:
```
git clone git@github.com:JAADEC/CSS-SNA.git
```

#### Setup virtual environment
The following steps should be run from inside the CSS-SNA folder so make sure to enter it:
```
cd CSS-SNA
```
In order to make sure all required packages are installed in a virtual environment, we will create a virtual environment specifically made for this project.

```
python3 -m venv .venv
```

Additionally, click the prompt to select the newly created virtual environment in vs code.

#### Activate virtual environment

On Linux, Unix or MacOS, using the terminal or bash shell:
```
source .venv/bin/activate
```
On Unix or MacOS, using the csh shell:
```
source .venv/bin/activate.csh
```
On Unix or MacOS, using the fish shell:
```
source .venv/bin/activate.fish
```
On Windows using the Command Prompt:
```
.venv\Scripts\activate.bat
```
On Windows using PowerShell:
```
.venv\Scripts\Activate.ps1
```

After activating the environment it should be shown by `(.venv)` in front of your directory.

#### Deactivate virtual environment


#### Install dependencies
All necessary dependencies are stored in `setup.py` and can be installed by first activating your virtual environment (see above). Now all dependencies can be installed by running the following command:

```
pip install .
```
When you get an error about `setuptools` not being defined, run the following command before retrying the install command from above:
```
pip install setuptools
```

#### Run project
Now, you should be good to go! Navigate to the `main.py` in the `css-sna` folder and run the file.