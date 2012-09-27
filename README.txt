The cell counter program is designed to load images of cells captured on a microscope and mark their coordinates. The coordinate files can then be used to train machine vision algorithms or human raters.

The program outputs coordinate files in .mat format. The files contain an array with the top left x,y and bottom right x, y cell coordinates. "Whole" arrays contain a fifth row identifying cell type. 
The included csv-mat converter can be used to generate tab-delimted .txt files from the .mat files. In the near future, the program will switch to csv generation as the default, and the converter will allow creation of .mat files. It will also become more robust against different naming conventions than it is currently.

The program is in ALPHA stage. A few things are broken, the code no doubt looks ugly, and some features that would be nice to have are missing. I'll try to fix it up when I can. However, I do not have the time and motivation to continue developing this program into a fully fledged software suite. I have uploaded it to Github as an early coding example.

I've also included 40 images of cells in a folder. These are in .jpg, not an ideal format, but necessary to pass them across the globe through some very cranky university email systems.

I've included 30 coordinate files marking the positions of the cells in the first 30 of 40 images. These files were generated using the cell counter program. Right now they are in Matlab format, but I will convert them soon in an upcoming update.

I've worked with a few collaborators who have tried to develop reliable identification coordinates using these data files, without great success. I welcome anyone who wants to try to work with these files, or email me at jtmorgan61@gmail.com if they need more assistance.
