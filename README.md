# Biofluorescence image analysis for Hippocampus reidi

This repository accompanies a scientific study of biofluorescence in the longsnout seahorse, Hippocampus reidi.

It demonstrates a reproducible Python workflow that estimates how much of the visible body area in a standardized photograph falls within RGB color ranges selected by the researcher. The repository is an example workflow for the article, not a general-purpose Python library.

## Scientific terms

**Biofluorescence** is visible light emitted by material after excitation by an external light source. This is the term used for the phenomenon represented in the standardized photographs. The term bioluminescence does not apply to these photographs.

A **standardized image** is a photograph acquired and prepared according to the study procedure, with comparable lighting, camera settings, framing, and excluded regions across samples.

The **body area** is the visible portion of the image considered part of the animal. In this workflow, it is represented by all non-black pixels, rather than the total image area.

An **RGB range** is a lower and upper red-green-blue triplet that defines a selected color interval in the image.

**Biofluorescence coverage** is the proportion of body-area pixels whose RGB values fall inside a selected RGB range. Coverage values are reported from 0 to 1 and rounded to four decimal places.

## What the analysis measures

The workflow classifies pixels as follows:

- background pixels are pure black pixels with RGB equal to (0, 0, 0);
- body pixels are every non-black pixel;
- selected-color pixels are body pixels inside a user-defined RGB range.

For each selected color, the reported value is:

~~~text
selected-color value =
selected body pixels / total body pixels
~~~

The background value is calculated separately:

~~~text
background value =
background pixels / total image pixels
~~~

These values are proportions from 0 to 1, rounded to four decimal places. The notebook, CSV export, and plots display them with exactly four decimal places (for example, `0.0125` or `0.0000`). Multiply a value by 100 when a percentage expressed from 0 to 100 is needed.

Each RGB range is evaluated independently. If two ranges overlap, the same pixel can be included in both ranges, so their values may add up to more than 1.

The analysis excludes background pixels from both the numerator and denominator of every selected color range. This prevents the black background from being counted as a selected color.

## Before starting

You need an internet connection for the first setup because uv downloads Python packages and creates the local project environment.

This project uses uv to install the exact dependency versions recorded in uv.lock. You do not need to create or activate a virtual environment manually.

## First-time setup

### Windows

1. Install uv.

Open PowerShell and copy the following command:

~~~powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
~~~

2. Close PowerShell and open it again.

3. Download this repository. On GitHub, choose Code, then Download ZIP. Extract the ZIP file.

If Git is already installed, you can instead run:

~~~powershell
git clone https://github.com/brunopiato/hippocampus_reidi.git
~~~

4. Open PowerShell in the extracted project folder.

5. Confirm that uv is available:

~~~powershell
uv --version
~~~

6. Install the project dependencies:

~~~powershell
uv sync
~~~

### macOS and Linux

1. Install uv.

Open Terminal and copy the following command:

~~~bash
curl -LsSf https://astral.sh/uv/install.sh | sh
~~~

2. Close Terminal and open it again.

3. Download this repository. On GitHub, choose Code, then Download ZIP. Extract the ZIP file.

If Git is already installed, you can instead run:

~~~bash
git clone https://github.com/brunopiato/hippocampus_reidi.git
~~~

4. Open Terminal in the extracted project folder.

5. Confirm that uv is available:

~~~bash
uv --version
~~~

6. Install the project dependencies:

~~~bash
uv sync
~~~

The first uv sync command creates a local .venv folder automatically. This folder is not part of the repository and does not need to be edited.

## Running the notebook

After the first-time setup, start JupyterLab by copying and running this complete command:

~~~bash
uv run jupyter lab --ServerApp.ip=127.0.0.1 --IdentityProvider.token="" --PasswordIdentityProvider.hashed_password="" notebooks/module_usage.ipynb
~~~

The `--ServerApp.ip`, `--IdentityProvider.token`, and `--PasswordIdentityProvider.hashed_password` options are required. Together, they keep JupyterLab accessible only from this computer (`127.0.0.1`) and disable the login token and password. Do not replace this command with `uv run jupyter lab`, because the shorter command will ask for a token.

On Windows, run the same command in PowerShell.

If JupyterLab asks for a token, close it, return to the project folder, and run the complete command above again. Do not expose this server to a network.

JupyterLab may not open the browser automatically. When the server starts, look in the terminal for a line similar to:

~~~text
http://127.0.0.1:8888/lab
~~~

Despite usually being `8888`, the port may have a different number. Copy the complete address shown in your terminal, open any web browser, paste the address into the address bar, and press Enter. You can also use the equivalent address `http://localhost:<port>/lab`, replacing `<port>` with the port shown in the terminal.

In JupyterLab:

1. Open notebooks/module_usage.ipynb if it is not already open.
2. Run the cells from top to bottom using the play button beside each cell or the Run All command.
3. Do not change the order of the cells.
4. The example uses the images and RGB ranges included in this repository.

## Notebook sections

The notebook demonstrates:

1. loading the project;
2. selecting RGB values interactively with the optional color picker;
3. analyzing one standardized seahorse image;
4. viewing the original image and generated masks;
5. analyzing every supported image in data/input;
6. saving the results to data/output/biofluorescence_results.csv.

The color picker is optional. The analysis can be run directly with the RGB ranges already written in the notebook.

## Preparing and replacing input images

The example images are stored in data/input. To analyze other photographs:

