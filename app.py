import streamlit as st
from PIL import Image
import os
import tempfile
import atexit
from geminigen import generate
from grade import grade
from graph import overlay_grid_on_image
from utils import resize_image_width, fix_image_orientation
from counter import read_counter, update_counter
import streamlit as st
from streamlit_cropperjs import st_cropperjs
from styles import load_css

# Custom CSS optimized for mobile with navigation styling
st.markdown(load_css(), unsafe_allow_html=True)
# Set page configuration
st.set_page_config(
    page_title="Homework Grader",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Define pages
def grader_page():
    st.title("Jorge's Grading App")
    st.subheader("Upload a picture of homework to grade")

    # Step 1: Upload Image
    if not st.session_state.upload_complete:
        uploaded_file = st.file_uploader(
            "Drag and drop or click to upload homework image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="file_uploader",
        )

        if uploaded_file is not None:
            # Clean old temp files before processing new ones
            clean_temp_files()

            # Create a temporary file to store the uploaded image
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f"_{uploaded_file.name}"
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                input_image_path = tmp_file.name

            # Add to temp files list for later cleanup
            st.session_state.temp_files.append(input_image_path)

            # Read image and fix orientation
            input_image = Image.open(input_image_path)
            fixed_image = fix_image_orientation(input_image)
            fixed_image = resize_image_width(fixed_image, target_width=1024)
            fixed_image.save(input_image_path)

            # Update session state
            st.session_state.original_image_path = input_image_path
            st.session_state.upload_complete = True
            st.rerun()

    # Step 2: Crop Image (if upload is complete but cropping is not)
    elif st.session_state.upload_complete and not st.session_state.cropping_complete:
        st.markdown("### Step 2: Crop Homework Image")
        st.write(
            "Drag to select the area you want to crop, then click the 'Crop Image' button."
        )

        # Read the image as bytes for cropperjs
        with open(st.session_state.original_image_path, "rb") as file:
            img_bytes = file.read()

        # Display cropper with responsive container
        st.markdown(
            '<div class="crop-container">',
            unsafe_allow_html=True,
        )

        # Mobile-optimized cropper
        cropped_pic = st_cropperjs(
            pic=img_bytes, btn_text="Crop Image", key="homework_cropper", size=0.01
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if cropped_pic is not None:
            # Save the cropped image
            cropped_path = os.path.join(
                tempfile.gettempdir(),
                f"cropped_{os.path.basename(st.session_state.original_image_path)}",
            )

            # Check if cropped_pic is bytes or a string
            if isinstance(cropped_pic, str):
                # Sometimes st_cropperjs returns a base64 string
                import base64

                try:
                    # Try to decode if it's a base64 string
                    if "base64," in cropped_pic:
                        base64_data = cropped_pic.split("base64,")[1]
                        with open(cropped_path, "wb") as f:
                            f.write(base64.b64decode(base64_data))
                    else:
                        # If it's some other string format, try saving it directly
                        with open(cropped_path, "wb") as f:
                            f.write(cropped_pic.encode("utf-8"))
                except Exception as e:
                    st.error(f"Error processing cropped image: {str(e)}")
                    return
            else:
                # If it's bytes, save directly
                with open(cropped_path, "wb") as f:
                    f.write(cropped_pic)

            # Add to temp files list
            st.session_state.temp_files.append(cropped_path)
            st.session_state.cropped_image = cropped_path
            st.session_state.cropping_complete = True

            # Show the cropped image and proceed button
            st.markdown("### Cropped Image")
            st.image(cropped_path, width=400)

            # Make buttons more mobile-friendly by adding space between them
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Continue with This Crop", use_container_width=True):
                    st.session_state.cropping_complete = True
                    st.rerun()
            with col2:
                if st.button("Start Over", use_container_width=True):
                    reset_app()

    # Step 3: Process the cropped image
    elif st.session_state.cropping_complete and not st.session_state.grading_complete:
        # Process the image
        with st.status("Grading homework...", expanded=True) as status:
            st.write("Loading image...")
            st.write("Adding grid overlay...")
            st.write("Generating grading data...")
            st.write("Applying grades to image...")

            try:
                graded_image_path, python_compatible_data = process_image(
                    st.session_state.cropped_image
                )
                # Store results for display
                st.session_state.graded_image_path = graded_image_path
                st.session_state.python_compatible_data = python_compatible_data
                st.session_state.grading_complete = True

                # Complete
                status.update(
                    label="Grading complete!", state="complete", expanded=False
                )
                st.rerun()

            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                status.update(label="Grading failed!", state="error", expanded=True)
                # Give option to try again
                if st.button("Try Again"):
                    st.session_state.cropping_complete = False
                    st.rerun()

    # Step 4: Display Results
    elif st.session_state.grading_complete:
        # Display results using mobile-friendly vertical layout
        st.markdown('<div class="results-container">', unsafe_allow_html=True)

        # Original image container
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.subheader("Original Homework")
        original_img = Image.open(st.session_state.cropped_image)
        st.image(original_img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Graded image container
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.subheader("Graded Homework")
        processed_image = Image.open(st.session_state.graded_image_path)
        st.image(processed_image, use_container_width=True)

        # Add a download button for the processed image
        with open(st.session_state.graded_image_path, "rb") as file:
            btn = st.download_button(
                label="Download Graded Homework",
                data=file,
                file_name="graded_homework.png",
                mime="image/png",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Display image details
        with st.expander("Image Details"):
            st.write(f"Original Image Size: {original_img.size}")
            st.write(
                f"Original Image Format: {original_img.format if hasattr(original_img, 'format') else 'PNG'}"
            )
            st.write(f"Original Image Mode: {original_img.mode}")

        # Display the generated data
        with st.expander("Grading Data"):
            st.code(st.session_state.python_compatible_data, language="python")

            # Add a download button for the data
            st.download_button(
                label="Download Data as Python File",
                data=f"data = {st.session_state.python_compatible_data}",
                file_name="homework_grade_data.py",
                mime="text/plain",
            )

        # Add a button to grade another image
        if st.button("Grade Another Image", use_container_width=True):
            reset_app()


def about_page():
    # About page content
    st.title("About the Homework Grader")

    st.header("Overview")
    st.write("This app automatically grades homework images using AI technology.")
    st.write(
        "Simply upload a picture of homework and let the app do the grading for you!"
    )
    # Step 1
    st.header("How It Works")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="vertical-center">', unsafe_allow_html=True)
        st.header("1. Upload")
        st.subheader("Take a photo of homework or upload an existing image")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.video("videos/upload.mp4", autoplay=True, loop=True)

    # Step 2
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="vertical-center">', unsafe_allow_html=True)
        st.header("2. Crop")
        st.subheader("Focus on just the homework sheet by cropping the image")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.video("videos/crop.mp4", autoplay=True, loop=True)

    # Step 3
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="vertical-center">', unsafe_allow_html=True)
        st.header("3. Grid Overlay")
        st.subheader("The app adds a coordinate grid to help analyze answers")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.image("images/grid.jpg", use_container_width=True)

    # Step 4
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="vertical-center">', unsafe_allow_html=True)
        st.header("4. AI Processing")
        st.subheader("The image is analyzed to identify answers using Gemini AI")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.image("images/grade_data.jpg", use_container_width=True)

    # Step 5
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="vertical-center">', unsafe_allow_html=True)
        st.header("5. Grading")
        st.subheader(
            "Correct and incorrect answers are automatically marked and a final score is written."
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.video("videos/grading.mp4", autoplay=True, loop=True)

    st.header("Technology")
    st.write("This app uses Google's Gemini AI to analyze and grade homework images.")
    st.write(
        "The grading process typically takes 10-15 seconds depending on the complexity of the homework."
    )

    st.header("Privacy")
    st.write(
        "Images are processed temporarily and not stored permanently after grading."
    )
    st.write(
        "All temporary files are deleted when you reset the app or close the browser."
    )


# Create a session state for tracking temporary files
if "temp_files" not in st.session_state:
    st.session_state.temp_files = []

# Initialize other session state variables
if "cropped_image" not in st.session_state:
    st.session_state.cropped_image = None
if "upload_complete" not in st.session_state:
    st.session_state.upload_complete = False
if "cropping_complete" not in st.session_state:
    st.session_state.cropping_complete = False
if "grading_complete" not in st.session_state:
    st.session_state.grading_complete = False
if "original_image_path" not in st.session_state:
    st.session_state.original_image_path = None
if "graded_image_path" not in st.session_state:
    st.session_state.graded_image_path = None
if "python_compatible_data" not in st.session_state:
    st.session_state.python_compatible_data = None

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


def clean_temp_files():
    """
    Clean up all temporary files stored in the session state
    """
    for file_path in st.session_state.temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.warning(f"Could not delete temp file {file_path}: {e}")

    # Clear the list after attempting to remove all files
    st.session_state.temp_files = []


def process_image(input_image_path):
    # Step 1: Overlay grid on the image
    grid_output_path = os.path.join(
        tempfile.gettempdir(),
        f"output_image_with_grid_{os.path.basename(input_image_path)}",
    )
    overlay_grid_on_image(
        input_image_path,
        grid_spacing=50,
        grid_opacity=50,
        label_inset=10,
        label_font_size=14,
        output_path=grid_output_path,
    )

    # Add grid path to temp files for cleanup
    st.session_state.temp_files.append(grid_output_path)

    counter_data = read_counter()
    print(counter_data)
    if not counter_data["can_make_request"]:
        # Ratge Limit Hit
        if counter_data["daily_remaining"] <= 0:
            raise Exception(
                "Global Daily rate limit reached. Please contact developer at jorgezavala.um@gmail.com if you would like to try this app."
            )
        else:
            raise Exception(
                "Global Monthly rate limit reached. Please contact developer at jorgezavala.um@gmail.com if you would like to try this app."
            )

    # Step 2: Generate grading data
    input_prompt = "grade this. include unanswered problems. **The 'correctness' property you return should be true if the student answer is correct for that question and false if incorrect**. *Notice that there is a graph overlay. Use that to help you approximate coordinates of answers*"
    python_compatible_data = generate(
        image_path=grid_output_path,
        prompt_text=input_prompt,
        api_key=GEMINI_API_KEY,
    )

    # Update counter by 1
    update_counter()

    # Write the data to a temporary file
    data_file_path = os.path.join(
        tempfile.gettempdir(),
        f"python_compatible_data_{os.path.basename(input_image_path)}.py",
    )
    with open(data_file_path, "w") as f:
        f.write("data = " + python_compatible_data)

    # Add data path to temp files for cleanup
    st.session_state.temp_files.append(data_file_path)

    # Import the data from the temporary file
    import sys

    sys.path.append(tempfile.gettempdir())
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "python_compatible_data", data_file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Step 3: Apply grading to the image
    output_image_path = os.path.join(
        tempfile.gettempdir(), f"graded_homework_{os.path.basename(input_image_path)}"
    )
    grade(input_image_path, data=module.data, output_path=output_image_path)

    # Add output path to temp files for cleanup
    st.session_state.temp_files.append(output_image_path)

    return output_image_path, python_compatible_data


def reset_app():
    """Reset the app to initial state"""
    clean_temp_files()
    st.session_state.cropped_image = None
    st.session_state.upload_complete = False
    st.session_state.cropping_complete = False
    st.session_state.grading_complete = False
    st.session_state.original_image_path = None
    st.session_state.graded_image_path = None
    st.session_state.python_compatible_data = None
    # Force a refresh
    st.rerun()


# Main app with navigation
def main():

    # Setup sidebar
    with st.sidebar:

        # Navigation using st.navigation
        page = st.navigation(
            {
                "Navigate": [
                    st.Page(about_page, title="About", icon="ℹ️"),
                    st.Page(grader_page, title="Try Out Grader Tool!", icon="📝"),
                ]
            }
        )

        # Reset button at the bottom of sidebar
        if st.button(
            "🔄 Reset App",
            use_container_width=True,
            help="Clears all temporary files and resets the app",
        ):
            reset_app()
            st.success("All temporary files have been cleared and app has been reset!")

        # Debug info in sidebar (always visible)
        with st.expander("Debug: Temporary Files"):
            st.write(f"Number of temp files: {len(st.session_state.temp_files)}")
            for file in st.session_state.temp_files:
                st.write(f"- {file} (Exists: {os.path.exists(file)})")

    # Run the selected page
    page.run()


# Register cleanup function to run on exit
atexit.register(clean_temp_files)

if __name__ == "__main__":
    main()
