# -*- coding: utf-8 -*-
# @Author: Bruno Piato
# @Date:   2026-02-12 07:38:47
# @Last Modified by:   Bruno Piato
# @Last Modified time: 2026-02-12 07:53:16
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display


def calculate_color_percentage(image_path, color_names: list, color_ranges: list):
    try:
        image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        total_pixels = image.shape[0] * image.shape[1]
    except:
        raise ValueError(
            "Unable to read the image file. Please check the file path.")

    if len(color_names) != len(color_ranges):
        raise ValueError(
            f"The number of colors should be the same as the number of color range pairs. There were {len(color_names)} color_names and {len(color_ranges)} colors.")

    colors_dictionary = {}
    for i, color_name in enumerate(color_names):
        new_dictionary = {}
        new_dictionary['lower'] = np.array(color_ranges[i][0])
        new_dictionary['upper'] = np.array(color_ranges[i][1])

        colors_dictionary[color_name] = new_dictionary

    image_mask = cv2.inRange(image,  np.array([0, 0, 0]),  np.array([0, 0, 0]))
    image_pixels = cv2.countNonZero(image_mask)
    image_percentage = (image_pixels/total_pixels)

    for color in colors_dictionary.keys():
        mask = cv2.inRange(
            image, colors_dictionary[color]['lower'], colors_dictionary[color]['upper'])
        pixels = cv2.countNonZero(mask)
        percentage = pixels/(total_pixels - image_pixels)

        colors_dictionary[color]['pixels'] = pixels
        colors_dictionary[color]['percentage'] = percentage

        globals()[f'{color}_mask'] = mask
        globals()[f'{color}_pixels'] = pixels
        globals()[f'{color}_percentage'] = percentage

    plt.figure(figsize=(12, 6))
    plot_ncols = ((2+len(color_names))//2)+1
    plot_nrows = 2

    plt.subplot(plot_nrows, plot_ncols, 1)
    plt.imshow(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB))
    plt.title('Original Image')
    plt.axis('off')

    plt.subplot(plot_nrows, plot_ncols, 2)
    plt.imshow(image_mask, cmap='gray')
    plt.title('Image mask')
    plt.axis('off')
    plt.text(0.5, -0.05, round(image_percentage, 3), ha='center',
                va='top', transform=plt.gca().transAxes)

    position = 3
    for color in color_names:
        plt.subplot(plot_nrows, plot_ncols, position)
        plt.imshow(globals()[f'{color}_mask'], cmap='gray')
        plt.title(F'{color.capitalize()} mask')
        plt.axis('off')
        plt.text(0.5, -0.05, round(globals()[f'{color}_percentage'], 3),
                    ha='center', va='top', transform=plt.gca().transAxes)

        position += 1

    plt.subplots_adjust(hspace=0.4)

    colors_dictionary['image'] = {'lower': np.array([0, 0, 0]),
                                    'upper': np.array([0, 0, 0]),
                                    'pixels': image_pixels,
                                    'percentage': image_percentage}

    for item in colors_dictionary.items():
        print(
            f"The {item[0].lower()} percentage is {round(item[1]['percentage']*100, 3)}%.")

    return colors_dictionary


def pick_color_from_image(image_path):
    colors = []  # List to store the picked RGB colors

    # Function to handle mouse click event
    def pick_color(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Read the color at the clicked pixel (BGR format)
            b, g, r = image[y, x]
            # Append the color in RGB format
            colors.append(list([int(r), int(g), int(b)]))
            print(f"Color at ({x}, {y}): R={r}, G={g}, B={b}")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise(ValueError("Error loading image. Please provide a valid path to the image file."))

    # Create an OpenCV window and set the mouse callback
    cv2.namedWindow('Image')
    cv2.setMouseCallback('Image', pick_color)

    # Show the image using OpenCV
    while True:
        cv2.imshow('Image', image)
        key = cv2.waitKey(1)

        # Check if the window is closed or if 'ESC' is pressed
        if key == 27 or cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            break

    # Destroy all OpenCV windows
    cv2.destroyAllWindows()

    return colors



def pick_color_from_image_matplotlib(image_path):
    colors = []

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Error loading image. Please provide a valid path to the image file.")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_title("Click on the image to pick colors")
    ax.axis("off")

    out = widgets.Output()
    done = widgets.Button(
        description="End color selection",
        button_style="success"
    )

    def onclick(event):
        if event.inaxes != ax or event.xdata is None:
            return

        x, y = int(event.xdata), int(event.ydata)
        r, g, b = image[y, x]
        colors.append([int(r), int(g), int(b)])

        with out:
            print(f"Pixel ({x}, {y}) → RGB = {r}, {g}, {b}")

        ax.scatter(x, y, c='red', s=40)
        fig.canvas.draw_idle()

    def finish(_):
        plt.close(fig)
        with out:
            print("\nSelection finished.")
            print("Captured colors:", colors)

    fig.canvas.mpl_connect("button_press_event", onclick)
    done.on_click(finish)

    display(done, out)
    plt.show()

    return colors



def process_images_in_folder(folder_path, color_names, color_ranges):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            print(filename)
            image_path = os.path.join(folder_path, filename)
            result = calculate_color_percentage(image_path, color_names, color_ranges)
            results.append((filename, result))
    return results
