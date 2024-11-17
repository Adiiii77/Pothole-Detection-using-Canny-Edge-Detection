from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
import cv2
import numpy as np
import os
import time
from matplotlib import pyplot as plt

views = Blueprint('views', __name__)


def load_and_process_image(image_path):
    """Load and preprocess the image."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    return img


def apply_image_processing(image):
    """Apply various image processing techniques."""
    blur = cv2.blur(image, (5, 5))
    gaussian_blur = cv2.GaussianBlur(image, (5, 5), 0)
    median_blur = cv2.medianBlur(image, 5)

    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(median_blur, kernel, iterations=1)
    dilation = cv2.dilate(erosion, kernel, iterations=5)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
    edges = cv2.Canny(dilation, 9, 220)

    return {
        'blur': blur,
        'gaussian_blur': gaussian_blur,
        'median_blur': median_blur,
        'erosion': erosion,
        'closing': closing,
        'edges': edges
    }


def save_plot(original, processed_images, output_path):
    """Save the plot of the results as an image."""
    plt.figure(figsize=(15, 10))

    plt.subplot(331)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title('Original')
    plt.xticks([]), plt.yticks([])

    positions = {
        'blur': 332,
        'gaussian_blur': 333,
        'median_blur': 334,
        'erosion': 335,
        'closing': 336,
        'edges': 338
    }

    for name, pos in positions.items():
        plt.subplot(pos)
        if name == 'edges':
            plt.imshow(processed_images[name], cmap='gray')
        else:
            plt.imshow(cv2.cvtColor(processed_images[name], cv2.COLOR_BGR2RGB))
        plt.title(name.replace('_', ' ').title())
        plt.xticks([]), plt.yticks([])

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Save uploaded file
        file = request.files['file']
        if file:
            # Ensure the upload folder exists
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Save the uploaded file
            filename = os.path.join(upload_folder, file.filename)
            file.save(filename)

            try:
                # Process the image
                original_image = load_and_process_image(filename)
                processed_images = apply_image_processing(original_image)

                # Save plot to static folder
                output_filename = f'output_{int(time.time())}.png'
                output_path = os.path.join(current_app.static_folder, output_filename)
                save_plot(original_image, processed_images, output_path)

                # Redirect to display result
                return redirect(url_for('views.show_plot', filename=output_filename))

            except Exception as e:
                return f"Error: {e}"

    return render_template('index.html', user=current_user)


@views.route('/show-plot/<filename>')
def show_plot(filename):
    """Show the processed image plot."""
    return render_template('plot.html',
                           image_url=url_for('static', filename=filename),
                           user=current_user)