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

Windows and macOS users should install
[Python 3.12 or newer](https://www.python.org/downloads/). Ubuntu users should follow the
Ubuntu instructions below because its Python installation separates support for virtual
environments into an additional system package. JupyterLab and the analysis dependencies
will be installed during the first-time setup.

Download the repository using one of these options:

- On GitHub, select **Code → Download ZIP**, then extract the downloaded file.
- If Git is installed, run:

```bash
git clone https://github.com/brunopiato/hippocampus_reidi.git
cd hippocampus_reidi
```

Open a terminal inside the downloaded project folder and follow the instructions for your
operating system. Copy and run each command one at a time.

## First-time setup

The `.venv` folder is not included in the downloaded repository. It stores the local Python
environment and must be created once on each computer. After checking the Python version,
the instructions create this folder and install the analysis program and its dependencies
inside it.

### Windows — first time

Open PowerShell in the project folder. First, confirm that Python 3.12 or newer is available:

```powershell
py -3.12 --version
```

Create the `.venv` folder:

```powershell
py -3.12 -m venv .venv
```

Install the required programs inside `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

Open the notebook:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab notebooks/module_usage.ipynb
```

### macOS — first time

Open Terminal in the project folder. First, confirm that Python 3.12 or newer is available:

```bash
python3 --version
```

Create the `.venv` folder:

```bash
python3 -m venv .venv
```

Install the required programs inside `.venv`:

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

Open the notebook:

```bash
.venv/bin/python -m jupyterlab notebooks/module_usage.ipynb
```

### Ubuntu 24.04 or newer — first time

Ubuntu provides virtual-environment support as a separate package. Install Python and this
package before creating `.venv`:

```bash
sudo apt update
sudo apt install python3 python3-venv
```

Confirm that the installed Python version is 3.12 or newer:

```bash
python3 --version
```

Create the `.venv` folder:

```bash
python3 -m venv .venv
```

Install the required programs inside `.venv`:

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

Open the notebook:

```bash
.venv/bin/python -m jupyterlab notebooks/module_usage.ipynb
```

On another Linux distribution, install Python 3.12 or newer and its `venv` package using
the distribution's package manager, then follow the same commands used for Ubuntu.

JupyterLab will open the notebook in your web browser. Run the cells from top to bottom
using the **Run** button. Keep the terminal open while using the notebook. To stop
JupyterLab, return to the terminal and press `Ctrl+C`.

## Open the notebook again later

As long as the `.venv` folder still exists, do not recreate the environment or reinstall the
dependencies. Open a terminal in the project folder and run only the command for your
operating system.

On Windows:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab notebooks/module_usage.ipynb
```

On macOS or Linux:

```bash
.venv/bin/python -m jupyterlab notebooks/module_usage.ipynb
```

If `.venv` has been deleted, repeat the **First-time setup** instructions.

## Use the notebook in Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/) can be used instead of opening
JupyterLab in a web browser.

Before using VS Code for the first time:

1. Complete the **First-time setup** for your operating system, including the commands that
   create `.venv` and install the required programs. The command that opens JupyterLab can
   be skipped.
2. Install Visual Studio Code.
3. Open Visual Studio Code and install the official **Python** and **Jupyter** extensions
   from Microsoft.
4. Select **File → Open Folder** and open the downloaded `hippocampus_reidi` project folder.
5. In the file explorer inside VS Code, open `notebooks/module_usage.ipynb`.
6. Select **Select Kernel** in the upper-right corner of the notebook.
7. Choose **Python Environments**, then select the Python interpreter inside the project's
   `.venv` folder.

The interpreter path ends with `.venv\Scripts\python.exe` on Windows or
`.venv/bin/python` on macOS and Linux. After selecting it, run the notebook cells from top
to bottom using **Run All** or the run button beside each cell.

On later uses, open the same project folder and notebook. VS Code will normally remember the
selected environment. If it does not, repeat the **Select Kernel** steps above.

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

### The `.venv` Python reports `No module named pip`

This means that `.venv` was only partially created. On Ubuntu, it normally happens when the
`python3-venv` system package was not installed first. Preserve the incomplete folder under
a different name:

```bash
mv .venv .venv-incomplete
```

Then install `python3-venv` and repeat the Ubuntu first-time setup:

```bash
sudo apt update
sudo apt install python3 python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

After the notebook is working, `.venv-incomplete` can be deleted.

### The notebook cannot import `hippocampus_reidi`

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
