from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from PIL import Image
import io

router = APIRouter()


@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    # check file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    try:
        # resize to 400x400 pixels
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        resized_image = image.resize((400, 400), Image.Resampling.LANCZOS)

        # convert to webp format
        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, format="WEBP")
        output_buffer.seek(0)

        # get final results
        webp_image_bytes = output_buffer.getvalue()
        image_size = len(webp_image_bytes)

        # return image with size
        return Response(
            content=webp_image_bytes,
            media_type="image/webp",
            headers={
                "X-Image-Size-Bytes": str(image_size),
                "Content-Disposition": "inline; filename=processed.webp"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to process image.")
