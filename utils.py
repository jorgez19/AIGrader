import numpy as np
from PIL import Image, ExifTags


def resize_image_width(image, target_width=1024):
    width, height = image.size

    # Calculate new height to maintain aspect ratio
    aspect_ratio = height / width
    new_height = int(aspect_ratio * target_width)

    # Resize the image
    resized_image = image.resize((target_width, new_height), Image.LANCZOS)

    return resized_image


def fix_image_orientation(image):
    # Fix image orientation based on EXIF data
    try:
        # Check if the image has EXIF data
        if hasattr(image, "_getexif") and image._getexif() is not None:
            exif = dict(
                (ExifTags.TAGS.get(k, k), v) for k, v in image._getexif().items()
            )

            # Check if Orientation tag exists
            if "Orientation" in exif:
                orientation = exif["Orientation"]

                # Apply orientation corrections
                if orientation == 2:
                    # Horizontal flip
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    # Rotate 180 degrees
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 4:
                    # Vertical flip
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    # Transpose (flip horizontally and rotate 90 degrees)
                    image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                        Image.ROTATE_90
                    )
                elif orientation == 6:
                    # Rotate 270 degrees
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 7:
                    # Transverse (flip vertically and rotate 90 degrees)
                    image = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(
                        Image.ROTATE_90
                    )
                elif orientation == 8:
                    # Rotate 90 degrees
                    image = image.transpose(Image.ROTATE_90)
    except (AttributeError, KeyError, IndexError):
        # Just return the image if there's any error
        pass

    return image
