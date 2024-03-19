import os
import io
import time


from modal import Mount, asgi_app, Image as ModalImage, Volume
from pydantic import BaseModel

from generation_scaling.common import stub

from generation_scaling.generate_image import generate_img

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app_image = (
    ModalImage.debian_slim(python_version="3.11")
    .apt_install(
        "libglib2.0-0", "libsm6", "libxrender1", "libxext6", "ffmpeg", "libgl1"
    )
    .pip_install("imaginairy")
    .pip_install("Pillow")
)

vol = Volume.from_name("image-vol", create_if_missing=True)


class PromptRequest(BaseModel):
    prompt: str


@stub.function(
    mounts=[
        Mount.from_local_dir(
            os.path.join(BASE_DIR, "templates"), remote_path="/root/templates"
        ),
        Mount.from_local_dir(
            os.path.join(BASE_DIR, "static"), remote_path="/root/static"
        ),
    ],
    container_idle_timeout=300,
    timeout=600,
    image=app_image,
    volumes={"/images": vol},
)
@asgi_app()
def web():
    from fastapi import FastAPI, Form
    from fastapi.responses import Response
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.responses import JSONResponse
    from io import BytesIO
    from PIL import Image

    app = FastAPI()

    @app.get("/")
    async def read_root():
        return FileResponse(os.path.join(BASE_DIR, "templates", "index.html"))


    @app.post("/gen_img")
    async def gen_img(prompt_request: PromptRequest):
        start_time = time()

        image_result, image_path = generate_img.remote(prompt=prompt_request.prompt)

        image_result.save(image_path)
        vol.commit()

        end_time = time()
        generation_time = end_time - start_time

        return JSONResponse(
            content={"image_path": image_path, "generation_time": generation_time}
        )

    @app.post("/gen_5_img")
    async def gen_5_img(prompt_request: PromptRequest):
        start_time = time()


        five_prompts = ["a dog", "a cat", "a horse", "a cow", "a bird"]

        all_image_paths = []

        for image_result, result_path in generate_img.map(five_prompts):
            if result_path:
                image_result.save(result_path)
                all_image_paths.append(result_path)
                vol.commit()

            vol.commit()

        end_time = time()
        generation_time = end_time - start_time


        return JSONResponse(
            content={"image_paths": all_image_paths, "generation_time": generation_time}
        )

    return app