1. prepare the images using the same acquisition and background-removal procedure;
2. copy the prepared JPEG, JPG, or PNG files into data/input;
3. remove or move the example images if you do not want to analyze them;
4. update the RGB ranges in notebooks/module_usage.ipynb;
5. run the notebook from the first cell.

The percentage depends strongly on image preparation. Use consistent lighting, camera settings, white balance, camera distance, and background-removal procedures across samples.

Regions that must not contribute to the body-area calculation should be replaced with pure black (0, 0, 0). With JPEG files, compression can change black pixels into near-black pixels. PNG is preferable when exact black background pixels must be preserved.

## Choosing RGB ranges

An RGB range has a lower and upper red-green-blue triplet for each channel:

~~~python
color_ranges = {
    "green": ((0, 100, 0), (100, 255, 100)),
    "red": ((100, 0, 0), (255, 100, 100)),
    "blue": ((0, 35, 102), (204, 204, 255)),
}
~~~

The lower and upper values must be integers from 0 to 255. The lower value cannot be greater than the upper value for any channel.

Use the optional color picker to inspect pixels in an image and then define ranges that match the study protocol. The ranges included in the notebook are examples for the included images and should not be treated as universal biological thresholds.

## Comparing with Patternize

The optional helper `make_patternize_color_ranges` converts RGB center values and a `col_offset` into ranges that approximate the color-threshold rule used by the R package Patternize. The default `col_offset=0.10` matches Patternize's default color offset, but the argument can be changed to match the value used in the R analysis.

~~~python
rgb_colors = {
    "green": (110, 172, 3),
}

patternize_ranges = hr.make_patternize_color_ranges(
    rgb_colors,
    col_offset=0.10,
)

results = hr.analyze_image(image_path, patternize_ranges)
~~~

For folder analysis, `analyze_folder` can create these ranges directly:

~~~python
folder_results = hr.analyze_folder(
    "data/input",
    method="patternize",
    patternize_rgb_colors=rgb_colors,
    col_offset=0.10,
    output_path=None,
)
~~~

`method="standard"` is the default and expects `color_ranges` with lower and upper RGB bounds.
The Patternize mode expects RGB center values instead.

This helper matches the per-channel color tolerance only. It does not reproduce Patternize's landmark or registration alignment, image resampling, outline masking, or `patArea` denominator. Those settings must also be made equivalent before comparing final measurements.

## Why use this workflow?

For standardized images that are already aligned and use a consistent background, this workflow can provide a simpler and more transparent way to calculate per-image color coverage. Its main advantages are: no landmark or registration step, explicit pixel-level rules, preservation of the original image resolution, straightforward batch processing, and easy auditing of the RGB ranges and generated CSV results.

This project implements a color-selection approach inspired by Patternize's RGB threshold. It is not a reimplementation of Patternize and does not provide its image-alignment or pattern-homology workflow.

## Results

The notebook saves a CSV file at:

~~~text
data/output/biofluorescence_results.csv
~~~

The output directory is created automatically. The CSV is ignored by Git because it is a generated result.

Each row represents one image and one selected color. The CSV includes:

- image filename;
- total, body, and background pixel counts;
- background value as a proportion from 0 to 1, rounded to four decimals;
- selected-color pixel count and normalized value from 0 to 1, rounded to four decimals;
- lower and upper RGB bounds used for that color.

The background measurements are repeated in every color row for the same image so that each row can be interpreted independently.

The analysis can also be used directly from Python:

~~~python
from pathlib import Path

import hippocampus_reidi as hr

color_ranges = {
    "red": ((100, 0, 0), (255, 100, 100)),
}

results = hr.analyze_folder(
    Path("data/input"),
    color_ranges,
)

hr.plot_image_analysis(
    Path("data/input/imagem6.jpg"),
    color_ranges,
)
~~~

By default, analyze_folder writes data/output/biofluorescence_results.csv. To use another location, pass a directory or CSV path through output_path. To disable CSV export, pass output_path=None.

## Troubleshooting

### The command uv is not recognized

Close the terminal, open it again, and run uv --version. The uv installer adds the command to the user environment, but an already-open terminal may not know about that change.

### The notebook cannot import hippocampus_reidi

Close JupyterLab. In the project folder, run:

~~~bash
uv sync
uv run jupyter lab --ServerApp.ip=127.0.0.1 --IdentityProvider.token="" --PasswordIdentityProvider.hashed_password="" notebooks/module_usage.ipynb
~~~

Make sure the terminal is currently inside the project folder containing pyproject.toml.

### JupyterLab opens but the interactive color picker does not work

The color picker requires the notebook widget support. Run the notebook in JupyterLab rather than opening the file as a static document. If the optional picker still does not work, skip that section and use the RGB ranges already defined in the notebook.

### The percentage is zero or unexpectedly large

Check the selected RGB bounds and inspect the generated masks. Also confirm that the image uses the expected RGB colors and that the background is pure black. Overlapping ranges are independent and can count the same pixel more than once.

### There are no images to analyze

Confirm that the files are directly inside data/input and use the .jpg, .jpeg, or .png extensions.

## Verifying the project

These commands are mainly for maintainers:

~~~bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
~~~

## Citation

If this workflow contributes to a publication, cite the repository using the metadata in CITATION.cff. GitHub also displays this metadata through the Cite this repository option.

## License

This project is distributed under the MIT License.
