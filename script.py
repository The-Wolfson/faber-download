import requests
import re
import io
import sys
from PIL import Image, ImageFile
import argparse

def download_image(url: str, page: int) -> ImageFile.ImageFile | None:

    url = re.sub(r"(?<=pagenumber=)\d*", str(page), url, count=1)

    request = requests.get(url, stream=True)
    if request.status_code == 200:
        image = Image.open(io.BytesIO(request.content))
        return image
    else:
        return None

def get_id(url: str) -> str:
    match = re.search(r"(?<=d)\d*", url)
    if match:
        return match.group(0)
    else:
        raise Exception("No ID found in the URL")

# input https://www.fabermusic.com/shop/six-from-six-the-musical-d40696/sample or https://www.fabermusic.com/shop/six-from-six-the-musical-d40696
def get_name(url: str) -> str | None:
    matches = re.findall(r"\w+(?=-)", url)
    if len(matches) > 0:
        return " ".join(matches).title()
    else:
        return None

def get_preview_image_url(eid: str) -> str:
    base_url = f"https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=preview&eid={eid}"
    request = requests.head(base_url, allow_redirects=True)
    return request.url

def get_perusal_pdf_url(eid: str) -> str:
    base_url = f"https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=perusal&page=0&eid={eid}"
    request = requests.head(base_url, allow_redirects=True)
    return request.url

def save_pdf_from_url(url: str, output: str):
    response = requests.get(url)
    file = open(output, "wb")
    file.write(response.content)
    file.close()

def save_pdf_from_images(images: list[ImageFile.ImageFile], output: str):
    images[0].save(
        output, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )

def run_preview(id: str, output: str):
    image_url = get_preview_image_url(id)

    images: list[ImageFile.ImageFile] = []
    while True:
        page_number = len(images) + 1
        result = download_image(image_url, page_number)
        if result is None:
            break
        images.append(result)
    save_pdf_from_images(images, output=output)


def run_perusal(id: str, output: str):
    pdf_url = get_perusal_pdf_url(id)
    save_pdf_from_url(pdf_url, output=output)


# input either https://www.fabermusic.com/shop/d40696 or https://www.fabermusic.com/shop/six-from-six-the-musical-d40696
# or https://www.fabermusic.com/shop/d40696/sample or https://www.fabermusic.com/shop/six-from-six-the-musical-d40696/sample
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download scores from Faber Music")
    parser.add_argument("url", help="The URL of the Faber Music product page", type=str)
    parser.add_argument("-o", "--output", type=str, default="./")
    parser.add_argument("--preview", action="store_true", help="Download preview PDF")
    parser.add_argument("--perusal", action="store_true", help="Download perusal PDF")

    args = parser.parse_args()

    preview: bool = args.preview
    perusal: bool = args.perusal
    if not preview and not perusal:
        preview = perusal = True

    score_id: str = get_id(args.url)
    name: str = get_name(args.url) or score_id

    if perusal:
        output = args.output + f"{name}-perusal.pdf"
        run_perusal(score_id, output)
    if preview:
        output = args.output + f"{name}-preview.pdf"
        run_preview(score_id, output)