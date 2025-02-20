# Branch Creator

This is a simple app designed to quickly create app for Avanan repos with correctly formatted branch names.


## Installation

1. Copy the repository:

```
git clone https://github.com/chkp-yohain/branch-creator.git
```

3. Create you virtual environment:

```
python3 -m venv venv
```

4. Access your virtual environment:

```
source venv/bin/activate
```

5. Install requirements:

```
pip install -r requirements.txt
```

6. Run the app:

```
python3 main.py
```

## Optional
If you want to run the app as a mac app (.app file), run the following command:

```
pyinstaller -w --clean --name="BranchCreator" --icon=app_icon.icns main.py
```

After running the command, you can access your newly created app in the dist folder.
