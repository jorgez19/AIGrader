from PIL import Image, ImageDraw, ImageFont
import sys


# Mark settings
MARK_OFFSET_X = 35  # How many pixels to the left of the coordinate to place the mark
MARK_SIZE = 40  # Size reference for all marks (both checkmark and X)
MARK_THICKNESS = max(3, MARK_SIZE // 8)  # Thickness for lines


def draw_checkmark(draw, position, size, color, thickness):
    """Draws a checkmark using lines."""
    x, y = position
    # Define points relative to the top-left corner (x, y) and size
    p1 = (x + size * 0.10, y + size * 0.50)  # Start point (left middle)
    p2 = (x + size * 0.35, y + size * 0.75)  # Mid point (bottom bend)
    p3 = (x + size * 0.85, y + size * 0.25)  # End point (top right)

    # Draw the two lines of the checkmark
    draw.line([p1, p2], fill=color, width=thickness, joint="curve")
    draw.line([p2, p3], fill=color, width=thickness, joint="curve")
    print(f"Drawing checkmark lines in {color} near ({position[0]}, {position[1]})")


def draw_x_mark(draw, position, size, color, thickness):
    """Draws an X using lines."""
    x, y = position
    # Define the four corners of an imaginary box where the X will be drawn
    margin = size * 0.1  # small margin from the edges
    top_left = (x + margin, y + margin)
    top_right = (x + size - margin, y + margin)
    bottom_left = (x + margin, y + size - margin)
    bottom_right = (x + size - margin, y + size - margin)

    # Draw the two diagonal lines of the X
    draw.line([top_left, bottom_right], fill=color, width=thickness, joint="curve")
    draw.line([top_right, bottom_left], fill=color, width=thickness, joint="curve")
    print(f"Drawing X-mark lines in {color} near ({position[0]}, {position[1]})")


def generate_marks_data(data):
    marks_data = []

    # Process each question to create mark data
    for i, question in enumerate(data["questions"]):
        # Skip questions that are missing required fields or don't have an answer written
        if not question.get("answer_written", False):
            continue

        # Get coordinates from the question data if available
        if "coordinates_of_answer" in question:
            coords = (
                question["coordinates_of_answer"]["x_coordinate"],
                question["coordinates_of_answer"]["y_coordinate"],
            )
        else:
            print(f"Warning: Question {i+1} is missing coordinates - skipping")
            continue

        # Create mark data
        if question["correctness"]:
            # Correct answer
            mark = {
                "coords": coords,
                "type": "check",
                "color": "green",
                "is_correct": True,
            }
        else:
            # Incorrect answer
            mark = {
                "coords": coords,
                "type": "x_mark",
                "color": "red",
                "is_correct": False,
            }

        marks_data.append(mark)

    return marks_data


# --- Main Script ---
def grade(INPUT_IMAGE_FILENAME, data=None, output_path=None):
    if data is None:
        print("No data provided. Using default test data.")
        # Define default test data here if needed
        data = {
            "correct_answers": 1,
            "questions": [
                {
                    "answer_written": True,
                    "correctness": True,
                    "question": "14x83",
                    "student_answer": "1162",
                    "correct_answer": "1162",
                    "coordinates_of_answer": {"x_coordinate": 69, "y_coordinate": 156},
                },
                {
                    "answer_written": True,
                    "correctness": False,
                    "question": "93x65",
                    "student_answer": "21",
                    "correct_answer": "6045",
                    "coordinates_of_answer": {"x_coordinate": 229, "y_coordinate": 158},
                },
            ],
            "total_amount_of_questions": 2,
        }

    # Generate marks data based on the questions
    marks_data = generate_marks_data(data)

    # Log summary of marking
    print(
        f"Marking {len(marks_data)} answers out of {data['total_amount_of_questions']} total questions"
    )
    print(f"Student got {data['correct_answers']} correct answers")

    try:
        img = Image.open(INPUT_IMAGE_FILENAME).convert("RGB")
        print(f"Successfully loaded image: {INPUT_IMAGE_FILENAME}")
    except FileNotFoundError:
        print(f"Error: Input image '{INPUT_IMAGE_FILENAME}' not found.")
        print("Please make sure the image file is in the same directory as the script.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    draw = ImageDraw.Draw(img)
    print("No fonts needed - all marks will be drawn using lines.")

    # Draw each mark based on its type
    for mark_info in marks_data:
        x, y = mark_info["coords"]
        color = mark_info["color"]
        mark_type = mark_info["type"]

        # Calculate the top-left position for the mark (offset to the left)
        mark_x = x - MARK_OFFSET_X

        if mark_type == "check":
            # Adjust y slightly down to better align visually
            mark_y = y + 5
            # Draw checkmark using lines
            draw_checkmark(draw, (mark_x, mark_y), MARK_SIZE, color, MARK_THICKNESS)
        elif mark_type == "x_mark":
            # Adjust y position to center the X mark
            mark_y = y - MARK_SIZE // 3
            # Draw X mark using lines
            draw_x_mark(draw, (mark_x, mark_y), MARK_SIZE, color, MARK_THICKNESS)
            status = "Incorrect"  # X marks are for incorrect answers
            print(
                f"Drawing X mark in {color} for {status} answer near ({x}, {y}) at ({mark_x}, {mark_y})"
            )
        else:
            print(f"Warning: Unknown mark type '{mark_type}' near ({x},{y}).")

    # Add a grade score at the top right of the image
    correct_count = sum(
        1 for q in data["questions"] if q.get("correctness", False) == True
    )
    grade_text = f"Score: {correct_count}/{data['total_amount_of_questions']}"
    # Font size for the grade text - adjust this value to change text size
    GRADE_FONT_SIZE = 20

    try:
        try:
            font = ImageFont.truetype("arial.ttf", GRADE_FONT_SIZE)
        except:
            font = ImageFont.load_default()
        try:
            # First try the newer method
            bbox = font.getbbox(grade_text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            try:
                # Fall back to textbbox if available (Pillow >=8.0.0)
                left, top, right, bottom = draw.textbbox((0, 0), grade_text, font=font)
                text_width = right - left
                text_height = bottom - top
            except AttributeError:
                # Last resort for very old Pillow versions
                text_width, text_height = draw.textsize(grade_text, font=font)

        # Position the text in the top right with 20px padding
        text_position = (img.width - text_width - 20, 10)

        # Draw the grade text at the top right of the image
        draw.text(text_position, grade_text, fill="blue", font=font)
        print(f"Added grade text: {grade_text} at position {text_position}")
    except Exception as e:
        print(f"Could not add grade text: {e}")
        # Fallback to a fixed position if all else fails
        draw.text((img.width - 200, 20), grade_text, fill="blue", font=font)
        print(f"Fallback: Added grade text at fixed position")

    # Save the modified image
    try:
        img.save(output_path)
        print(f"\nSuccessfully saved graded image as: {output_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

    return {
        "success": True,
        "output_file": output_path,
        "marked_answers": len(marks_data),
        "total_questions": data["total_amount_of_questions"],
        "correct_answers": data["correct_answers"],
    }
