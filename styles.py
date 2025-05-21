def load_css():
    return """
    <style>
        .main {
            padding: 1rem;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .upload-container {
            border: 2px dashed #4c8bff;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .results-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        .image-container {
            padding: 1rem;
            border-radius: 10px;
            background-color: #f8f9fa;
            margin-bottom: 1rem;
        }
        .input-options {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .input-option {
            padding: 1rem;
            border-radius: 10px;
            background-color: #f8f9fa;
            text-align: center;
        }
        .crop-container {
            margin: 0.5rem 0;
            padding: 0;
            max-height: 60vh;
            overflow: hidden;
        }
        /* Optimize cropperjs for mobile */
        .cropperjs-wrapper {
            width: 80% !important;
            height: 60vh !important;
            max-height: 500px !important;
        }
        .cropper-container {
            width: 60% !important;
            max-height: 60vh !important;
            touch-action: none;
        }
        .cropper-view-box,
        .cropper-face {
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
        .cropper-point {
            width: 20px !important;
            height: 20px !important;
            opacity: 0.8 !important;
        }
        /* Navigation styling */
        .stButton button {
            min-height: 44px !important;
            margin: 8px 0 !important;
            border-radius: 8px !important;
        }
        .cropper-canvas,
        .cropper-crop-box {
            max-height: 60vh !important;
        }
        .vertical-center {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        min-height: 150px; /* Adjust based on your video height */
    }
    </style>
    """
