# Biofluorescence image analysis for *Hippocampus reidi*

This repository contains a reproducible workflow for estimating how much of an animal's
visible body area falls within selected RGB color ranges. It was developed to support the
study of biofluorescence in the longsnout seahorse, *Hippocampus reidi*.

The analysis can be used with one image or with a folder of images. An example dataset and
a ready-to-run Jupyter notebook are included. Also an auxiliary function to get RGB values 
from pixels was developed here.

## What the analysis measures

The program separates each image into:

- background pixels, defined as pure black (`RGB = 0, 0, 0`) are desregarded of the analysis;
- body pixels, defined as every non-black pixel;
- pixels that fall within each RGB range selected by the researcher.

For each color range, the reported value is:

```text
percentage = pixels inside the RGB range / non-black body pixels × 100
```

The program also displays the original image and the masks used in the calculation, making
it possible to visually inspect the classification.

## Before starting

Install [Python 3.12 or newer](https://www.python.org/downloads/). JupyterLab and all other
required programs will be installed automatically in the steps below.

Download the repository using one of these options:

- On GitHub, select **Code → Download ZIP**, then extract the downloaded file.
- If Git is installed, run:

```bash
git clone https://github.com/brunopiato/hippocampus_reidi.git
cd hippocampus_reidi
```

Open a terminal inside the downloaded project folder and follow the instructions for your
operating system. Copy and run each command one at a time.

## Run the notebook

### Windows

Open PowerShell in the project folder and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m jupyter lab notebooks/module_usage.ipynb
```

### macOS and Linux

Open Terminal in the project folder and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m jupyter lab notebooks/module_usage.ipynb
```

JupyterLab will open the notebook in your web browser. Run the cells from top to bottom
using the **Run** button. Keep the terminal open while using the notebook. To stop
JupyterLab, return to the terminal and press `Ctrl+C`.

After the first installation, only the final command is needed to reopen the notebook.

## Using the notebook

The example notebook is organized into four parts:

1. Load the analysis program.
2. Select an image and define the RGB ranges.
3. Analyze one image and inspect its masks and percentages.
4. Apply the same RGB ranges to all supported images in a folder.

The notebook also includes an optional interactive color picker. Click points on the image
to inspect their RGB values and select **End color selection** when finished.

To analyze your own material:

1. Add the prepared images to a folder inside the project.
2. Change `image_path` or `folder_path` in the notebook as needed.
3. Replace the example RGB ranges with ranges calibrated for your study.
4. Run the analysis and visually inspect every generated mask.

JPEG, PNG, and JPG files are supported.

## Preparing images

Image preparation directly affects the calculated percentages.

- Remove all regions that must not be included in the body-area calculation.
- Replace the removed background with pure black (`RGB = 0, 0, 0`).
- Prefer PNG after background removal. JPEG compression can turn black pixels into
  near-black pixels, which the current method does not classify as background.
- Use consistent lighting, camera settings, white balance, distance, and image-processing
  procedures across samples.
- Calibrate RGB ranges for the acquisition conditions of each study. The ranges included in
  the notebook are examples and should not be treated as universal biofluorescence ranges.

## Interpreting the results

Each selected color produces a pixel count, a percentage, and a visual mask. The background
percentage is calculated relative to the complete image; color percentages are calculated
relative to the non-black body area.

Color ranges are evaluated independently. If ranges overlap, a pixel can be counted in more
than one range and the percentages may sum to more than 100%. Researchers should therefore
document the selected RGB bounds and inspect the masks before comparing individuals or
experimental groups.

## Troubleshooting

If the notebook reports that `hippocampus_reidi` cannot be found, close JupyterLab and run
the installation command again from the project folder.

When using VS Code instead of JupyterLab, install the official Python and Jupyter extensions
and select the Python environment located in the project's `.venv` folder as the notebook
kernel.

## Citation

If this software contributes to a publication, cite it using the metadata provided in
[`CITATION.cff`](CITATION.cff). GitHub also displays this information through the
**Cite this repository** option.

## License

This project is distributed under the [MIT License](LICENSE).

## Development

Technical information for contributors and maintainers is available in
[`DEVELOPMENT.md`](DEVELOPMENT.md).
