from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color


def text_to_image(text: str):

    png_bytes = bytes()
    text = bytes(text, "utf-8").decode("unicode_escape")

    with Drawing() as draw:
        draw.font =  "./font.ttf"
        draw.font_size = 18
        draw.fill_color = Color("white")

        # Create a temporary image to measure the text
        with Image(width=1, height=1) as temp_img:
            metrics = draw.get_font_metrics(temp_img, text, multiline=True)
            text_width = int(metrics.text_width)
            text_height = int(metrics.text_height)

        padding = 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2

        with Image(width=img_width, height=img_height, background=Color('black')) as img:

            draw.text(padding, int(img_height / 2 - text_height / 2 + metrics.ascender), text)

            draw(img)
            img.trim()

            #  img.format = 'png'
            png_bytes = img.make_blob(format='png')

    return png_bytes


