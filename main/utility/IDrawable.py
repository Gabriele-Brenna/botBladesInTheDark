import io

from PIL import Image


def image_to_bytes(image: Image) -> bytes:
    """
    Utility method to convert an Image into an array of bytes.

    :param image: the Image to convert.
    :return: the bytes of the image.
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image.format)
    image_bytes = image_bytes.getvalue()
    return image_bytes


class IDrawable:
    """
    This class models the interface of all the objects that can be drawn.
    """

    def draw_image(self, **kwargs) -> bytes:
        """
        Draws the object on which this method is called.

        :return: the bytes of the object's image.
        """
        pass
