import requests
import re
import io
import sys
from PIL import Image, ImageFile

def download_image(url: str, page: int) -> ImageFile.ImageFile | None: #return error or image
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

def get_name(url: str) -> str:
    matches = re.findall(r"\w+(?=-)", url)
    return " ".join(matches).title()

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

if __name__ == '__main__':
    URL = sys.argv[1]
    PDF_PREVIEW_OUTPUT = f"{get_name(URL)}-preview.pdf"
    PDF_PERUSAL_OUTPUT = f"{get_name(URL)}-perusal.pdf"
    SCORE_ID = get_id(URL)
    IMAGE_URL = get_preview_image_url(SCORE_ID)
    PDF_URL = get_perusal_pdf_url(SCORE_ID)
    IMAGES: list[ImageFile.ImageFile] = []
    while True:
        PAGE_NUMBER = len(IMAGES) + 1
        RESULT = download_image(IMAGE_URL, PAGE_NUMBER)
        if RESULT is None:
            break
        IMAGES.append(RESULT)
    save_pdf_from_url(PDF_URL, output=PDF_PERUSAL_OUTPUT)
    save_pdf_from_images(IMAGES, output=PDF_PREVIEW_OUTPUT)

# https://www.fabermusic.com/shop/d40696 //product listing
# https://www.fabermusic.com/shop/d40696/sample // product sample page
# https://www.epartnershub.com/engravingservices/view.aspx?q=1D6C09323594E33ECBDBCA6F016A67B8CE3C5D7ED90BC38F30772354EFF47AD4 // sample iframe
# https://w56378sxd7.execute-api.eu-west-2.amazonaws.com/Prod/faber-preview?guid=4634c725-d838-4793-8ca3-b53cc9928c91&fileformat=png&previewtype=singlepage&pagenumber=1 //preview image of page
#
# https://www.fabermusic.com/shop/d45182 // product listing
# https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=preview&eid=45182 // redirects to preview image
#
# https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=perusal&page=0&eid=45182 // redirects to full perusal pdf
#
# https://w56378sxd7.execute-api.eu-west-2.amazonaws.com/Prod/faber-preview?guid=6b06f6b1-fd14-4263-98a6-65c59819040e&fileformat=png&previewtype=perusal&pagenumber=1 // watermarked png
#
# https://w56378sxd7.execute-api.eu-west-2.amazonaws.com/Prod/faber-preview?guid=bfaaff71-6e02-4467-bc6e-94fa138969d8&fileformat=png&previewtype=perusal // watermarked pdf
# https://w56378sxd7.execute-api.eu-west-2.amazonaws.com/Prod/faber-preview?guid=6b06f6b1-fd14-4263-98a6-65c59819040e&fileformat=png&previewtype=perusal&pagenumber=0 // watermarked pdf
#
# https://www.epartnershub.com/api/download.aspx?hash=028f38bdd5b65b7c99275b08a2c13e00&epartner=fabermusicstore&sale=3605678 // full d33663 pdf
# https://www.epartnershub.com/api/download.aspx?hash=9df81ee453e3ce3cbfcc3cc56f97f3ea&epartner=fabermusicstore&sale=3605679 // full d44195 pdf
#
# https://www.fabermusic.com/shop/d33663
# https://www.fabermusic.com/shop/d33663/sample
# https://www.epartnershub.com/engravingservices/view.aspx?q=A9AEDE6CCAAE54A5DFD5723B3A87E890EA90AC9447269D26AB642F016951B3C0
# https://www.epartnershub.com/EngravingServices/ViewHandler.ashx?op=perusal&page=0&eid=33663
# https://w56378sxd7.execute-api.eu-west-2.amazonaws.com/Prod/faber-preview?guid=8dcfc705-650e-4709-b0fb-e9d29ec9c384&fileformat=png&previewtype=perusal&pagenumber=0
# https://www.epartnershub.com/api/download.aspx?hash=028f38bdd5b65b7c99275b08a2c13e00&epartner=fabermusicstore&sale=3605678
