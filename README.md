# README

A Python module to calculate the percentage of a range of RGB colors inside a given image. It was originally developed to quantify the biofluorescent body percentage of seahorses (*Hippocampus reidi*).

It is very important that the image have its background removed in such a way that only the bodyparts of interest remain. This step is crucial to guarantee that the percentage of pixels inside a range of RGB colors do not consider the background, reducing estimation error.

There are several functionalites inside the program:

- A color picker function
- A percentage estimator function
- A class representing the image being analysed
