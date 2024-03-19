from modal import Image as Modal_Image, Stub, gpu
from datetime import datetime
import uuid

imaginairy_image = (
    Modal_Image.debian_slim(python_version="3.12.1")
    .apt_install(
        "libglib2.0-0", "libsm6", "libxrender1", "libxext6", "ffmpeg", "libgl1"
    )
    .pip_install("imaginairy")
    .pip_install("Pillow")
)

stub = Stub("imaginairy")

with imaginairy_image.imports():
    from imaginairy.api.generate import imagine
    from imaginairy.schema import ImaginePrompt
    from PIL import Image
    import PIL


@stub.function(gpu=gpu.A10G(), container_idle_timeout=240, image=imaginairy_image)
def gen_image(prompt):
    prompt = ImaginePrompt(
        prompt=prompt,
        seed=1,
        model_weights="sdxl",
        size="hd",
    )

    result = next(imagine(prompts=prompt))
    return result.img


@stub.function(image=imaginairy_image)
def save_image(img):
    unique_id = uuid.uuid4()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    unique_file_name = f"generated_{timestamp}_{unique_id}.png"

    img.save(unique_file_name)


@stub.local_entrypoint()
def main():
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    image_prompts = [
        "a dog",
        "a cat",
        "a giraffe",
        "a gorilla",
        "a horse",
        "a lizard",
        "a cougar",
        "a monkey",
        "a hamster",
    ]
    for prompt_response in gen_image.map(image_prompts):
        save_image.local(prompt_response)
    # save_image.local(gen_image.remote(prompt="a flower"))

    end_time = datetime.now()
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    duration = end_time - start_time
    print(f"Total duration: {duration}")

