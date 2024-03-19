from modal import Image as Modal_Image, gpu

from generation_scaling.common import stub

imaginairy_image = (
    Modal_Image.debian_slim(python_version="3.12.1")
    .apt_install(
        "libglib2.0-0", "libsm6", "libxrender1", "libxext6", "ffmpeg", "libgl1"
    )
    .pip_install("imaginairy")
    .pip_install("Pillow")
)


with imaginairy_image.imports():
    from imaginairy.api.generate import imagine
    from imaginairy.schema import ImaginePrompt

    import os
    from datetime import datetime
    import random
    import string


@stub.function(image=imaginairy_image, gpu=gpu.A10G(), container_idle_timeout=500)
async def generate_img(prompt: str = "a sunset"):
    prompt = ImaginePrompt(
        prompt=prompt,
        model_weights="sdxl",
        size="hd",
    )

    result = next(imagine(prompts=prompt))

    unique_filename = generate_unique_filename(extension="jpeg")

    directory_path = "/images"
    full_path = os.path.join(directory_path, unique_filename)

    return result.img, full_path


def generate_unique_filename(extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand_str = "".join(random.choices(string.ascii_letters + string.digits, k=5))

    return f"{timestamp}_{rand_str}.{extension}"
