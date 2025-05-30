---
title: Zim Docs OCR-to-JSON Extractor
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 5.31.0
app_file: app.py
pinned: false
license: mit
---

# Zim Docs OCR-to-JSON Extractor

## Overview

Welcome to the **Zim Docs OCR-to-JSON Extractor**! This is a powerful and user-friendly web application built with Gradio, designed to help you upload scanned documents (PDFs) or images (PNG, JPG, etc.). It then uses a vision AI model to perform Optical Character Recognition (OCR) and extract structured information into a JSON format. This tool aims to streamline your process of digitizing and organizing data from various document types, such as **driver's licenses, passports, national ID cards, invoices, receipts, and more.**

## Requirements

To use this application, you'll need:

* Python 3.7+
* Gradio
* Gradio-PDF (`gradio_pdf`)
* Requests
* PyMuPDF (`fitz`)
* An API Key from [OpenRouter.ai](https://openrouter.ai/) (or any other service compatible with the OpenAI chat completions API format).
    * You should set this key as an environment variable named `API_KEY`. The Python script uses `os.getenv("API_KEY")` to retrieve this key. If you're using Hugging Face Spaces, you can set this as a "Secret".

## Running the Application

**On Hugging Face Spaces:**

This application is designed for deployment on Hugging Face Spaces.
1.  Ensure your `requirements.txt` file in your Hugging Face Space repository lists all necessary dependencies (e.g., `gradio`, `gradio_pdf`, `requests`, `PyMuPDF`).
2.  You should configure your `API_KEY` as a "Secret" in your Hugging Face Space settings. The application will then retrieve it using `os.getenv("API_KEY")`.
3.  Once deployed, you can access the application via the URL provided by your Hugging Face Space.
    * **Live Demo:** You can try out a live demo of this application at: [Demo](https://huggingface.co/spaces/NyashaK/DocOCR2JSON)

**For Local Development/Testing (Optional):**

If you wish to run the application on your local machine:
1.  Make sure you have all dependencies listed under "Requirements" installed in your local Python environment (e.g., by running `pip install gradio gradio_pdf requests PyMuPDF`).
2.  Set the `API_KEY` environment variable on your local system.
3.  You can then run the application using the command:
    ```bash
    python app.py
    ```
    Your Python file should be named `app.py` (or update this command if it's different). It will typically be available at `http://127.0.0.1:7860`.

## How to Use

1.  **Access the Application:** Open the URL of your Hugging Face Space where the application is deployed (see Live Demo link above), or your local URL if running it locally.
2.  **Upload Your Document:**
    * Drag and drop a supported file (PDF, PNG, JPG, etc.) into the designated upload area.
    * Alternatively, click on the upload area to open your file browser and select the document.
3.  **View Preview:**
    * Once you've uploaded a file, the "Document Preview" tab will attempt to display the image or the first page of your PDF.
4.  **Check Extracted Data:**
    * The application will automatically process your document.
    * Switch to the "Extracted Data (JSON)" tab to view the structured information extracted by the AI model.
    * If any errors occur during processing (e.g., unsupported file type, API issue), an error message will be displayed in the JSON output area.

## Troubleshooting

Here are some common issues you might encounter and how to resolve them:

* **API Key Issues:** Ensure your `API_KEY` is correctly set as a Secret on Hugging Face Spaces (or as an environment variable for local testing). Also, verify that your key is valid and has sufficient credits/access for the chosen model.
* **Dependency Errors:** If you're on Hugging Face, double-check your `requirements.txt` file. For local use, ensure all libraries are installed in your environment.
* **File Conversion Failures:** For PDFs, `PyMuPDF (fitz)` needs to be available. Corrupted PDF files might also cause issues with conversion.
* **Model Output/JSON Errors:**
    * If the model doesn't return valid JSON, the application will attempt to report an error.
    * The quality of the extracted JSON heavily depends on the clarity of your input document, the capabilities of the chosen vision model, and the effectiveness of the prompt used to guide the AI.
* **Network Errors:** You'll need a stable internet connection for the application to make external API calls. These can fail due to network issues or timeouts. If you're on Hugging Face, this might relate to the Space's network access or API endpoint reachability.

---

This README provides you with a concise guide to understanding, setting up, and using the Zim Docs OCR-to-JSON Extractor.