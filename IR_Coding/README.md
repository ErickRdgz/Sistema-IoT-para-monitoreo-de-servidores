## Encoding and decoding of IR commands

Using an algorithm developed in Python, the bit frames are constructed according to the encoding tables and the desired instructions. 
The LIRC software library was used to transmit and receive infrared commands with the raspberry PI. LIRC does not have a Python library focused on the execution of its functions from this programming language, this must be executed from terminal so the 'OS' library has been used to execute commands to terminal from Python.
