import gradio as gr
from gradio_pdf import PDF
import base64
import requests
import json
import re
import fitz
import os


API_KEY = os.getenv("API_KEY")
IMAGE_MODEL = "opengvlab/internvl3-14b:free"


def extract_json_from_code_block(text):
    if not isinstance(text, str):
        return {"error": "Invalid input: text must be a string."}
    try:
        # Standard Markdown code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_match = re.search(r"^\s*(\{.*?\})\s*$", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                first_brace = text.find('{')
                last_brace = text.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_str = text[first_brace:last_brace + 1]
                else:
                    return {"error": "No JSON block or discernible JSON object found in response."}

        # Attempt to fix common issues like trailing commas before parsing
        json_str_fixed = re.sub(r',\s*([\}\]])', r'\1', json_str)

        return json.loads(json_str_fixed)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in model response: {str(e)}", "problematic_snippet (approx)": json_str_fixed,
                "raw_output": text}
    except Exception as e:
        return {"error": f"An unexpected error occurred during JSON extraction: {str(e)}", "raw_output": text}


def convert_pdf_to_image(pdf_path, page_number=0):
    try:
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            return None
        doc = fitz.open(pdf_path)
        if not doc.page_count > 0:
            doc.close()
            print(f"Warning: PDF '{os.path.basename(pdf_path)}' has no pages.")
            return None
        if page_number >= doc.page_count:
            page_number = doc.page_count - 1
            print(f"Warning: Requested page {page_number + 1} out of bounds. Using last page ({page_number + 1}).")

        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=200)

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        safe_base_name = re.sub(r'[^\w\-_]', '_', base_name)
        temp_image_path = f"temp_page_{safe_base_name}_{page_number}.png"

        pix.save(temp_image_path)
        doc.close()
        return temp_image_path
    except Exception as e:
        print(f"Error converting PDF '{os.path.basename(pdf_path)}' to image: {e}")
        return None


def process_document_with_vision_model(image_path):
    if image_path is None:
        return {"error": "No image provided for vision model processing (image_path is None)."}
    if not os.path.exists(image_path):
        return {"error": f"Image file does not exist at path: {image_path}"}

    try:
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        data_url = f"data:image/png;base64,{encoded_image}"

        prompt = f"""You are a highly capable AI assistant specialized in document analysis and data extraction.
        Your mission is to meticulously examine the provided image, identify the type of document, and extract all pertinent information into a structured JSON format.
        Your entire response must be a **single, valid JSON object**. Do not include any introductory or concluding text outside of this JSON.
        (Your detailed prompt structure here - ensure it's the same as your working version)
        """
        payload = {
            "model": IMAGE_MODEL,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt},
                                                      {"type": "image_url", "image_url": {"url": data_url}}]}],
            "max_tokens": 4096
        }
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload,
                                 timeout=120)  # Added timeout
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0] and "content" in \
                result["choices"][0]["message"]:
            model_raw_output = result["choices"][0]["message"]["content"]
            return extract_json_from_code_block(model_raw_output)
        else:
            print(f"Unexpected API response format: {json.dumps(result, indent=2)}")
            return {"error": "Unexpected API response format from vision model.", "raw_api_response": result}

    except requests.exceptions.Timeout:
        print("Network Error: Request to OpenRouter API timed out.")
        return {"error": "Network Error: Request to OpenRouter API timed out."}
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {str(e)}")
        return {"error": f"Network Error: {str(e)}"}
    except Exception as e:
        print(
            f"General Error in vision model processing for {os.path.basename(image_path if image_path else 'No Image Path')}: {str(e)}")
        return {"error": f"General Error in vision model processing: {str(e)}"}


