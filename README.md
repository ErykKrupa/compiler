# Compiler
Project for Formal Languages And Translation Techniques course on V semester.

### Files
The samples folder contains code of language that can be compiled by the compilator.
In task.pdf you can find specific content of task.
The virtual_machine folder contains the code of the virtual machine on which compiler's
output code can be run. Virtual machine is available in two version: normal (maszyna-wirtualna)
or for big numbers (maszyna-wirtualna-cln) which requires additional package to run. Virtual
machine is written in C++ by Maciej Gębala, course lecturer.


### Packages
Python 3 and Sly are required to run compiler.
SLY (Sly Lex Yacc) is library for writing parsers and compilers.
CLN (Class Library for Numbers) is required to build virtual machine of big numbers.

### Packages installation
Example packages installation for Ubuntu.

Update apt-get:
```
sudo apt-get update
```
Install Python 3:
```
sudo apt-get install python3
```
Install PIP (standard package manager for Python packages) to be able to install Sly:
```
sudo apt-get install python3-pip
```
Install Sly using PIP for Python 3:
```
python3 -m pip install sly
```
If you want to use virtual machine of big numbers, you also need:
```
sudo apt-get install libcln-dev
```  


### Launching
Go to virtual_machine folder.

Build virtual machine:
```
make maszyna-wirtualna
```
or virtual machine of big numbers:
```
make maszyna-wirtualna-cln
```

Go to main folder.

Run compiler:
```
python3 src/compiler.py input_file.imp build/output_file.mr
```
or
```
./compiler input_file.imp build/output_file.mr
```
To run generated code use virtual machine:
```
virtual_machine/maszyna-wirtualna build/output_file.mr
```
or virtual machine for big numbers:
```
virtual_machine/maszyna-wirtualna-cln build/output_file.mr
```
