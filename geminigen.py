import base64
import os
import json
from google import genai
from google.genai import types


def generate(image_path=None, prompt_text="", api_key=None):
    if not api_key:
        raise ValueError("API key is required")

    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.5-flash-preview-04-17"

    parts = []
    if image_path:
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            # Encode the image data as base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            parts.append(
                types.Part.from_bytes(
                    mime_type="""image/jpeg""",
                    data=base64.b64decode(image_base64),
                )
            )
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return  # Exit if image file is not found
        except Exception as e:
            print(f"Error reading image file: {e}")
            return

    if prompt_text:
        parts.append(types.Part.from_text(text=prompt_text))

    contents = [
        types.Content(
            role="user",
            parts=parts,
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=8000),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=[
                "questions",
                "total_amount_of_questions",
                "correct_answers",
            ],
            properties={
                "questions": genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        required=[
                            "question",
                            "student_answer",
                            "correct_answer",
                            "correctness",
                            "answer_written",
                            "coordinates_of_answer",
                        ],
                        properties={
                            "question": genai.types.Schema(
                                type=genai.types.Type.STRING,
                            ),
                            "student_answer": genai.types.Schema(
                                type=genai.types.Type.STRING,
                            ),
                            "correct_answer": genai.types.Schema(
                                type=genai.types.Type.STRING,
                            ),
                            "correctness": genai.types.Schema(
                                type=genai.types.Type.BOOLEAN,
                            ),
                            "answer_written": genai.types.Schema(
                                type=genai.types.Type.BOOLEAN,
                            ),
                            "coordinates_of_answer": genai.types.Schema(
                                type=genai.types.Type.OBJECT,
                                required=["x_coordinate", "y_coordinate"],
                                properties={
                                    "x_coordinate": genai.types.Schema(
                                        type=genai.types.Type.INTEGER,
                                    ),
                                    "y_coordinate": genai.types.Schema(
                                        type=genai.types.Type.INTEGER,
                                    ),
                                },
                            ),
                        },
                    ),
                ),
                "total_amount_of_questions": genai.types.Schema(
                    type=genai.types.Type.INTEGER,
                ),
                "correct_answers": genai.types.Schema(
                    type=genai.types.Type.INTEGER,
                ),
            },
        ),
    )
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            json_response += chunk.text
            print(chunk.text, end="")  # Still print for debugging

        # Convert the JSON booleans (true/false) to Python booleans (True/False)
        if json_response:

            # Convert the parsed JSON to a Python-compatible string
            # This will replace 'true' with 'True' and 'false' with 'False'
            python_compatible_data = json_response.replace(
                '"correctness": true', '"correctness": True'
            )
            python_compatible_data = python_compatible_data.replace(
                '"correctness": false', '"correctness": False'
            )
            python_compatible_data = python_compatible_data.replace(
                '"answer_written": true', '"answer_written": True'
            )
            python_compatible_data = python_compatible_data.replace(
                '"answer_written": false', '"answer_written": False'
            )

            # Print a delimiter to separate the JSON output from the Python-compatible output
            print("\n\n# Python-compatible data (for direct use):")
            print(python_compatible_data)

            return python_compatible_data
    except Exception as e:
        print(f"An error occurred: {e}")
