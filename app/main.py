from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
import os

app = FastAPI()

# Ensure the static directory exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.isdir(static_path):
    os.makedirs(static_path)

app.mount("/static", StaticFiles(directory=static_path), name="static")

# Define the path to the templates directory
templates_path = os.path.join(os.path.dirname(__file__), "templates")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    try:
        with open(os.path.join(templates_path, "index.html")) as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resize", response_class=HTMLResponse)
async def resize_image(scale: float = Form(...), file: UploadFile = File(...)):
    try:
        # Read image
        image = Image.open(io.BytesIO(await file.read()))

        # Resize image
        width, height = image.size
        new_size = (int(width * scale), int(height * scale))
        resized_image = image.resize(new_size)

        # Save resized image to a buffer
        buf = io.BytesIO()
        resized_image.save(buf, format="PNG")
        buf.seek(0)

        # Generate color distribution graphs
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        # Original image color distribution
        original_array = np.array(image)
        original_colors, original_counts = np.unique(original_array.reshape(-1, 3), axis=0, return_counts=True)
        ax[0].bar(range(len(original_colors)), original_counts, color=original_colors / 255.0)
        ax[0].set_title("Original Image Color Distribution")

        # Resized image color distribution
        resized_array = np.array(resized_image)
        resized_colors, resized_counts = np.unique(resized_array.reshape(-1, 3), axis=0, return_counts=True)
        ax[1].bar(range(len(resized_colors)), resized_counts, color=resized_colors / 255.0)
        ax[1].set_title("Resized Image Color Distribution")

        # Save plots to a buffer
        plot_buf = io.BytesIO()
        plt.savefig(plot_buf, format="png")
        plot_buf.seek(0)

        with open(os.path.join(templates_path, "result.html")) as f:
            result_html = f.read()

        return HTMLResponse(content=result_html.format(image_data=buf.getvalue().hex(), plot_data=plot_buf.getvalue().hex()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import sys
    import logging

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting server...")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)
