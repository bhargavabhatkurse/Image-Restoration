import cv2
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

drawing = False
x_start, y_start = 0, 0
x_end, y_end = 0, 0
image = None
image_copy = None

def select_roi(event, x, y, flags, param):  #region of interest
    global x_start, y_start, x_end, y_end, drawing, image_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_start, y_start = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_end, y_end = x, y
        cv2.rectangle(image_copy, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        cv2.imshow("Image", image_copy)

def open_image():
    # Read the filename from the entry field
    filename = filename_entry.get()
    filename = "images/" + filename   #folder name is 'images' where images are stored

    # Read the image
    global image, image_copy
    image = cv2.imread(filename)  
    if image is None:
        print("Failed to load the image:", filename)
        return

    # Create a copy of the image for display
    image_copy = image.copy()

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", select_roi)
    cv2.imshow("Image", image)

def apply_filters():
    
    # Apply the filters and process the ROI
    if image is None:
        print("No image loaded.")
        return

    # Read the values from the sliders
    blur_kernel_size = blur_slider.get()
    dilation_iterations = dilation_slider.get()
    threshold_value = threshold_slider.get()
    threshold_type = cv2.THRESH_BINARY if threshold_mode.get() == 0 else cv2.THRESH_BINARY_INV

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(image, (blur_kernel_size, blur_kernel_size), 0)

    if threshold_mode.get() == 0:  # Local Thresholding
        # Define the coordinates of the ROI
        roi = image[y_start:y_end, x_start:x_end]

        # ROI to grayscale
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to the grayscale ROI
        _, binary_roi = cv2.threshold(gray_roi, threshold_value, 255, threshold_type)

        # Create a mask with the same dimensions as the original image
        mask = np.zeros_like(image, dtype=np.uint8)

        # Insert the thresholded ROI into the mask
        mask[y_start:y_end, x_start:x_end] = cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2BGR)
    else:  # Thresholding over the full image
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to the grayscale image
        _, mask = cv2.threshold(gray_image, threshold_value, 255, threshold_type)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Perform Canny edge detection
    edges = cv2.Canny(mask, 30, 100)

    # Dilate the edges to make them thicker
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=dilation_iterations)

    inpainted = cv2.inpaint(image, dilated_edges, inpaintRadius=3, flags=cv2.INPAINT_NS)

    cv2.imshow("Restored image", inpainted)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Create the main window
root = tk.Tk()
root.title("Image Restoration")
root.geometry("600x600")  # Set the width and height of the window

label = tk.Label(root, text="\n\nThis software restores images using edge inpainting\n")
label.pack()

label = tk.Label(root, text="Made by\nBhargava Bhatkurse and Akash Gauns") #space
label.pack()

label = tk.Label(root, text="\n\nEnter the file name(with extension) and hit enter")
label.pack()

label = tk.Label(root, text="After image opens, select the region to restore")
label.pack()

# Create the filename entry field
filename_entry = tk.Entry(root)
filename_entry.pack()

# Bind the Enter key to open the image
root.bind('<Return>', lambda event: open_image())

label = tk.Label(root, text="\n") #space
label.pack()

# Create the sliders
blur_slider = tk.Scale(root, from_=1, to=31, orient=tk.HORIZONTAL, label="Blur Kernel Size")
blur_slider.set(13)
blur_slider.pack()

label = tk.Label(root, text="\n") #space
label.pack()

dilation_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, label="Dilation Iter")
dilation_slider.set(5)
dilation_slider.pack()

label = tk.Label(root, text="\n") #space
label.pack()

threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Threshold")
threshold_slider.set(250)
threshold_slider.pack()


# Create the threshold mode radio buttons
threshold_mode = tk.IntVar()
threshold_mode.set(0)

local_threshold_radio = tk.Radiobutton(root, text="Thresholding over a Region", variable=threshold_mode, value=0)
local_threshold_radio.pack()

full_image_threshold_radio = tk.Radiobutton(root, text="Threshold over Full Image", variable=threshold_mode, value=1)
full_image_threshold_radio.pack()

# Create the apply button
apply_button = tk.Button(root, text="Restore", command=apply_filters)
apply_button.pack()

# Start the Tkinter event loop
root.mainloop()
