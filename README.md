# Quick Start #

To run this software on your computer, first make sure you have [Python 3.10](https://www.python.org/downloads/) or later installed. Then do the following:

 - Clone the repo using git or download as zip
 - run `cd path/to/airdrop` to change the directory to wherever Airdrop is sourced in your preferred terminal emulator
 - Activate virtual env by running one of the following commands respective to your operating system:

```bash
# On Unix or MacOS, using the bash shell
source ./venv/bin/activate

# On Unix or MacOS, using the csh shell
source ./venv/bin/activate.csh

# On Unix or MacOS, using the fish shell
source ./venv/bin/activate.fish

# On Windows using the Command Prompt
venv\Scripts\activate.bat

# On Windows using PowerShell
venv\Scripts\Activate.ps1
```

 - Install the required dependencies by running `python3 -m pip install -r ./requirements.txt`
 - Run the actual program with `python3 -m airdrop`
