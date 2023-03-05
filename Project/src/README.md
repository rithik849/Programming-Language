**Building the Programming Language**

Building the language as an executable requires the use of plyinstaller available as a python module via pip.

To obtain pyinstaller run:

pip install pyinstaller

Once pyinstaller is available, to create an executable on your platform run, from the src project directory:

pyinstaller --onefile main.py --name lang

This will create a number of directories once the command has finished processing. The executable will be available at the dist directory, that is created by the command.

**Running the Programming Language**

The program runs as a command line/terminal executable.

It has one required flag -f for which we pass a program that conforms to the grammer. From here the program will run, and give an output, or an error report.

The other optional flags include:

* -t : To view the parse tree.
* -s : To view the symbol tables generated when runnig the program.
* -p : To view the python code equivalant of the program.
* -d : To view the duration of execution of the program.
* -h : For help in viewing the options of flags for the executable.