# --- Custom CSS for a Modern Dark UI ---
inspired_dark_css = """
/* Overall App Container */
.gradio-container {
    font-family: 'Inter', sans-serif;
    background-color: var(--neutral-950, #0c0c0f); /* Very dark background */
    padding: 0; /* Remove default padding if using full-width sections */
}

/* Main Title Area */
#app-header {
    background-color: var(--neutral-900, #121218);
    padding: 20px 30px;
    border-bottom: 1px solid var(--neutral-800, #2a2a38);
    margin-bottom: 0px; /* Spacing after header */
}
#app-title {
    text-align: center;
    color: var(--primary-400, #A78BFA);
    margin-bottom: 2px;
    font-size: 28px !important;
    font-weight: 600;
}
#app-subtitle {
    text-align: center;
    color: var(--neutral-400, #888898);
    margin-top: 0px;
    font-size: 16px !important;
    font-weight: 400;
}

/* Main content row styling */
#main-content-row {
    padding: 20px 30px; /* Add padding around the main content columns */
    gap: 30px; /* Space between columns */
}

/* "Node" or "Block" Styling for Columns/Sections */
.input-block, .output-block-column {
    background-color: var(--neutral-900, #121218); /* Slightly lighter than page bg */
    border-radius: 12px;
    padding: 25px;
    border: 1px solid var(--neutral-800, #2a2a38);
    box-shadow: 0 4px 12px rgba(0,0,0, 0.2); /* Subtle shadow for depth */
    height: 100%; /* Make blocks in a row take same height if desired */
}
.input-block h4, .output-block-column h4 { /* Section Headers */
    color: var(--neutral-200, #e0e0e0);
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 18px;
    border-bottom: 1px solid var(--neutral-700, #3a3a48);
    padding-bottom: 10px;
}

/* File Input Area */
.file-input-box > div[data-testid="block-label"] { display: none; } /* Hide default label if custom header is used */
.file-input-box .upload-box, .file-input-box > .svelte- যাহ코 > .upload-box { /* Target Gradio's file input */
    border: 2px dashed var(--primary-600, #7C3AED);
    background-color: var(--neutral-800, #1a1a22);
    border-radius: 8px;
    padding: 30px;
    color: var(--neutral-300, #c0c0c0);
}
.file-input-box .upload-box:hover, .file-input-box > .svelte- যাহ코 > .upload-box:hover {
    background-color: var(--neutral-700, #22222a);
    border-color: var(--primary-500, #8B5CF6);
}
.input-block .input-guidance p { /* Styling for help text */
    font-size: 0.85em;
    color: var(--neutral-400, #888898);
    text-align: center;
    margin-top: 15px;
}


/* Output Tabs Styling */
.output-block-column .gr-tabs { margin-top: -10px; } /* Adjust if needed */
.output-block-column .gr-tabs .tab-nav button { /* Tab buttons */
    background-color: transparent !important;
    color: var(--neutral-400, #888898) !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
}
.output-block-column .gr-tabs .tab-nav button.selected { /* Selected tab button */
    color: var(--primary-400, #A78BFA) !important;
    border-bottom: 2px solid var(--primary-400, #A78BFA) !important;
    background-color: var(--neutral-800, #1a1a22) !important; /* Slight bg for selected tab */
}
.tab-item-content { /* Content area within each tab */
    background-color: var(--neutral-850, #16161c); /* Slightly different from block bg for depth */
    padding: 20px;
    border-radius: 0 0 8px 8px;
    min-height: 400px; /* Ensure tabs have some content height */
    border: 1px solid var(--neutral-750, #30303c);
    border-top: none;
}

/* Preview Output (PDF/Image) Styling within Tab */
.preview-output-container { /* Specific container for PDF/Image */
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%; /* Takes height from .tab-item-content */
}
.preview-output-container img, .preview-output-container iframe {
    max-width: 100%;
    max-height: 500px; /* Max height for preview */
    object-fit: contain;
    border-radius: 4px;
    background-color: var(--neutral-100, #f0f0f0); /* Light bg for image/pdf itself for visibility */
}

/* JSON Output Styling within Tab */
.json-output-container .gr-json, .json-output-container .gr-code {
    background-color: var(--neutral-900, #0e0e12) !important; /* Darker for code/json */
    border: 1px solid var(--neutral-700, #3a3a48) !important;
    color: var(--neutral-200, #e0e0e0) !important;
    padding: 15px !important;
    border-radius: 6px !important;
    height: 100% !important;
    font-size: 0.9em !important;
}
/* Attempt to make JSON content more readable */
.json-output-container .gr-json span { color: inherit !important; }
.json-output-container .gr-json .str { color: #90EE90 !important; } /* LightGreen strings */
.json-output-container .gr-json .num { color: #ADD8E6 !important; } /* LightBlue numbers */
.json-output-container .gr-json .bool { color: #FFB6C1 !important; } /* LightPink booleans */
.json-output-container .gr-json .null { color: #D3D3D3 !important; } /* LightGray nulls */
.json-output-container .gr-json .key { color: #FFD700 !important; } /* Gold keys */

footer{display:none !important}
"""


