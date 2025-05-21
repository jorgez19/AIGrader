from PIL import Image, ImageDraw, ImageFont


def overlay_grid_on_image(
    image_path,
    grid_spacing=50,
    grid_opacity=50,
    label_inset=10,
    label_font_size=14,
    output_path="grid_overlay.png",
):

    # Overlays a grid with pixel counts onto an existing image.

    try:
        # Open the existing image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        # Create a transparent overlay image for the grid
        overlay = Image.new(
            "RGBA", (width, height), (0, 0, 0, 0)
        )  # Transparent background
        draw = ImageDraw.Draw(overlay)

        grid_color = (0, 0, 0, grid_opacity)  # Black grid with specified opacity
        grid_font_color = (255, 0, 0, 180)  # Red font with slight transparency

        try:
            grid_font = ImageFont.truetype("arial.ttf", label_font_size)
        except IOError:
            grid_font = ImageFont.load_default()

        # Draw vertical grid lines and pixel labels
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            draw.text(
                (x + 2, label_inset), str(x), fill=grid_font_color, font=grid_font
            )  # Label on top

        # Draw horizontal grid lines and pixel labels
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            draw.text(
                (label_inset, y + 2), str(y), fill=grid_font_color, font=grid_font
            )  # Label on left

        combined = Image.alpha_composite(img, overlay).convert("RGB")

        # Save the combined image
        combined.save(output_path)
        print(f"Grid overlay image saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
