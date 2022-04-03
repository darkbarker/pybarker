import os
import io
import tempfile
import subprocess

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile


# конвертит существующую картинку правильную аплоаженную в JPG вписывая в указанный формат
# файл поддерживается:
# django.core.files.uploadedfile.InMemoryUploadedFile
# django.core.files.uploadedfile.TemporaryUploadedFile
# возвращает InMemoryUploadedFile для установки в атрибут модели
def resize_image_file_tojpg(file, maxdimension):
    fill_alpha_color = (255, 255, 255)
    jpeg_quality = 65

    im = Image.open(file)

    if im.mode in ("RGBA", "LA"):
        background = Image.new(im.mode[:-1], im.size, fill_alpha_color)
        background.paste(im, im.split()[-1])
        im = background
    else:
        if im.mode != "RGB":
            im = im.convert("RGB")

    output = io.BytesIO()
    im.thumbnail((maxdimension, maxdimension))
    im.save(output, format="JPEG", quality=jpeg_quality)
    output.seek(0)

    img_size = output.getbuffer().nbytes

    file_name, _ = os.path.splitext(file.name)
    new_file_name = "%s.crop.jpg" % file_name

    return InMemoryUploadedFile(output, "ImageField", new_file_name, "image/jpeg", img_size, None)


def _stderr_str(stderr):
    if not stderr:
        return "-"
    if isinstance(stderr, bytes):
        try:
            stderr = stderr.decode("utf-8")
        except Exception as _:
            pass
    if not isinstance(stderr, str):
        stderr = str(stderr)
    return "; ".join([s.strip() for s in stderr.split("\n") if s.strip()])


def resize_pdf_file_tojpg(file, dimension):
    try:
        with tempfile.NamedTemporaryFile() as ifile, tempfile.NamedTemporaryFile() as ofile:
            ifile.write(file.read())
            # ifile.flush()

            # file.pdf[0] - first page pdf, "-resize 220x205",
            # convert -append -resize 666 -density 300 -quality 70 ifile.name JPEG:ofile.name
            params = ["convert", "-append", "-resize", str(dimension), "-density", "300", "-quality", "70", ifile.name, "JPEG:%s" % ofile.name]
            subprocess.run(params, capture_output=True, check=True)

            output = io.BytesIO()
            output.write(ofile.read())
            output.seek(0)

            img_size = output.getbuffer().nbytes
            new_file_name = "%s.jpg" % file.name

            return InMemoryUploadedFile(output, "ImageField", new_file_name, "image/jpeg", img_size, None)
    except subprocess.CalledProcessError as e:
        raise Exception('call process error convert pdf: "%s", stderr: "%s"' % (str(e), _stderr_str(e.stderr))) from None
    except Exception as e:
        raise Exception('unknown error convert pdf: "%s"' % str(e)) from None