app_theme = gr.themes.Monochrome(
    primary_hue=gr.themes.Color(
        c50='#F5F3FF', c100='#EDE9FE', c200='#DDD6FE', c300='#C4B5FD', c400='#A78BFA',
        c500='#8B5CF6', c600='#7C3AED', c700='#6D28D9', c800='#5B21B6', c900='#4C1D95',
        c950='#3B0B7D'
    ),
    secondary_hue="purple",
    neutral_hue="slate",
    radius_size=gr.themes.sizes.radius_md,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Fira Code"), "monospace"]
).set()

app_theme = gr.themes.Monochrome(
    primary_hue=gr.themes.Color("#F5F3FF", "#EDE9FE", "#DDD6FE", "#C4B5FD", "#A78BFA", "#8B5CF6", "#7C3AED", "#6D28D9",
                                "#5B21B6", "#4C1D95", "#3B0B7D"),
    secondary_hue=gr.themes.Color("#F5F3FF", "#EDE9FE", "#DDD6FE", "#C4B5FD", "#A78BFA", "#8B5CF6", "#7C3AED",
                                  "#6D28D9", "#5B21B6", "#4C1D95", "#3B0B7D"),  # Align with primary
    neutral_hue=gr.themes.colors.slate,
    radius_size=gr.themes.sizes.radius_md,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Fira Code"), "monospace"],
)

