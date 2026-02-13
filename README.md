# README

A Python module to calculate the percentage of a range of RGB colors inside a given image. It was originally developed to quantify the biofluorescent body percentage of seahorses (*Hippocampus reidi*).

It is very important that the image have its background removed in such a way that only the bodyparts of interest remain. This step is crucial to guarantee that the percentage of pixels inside a range of RGB colors do not consider the background, reducing estimation error.

There are several functionalites inside the program:

- A color picker function (two versions, one using matplotlib, which is better for Jupyter Notebooks in Dev Containers, and one using OpenCV)
- A percentage estimator function
- A class representing the image being analysed

We added the .devcontainer functionallity, which allows the user to reproduce the exact environment in which it was developed and ran.
To install it follow the steps:
1. Install and run Docker
2. Install VS Code
3. Install the Dev Container extension
4. Install Git and clone the repository
5. Press Ctrl+Shift+P on the keyboard and type "Dev Containers: Open Folder in Container..."
6. Choose the repository folder you just downloaded
7. This will create a local Docker container which will have Debian 12 and Python 3.12 installed in it and all the dependencies it needs to run.
8. To close the container press the button in the bottom-left part of the screen where is written "Dev Container: Python 3" and choose "Close Remote Connection"