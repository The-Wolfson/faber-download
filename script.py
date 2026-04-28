import os.path

import requests
import re
import io
from PIL import Image, ImageFile
import argparse
import logging

def download_image(url: str, page: int) -> ImageFile.ImageFile | None:
    url = re.sub(r"(?<=pagenumber=)\d*", str(page), url, count=1)
    logging.debug(f"Downloading page {page} from {url}")

    request = requests.get(url, stream=True)
    if request.status_code == 200:
        logging.debug(f"Page {page} downloaded successfully")
        image = Image.open(io.BytesIO(request.content))
        return image
    else:
        logging.debug(f"Page {page} returned status {request.status_code}, stopping")
        return None

def get_id(url: str) -> str:
    match = re.search(r"(?<=d)\d*", url)
    if match:
        return match.group(0)
    else:
        raise Exception("No ID found in the URL")

def get_name(url: str) -> str | None:
    matches = re.findall(r"\w+(?=-)", url)
    if len(matches) > 0:
        return " ".join(matches).title()
    else:
        return None

def get_preview_image_url(eid: str) -> str:
    base_url = f"https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=preview&eid={eid}"
    logging.debug(f"Resolving preview URL for eid={eid}")
    request = requests.head(base_url, allow_redirects=True)
    logging.debug(f"Resolved to {request.url}")
    return request.url

def get_perusal_pdf_url(eid: str) -> str:
    base_url = f"https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=perusal&page=0&eid={eid}"
    logging.debug(f"Resolving perusal URL for eid={eid}")
    request = requests.head(base_url, allow_redirects=True)
    logging.debug(f"Resolved to {request.url}")
    return request.url

def save_pdf_from_url(url: str, output: str):
    logging.debug(f"Fetching PDF from {url}")
    response = requests.get(url)
    with open(output, "wb") as file:
        file.write(response.content)
    logging.info(f"Saved to {output}")

def save_pdf_from_images(images: list[ImageFile.ImageFile], output: str):
    images[0].save(
        output, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )
    logging.info(f"Saved to {output}")

def run_preview(id: str, output: str):
    logging.info(f"Downloading preview for {id}")
    image_url = get_preview_image_url(id)

    images: list[ImageFile.ImageFile] = []
    while True:
        page_number = len(images) + 1
        result = download_image(image_url, page_number)
        if result is None:
            break
        images.append(result)

    logging.info(f"Downloaded {len(images)} page(s)")
    save_pdf_from_images(images, output=output)

def run_perusal(id: str, output: str):
    logging.info(f"Downloading perusal for {id}")
    pdf_url = get_perusal_pdf_url(id)
    save_pdf_from_url(pdf_url, output=output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download scores from Faber Music")
    parser.add_argument("url", help="The URL of the Faber Music product page", type=str)
    parser.add_argument("-o", "--output", type=str, default="./")
    parser.add_argument("--preview", action="store_true", help="Download preview PDF")
    parser.add_argument("--perusal", action="store_true", help="Download perusal PDF")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    preview: bool = args.preview
    perusal: bool = args.perusal
    if not preview and not perusal:
        preview = perusal = True

    score_id: str = get_id(args.url)
    name: str = get_name(args.url) or score_id
    logging.info(f"Score: {name} (id={score_id})")

    if perusal:
        output = os.path.join(args.output, f"{name}-perusal.pdf")
        run_perusal(score_id, output)
    if preview:
        output = os.path.join(args.output, f"{name}-preview.pdf")
        run_preview(score_id, output)