with gr.Blocks(
        theme=app_theme,
        css=inspired_dark_css,
        title="Zimbabwean Document AI Extractor"
) as app:
    with gr.Column(elem_id="app-header", scale=0):
        gr.Markdown("<h1 id='app-title'>Zim Docs Optical Character Recognition (OCR)-JSON</h1>", elem_id="title_md")
        gr.Markdown("<h3 id='app-subtitle'>Effortlessly convert scanned documents and images into ready-to-use JSON data. </h3>",
                    elem_id="subtitle_md")

    with gr.Row(elem_id="main-content-row", equal_height=True):
        with gr.Column(scale=1, min_width=400, elem_classes=["input-block"]):
            gr.Markdown("<h4>📂 OCR → JSON</h4>")
            file_input = gr.File(
                label="Drag & Drop or Click to Upload (PDF, PNG, JPG)",
                file_types=[".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".gif"],
                type="filepath",
                elem_classes=["file-input-box"]
            )

            with gr.Group(elem_classes=["input-guidance"]):
                gr.Markdown(
                    """
                    <p>Supported: PDF, PNG, JPG, JPEG, BMP, GIF.<br>
                    For optimal results, ensure the document image is clear and well-lit.</p>
                    """
                )


        with gr.Column(scale=2, min_width=600, elem_classes=["output-block-column"]):
            gr.Markdown("<h4>Extraction Results</h4>")
            with gr.Tabs(elem_id="output_tabs"):
                with gr.TabItem("📄 Document Preview", elem_id="preview_tab", elem_classes=["tab-item-content"]):
                    with gr.Group(elem_classes=["preview-output-container"]):
                        pdf_output = PDF(visible=False, show_label=False, elem_classes=["preview-output-item"])
                        image_output = gr.Image(visible=False, show_label=False, show_share_button=False,
                                                show_download_button=True, elem_classes=["preview-output-item"])
                    no_preview_message = gr.Markdown("Upload a document to see a preview.", visible=True,
                                                     elem_id="no_preview_msg")

                with gr.TabItem("Extracted Data (JSON)", elem_id="json_tab", elem_classes=["tab-item-content"]):
                    with gr.Group(elem_classes=["json-output-container"]):
                        json_output = gr.JSON(visible=False, show_label=False, elem_classes=["json-output-item"])
                    no_json_message = gr.Markdown("Analysis results will appear here.", visible=True,
                                                  elem_id="no_json_msg")


    def update_outputs_and_previews(file_path_str):
        pdf_val, pdf_vis_update = None, gr.update(visible=False)
        img_val, img_vis_update = None, gr.update(visible=False)
        json_val, json_vis_update = {"status": "Awaiting document..."}, gr.update(visible=False)
        no_preview_msg_update = gr.update(visible=True, value="Upload a document to see a preview.")
        no_json_msg_update = gr.update(visible=True, value="Analysis results will appear here.")

        if file_path_str is None:
            json_val = {"status": "No document provided. Please upload a file."}
            return pdf_val, pdf_vis_update, img_val, img_vis_update, json_val, json_vis_update, no_preview_msg_update, no_json_msg_update


        temp_image_to_process = None
        pdf_display_path = None
        image_display_path = None
        delete_temp_file = False

        current_file_path = file_path_str

        if current_file_path.lower().endswith('.pdf'):
            pdf_display_path = current_file_path
            temp_image_to_process = convert_pdf_to_image(current_file_path)
            if temp_image_to_process is None:
                error_msg = {"error": f"Failed to convert PDF: {os.path.basename(current_file_path)}."}
                print(error_msg["error"])
                pdf_val, pdf_vis_update = pdf_display_path, gr.update(visible=True)
                img_val, img_vis_update = None, gr.update(visible=False)
                json_val, json_vis_update = error_msg, gr.update(visible=True)
                no_preview_msg_update = gr.update(visible=False)
                no_json_msg_update = gr.update(visible=False)
                return pdf_val, pdf_vis_update, img_val, img_vis_update, json_val, json_vis_update, no_preview_msg_update, no_json_msg_update
            delete_temp_file = True
            pdf_val, pdf_vis_update = pdf_display_path, gr.update(visible=True)
            no_preview_msg_update = gr.update(visible=False)

        elif current_file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_display_path = current_file_path
            temp_image_to_process = current_file_path
            img_val, img_vis_update = image_display_path, gr.update(visible=True)
            no_preview_msg_update = gr.update(visible=False)
        else:
            error_msg = {"error": "Unsupported file format. Please upload PDF, PNG, JPG, JPEG, BMP, or GIF."}
            print(error_msg["error"])
            json_val, json_vis_update = error_msg, gr.update(visible=True)
            no_json_msg_update = gr.update(visible=False)
            return pdf_val, pdf_vis_update, img_val, img_vis_update, json_val, json_vis_update, no_preview_msg_update, no_json_msg_update

        if temp_image_to_process is None:
            error_msg = {"error": "Internal error: No image available for processing after file check."}
            print(error_msg["error"])
            json_val, json_vis_update = error_msg, gr.update(visible=True)
            no_json_msg_update = gr.update(visible=False)
            return pdf_val, pdf_vis_update, img_val, img_vis_update, json_val, json_vis_update, no_preview_msg_update, no_json_msg_update

        extracted_json_result = process_document_with_vision_model(temp_image_to_process)
        json_val, json_vis_update = extracted_json_result, gr.update(visible=True)
        no_json_msg_update = gr.update(visible=False)

        if delete_temp_file and temp_image_to_process and os.path.exists(
                temp_image_to_process) and temp_image_to_process != current_file_path:
            try:
                os.remove(temp_image_to_process)
                print(f"Temporary image '{temp_image_to_process}' deleted.")
            except Exception as e:
                print(f"Error deleting temporary image '{temp_image_to_process}': {e}")


        if pdf_display_path:
            img_vis_update = gr.update(visible=False)
            img_val = None
        elif image_display_path:
            pdf_vis_update = gr.update(visible=False)
            pdf_val = None

        return pdf_val, pdf_vis_update, img_val, img_vis_update, json_val, json_vis_update, no_preview_msg_update, no_json_msg_update


    all_outputs = [
        pdf_output, pdf_output,
        image_output, image_output,
        json_output, json_output,
        no_preview_message,
        no_json_message
    ]

    file_input.change(
        update_outputs_and_previews,
        inputs=[file_input],
        outputs=all_outputs
    )

if __name__ == "__main__":
    app.launch(show_error=True, show_api=False, debug=True)