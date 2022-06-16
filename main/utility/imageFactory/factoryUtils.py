from typing import Tuple

from PIL.ImageDraw import ImageDraw


def delimiter_rect(draw: ImageDraw, box_dim: Tuple[int, int]):
    # Useful rect around the box
    shape = ((0, 0), (box_dim[0] - 1, box_dim[1] - 1))
    draw.rectangle(shape, outline="black", width=1)


def average_char_size(text: str, font):
    """
    Return the average size of a char in the given text using the given font
    :param text: is the text to measure.
    :param font: is the font of the text.
    :return:
    """
    max_c = 0
    for c in text:
        max_c += font.getsize(c)[0]

    text_length = len(text)
    if text_length == 0:
        text_length = 1

    result = max_c / text_length
    if result == 0:
        result = 1
    return result
