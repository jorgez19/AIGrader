# Homework Grader

An AI-powered application that automatically grades homework from images using Google's Gemini API.

## Overview

This Streamlit application allows teachers and educators to quickly grade homework assignments by simply uploading a photo. The app uses AI to identify questions, analyze student answers, and mark them as correct or incorrect.

## Features

- **Simple Upload**: Take a photo of homework or upload an existing image
- **Interactive Cropping**: Focus on just the homework sheet with an easy-to-use cropping tool
- **Grid Overlay**: The app adds a coordinate grid to help with answer analysis
- **AI Processing**: Powered by Google's Gemini AI to identify and evaluate answers
- **Automatic Grading**: Correct and incorrect answers are automatically marked with a final score
- **Downloadable Results**: Save the graded homework as an image or download the raw data

## How It Works

### 1. Upload
Upload a photo of homework directly from your device or take a new picture.

### 2. Crop
Focus on just the homework sheet by cropping the image to improve analysis accuracy.

### 3. Grid Overlay
The app adds a coordinate grid to help the AI analyze answer positions.

### 4. AI Processing
The image is analyzed by Gemini AI to identify questions and student answers.

### 5. Grading
Answers are automatically marked as correct or incorrect with a final score calculated.

## Technology

This application uses:

- **Streamlit**: For the web interface
- **Google's Gemini AI**: For image analysis and grading
- **PIL/Pillow**: For image processing
- **streamlit-cropperjs**: For the interactive cropping feature

## Privacy

- Images are processed temporarily and not stored permanently after grading
- All temporary files are deleted when you reset the app or close the browser
- Your data remains private and secure throughout the grading process


## Requirements

- Python 3.8 or higher
- Streamlit 1.31.0 or higher
- Google Generative AI API access
- See requirements.txt for full list of dependencies


## Contact

For questions or support, please contact: jorgezavala.um@gmail.com