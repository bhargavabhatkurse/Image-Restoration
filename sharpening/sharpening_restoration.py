
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


def unsharp_masking(image, sigma=1.5, strength=2.5):
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1 + strength, blurred, -strength, 0)
    # kernel = np.ones((3, 3), np.uint8)
    # dilated_edges = cv2.dilate(sharpened, kernel, iterations=2)

    return sharpened

def laplacian_sharpening(image, degree=0.7, kernel_size=5):
    # Split the image into color channels
    b, g, r = cv2.split(image)

    # Apply Gaussian blur to each color channel
    blurred_b = cv2.GaussianBlur(b, (kernel_size, kernel_size), 0)
    blurred_g = cv2.GaussianBlur(g, (kernel_size, kernel_size), 0)
    blurred_r = cv2.GaussianBlur(r, (kernel_size, kernel_size), 0)

    # Apply Laplacian operator to each color channel
    laplacian_b = cv2.Laplacian(blurred_b, cv2.CV_64F, ksize=3)
    laplacian_g = cv2.Laplacian(blurred_g, cv2.CV_64F, ksize=3)
    laplacian_r = cv2.Laplacian(blurred_r, cv2.CV_64F, ksize=3)

    # Perform sharpening by subtracting the Laplacian image from each color channel
    sharp_b = np.clip(b - degree * laplacian_b, 0, 255).astype(np.uint8)
    sharp_g = np.clip(g - degree * laplacian_g, 0, 255).astype(np.uint8)
    sharp_r = np.clip(r - degree * laplacian_r, 0, 255).astype(np.uint8)

    # Merge the sharpened color channels back into a BGR image
    sharp_image = cv2.merge((sharp_b, sharp_g, sharp_r))

    return sharp_image

def calculate_total_variation(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the horizontal and vertical gradients
    gradient_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    # Compute the total variation by summing the absolute values of the gradients
    total_variation = cv2.sumElems(cv2.addWeighted(cv2.convertScaleAbs(gradient_x), 0.5,
                                                   cv2.convertScaleAbs(gradient_y), 0.5, 0))[0]

    return total_variation

def process_image():
    global image, sigma, strength, degree, kernel_size

    # Perform unsharp masking
    unsharp_image = unsharp_masking(image, sigma.get(), strength.get())
    laplacian_image = laplacian_sharpening(image, degree.get(), kernel_size.get())

    # Display the original and sharpened images
    cv2.imshow('Original Image', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    cv2.imshow('Unsharp Masking', cv2.cvtColor(unsharp_image, cv2.COLOR_BGR2RGB))
    cv2.imshow('Laplacian', cv2.cvtColor(laplacian_image, cv2.COLOR_BGR2RGB))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Calculate the total variation for each image
    tv1 = calculate_total_variation(unsharp_image)
    tv2 = calculate_total_variation(laplacian_image)

    # Compare the total variations
    if tv1 > tv2:
        messagebox.showinfo("Result", "Unsharp masking has more detail and better quality.")
    elif tv1 < tv2:
        messagebox.showinfo("Result", "Laplacian sharpening has more detail and better quality.")
    else:
        messagebox.showinfo("Result", "Both methods have the same level of detail and quality.")




# TKinter Code
def open_image():
    global image
    image_name = file_entry.get()
    if image_name:
        image = cv2.imread(image_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert the image to PIL format
        pil_image = Image.fromarray(image)

        # Create a Tkinter-compatible photo image
        photo = ImageTk.PhotoImage(pil_image)

# Create the main window
window = tk.Tk()
window.title("Image Restoration using Image Sharpening")
window.geometry("400x800")

# Create a label and entry for the file name
description = tk.Label(window, text="By Bhargava Bhatkurse and Akash Gauns\n(Image Processing Project)\n\n")
description.pack()


# Create a label and entry for the file name
file_label = tk.Label(window, text="Image File:")
file_label.pack()
file_entry = tk.Entry(window)
file_entry.pack()

# Create a button to open the image
open_button = tk.Button(window, text="Open Image", command=open_image)
open_button.pack()


# Create sliders for the parameters
sigma_label = tk.Label(window, text="\n\nUnsharp masking method: \nSigma:")
sigma_label.pack()
sigma = tk.DoubleVar()
sigma_slider = tk.Scale(window, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, variable=sigma)
sigma_slider.set(2.5)
sigma_slider.pack()

strength_label = tk.Label(window, text="Strength:")
strength_label.pack()
strength = tk.DoubleVar()
strength_slider = tk.Scale(window, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, variable=strength)
strength_slider.set(3)
strength_slider.pack()

degree_label = tk.Label(window, text="\n\nLaplacian Method: \n\nDegree\n(1:full Laplacian mask: \n0: no mask):\n")
degree_label.pack()
degree = tk.DoubleVar()
degree_slider = tk.Scale(window, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, variable=degree)
degree_slider.set(0.7)
degree_slider.pack()

kernel_size_label = tk.Label(window, text="\n\nKernel Size(for the blur):")
kernel_size_label.pack()
kernel_size = tk.IntVar()
kernel_size_slider = tk.Scale(window, from_=3, to=9, resolution=2, orient=tk.HORIZONTAL, variable=kernel_size)
kernel_size_slider.set(5)
kernel_size_slider.pack()


process_button = tk.Button(window, text="Process Image", command=process_image)
process_button.pack()

# Start the Tkinter event loop
window.mainloop()
