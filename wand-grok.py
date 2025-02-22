from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

text = "Hello, World!"

with Drawing() as draw:
    draw.font =  "./font.ttf"
    draw.font_size = 18

    # Create a temporary image to measure the text
    with Image(width=1, height=1) as temp_img:
        metrics = draw.get_font_metrics(temp_img, text, multiline=True)
        text_width = int(metrics.text_width)
        text_height = int(metrics.text_height)

    padding = 10
    img_width = text_width + padding * 2
    img_height = text_height + padding * 2

    # Create the final image with the calculated size
    with Image(width=img_width, height=img_height, background=Color('white')) as img:
        # Position the text (centered with padding)
        draw.text(padding, int(img_height / 2 - text_height / 2 + metrics.ascender), text)

        # Apply the drawing to the image
        draw(img)

        img.trim()

        # Save the image
        img.save(filename='text_image.png')

print(f"Image created with size {img_width}x{img_height}")
