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
* **Live Demo:** You can try out a live demo of this application at: [Demo](https://huggingface.co/spaces/NyashaK/DocOCR2JSON)