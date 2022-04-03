import zlib
import struct

from PIL import Image, ImageFile


# возвращает: (width, height, type), пример: (156, 156, PNG) или JPEG
# код на основе джанговского ImageFile.get_image_dimensions
# вернёт экзепшен если чо не так
def get_image_parameters(file):

    p = ImageFile.Parser()

    file_pos = file.tell()
    file.seek(0)

    try:
        # Most of the time Pillow only needs a small chunk to parse the image
        # and get the dimensions, but with some TIFF files Pillow needs to
        # parse the whole file.
        chunk_size = 1024
        while 1:
            data = file.read(chunk_size)
            if not data:
                break
            try:
                p.feed(data)
            except zlib.error as e:
                # ignore zlib complaining on truncated stream, just feed more
                # data to parser (ticket #19457).
                if e.args[0].startswith("Error -5"):
                    pass
                else:
                    raise
            except struct.error:
                # Ignore PIL failing on a too short buffer when reads return
                # less bytes than expected. Skip and feed more data to the
                # parser (ticket #24544).
                pass
            except RuntimeError:
                # e.g. "RuntimeError: could not create decoder object" for
                # WebP files. A different chunk_size may work.
                pass
            if p.image:
                return p.image.size[0], p.image.size[1], p.image.format
            chunk_size *= 2
        raise Exception("unknown format?") from None
    finally:
        file.seek(file_pos)
