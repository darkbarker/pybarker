import os
import tempfile
import hashlib


# создаёт временный файл и возвращает путь с указанным содержимым, делается однократно, т.е. файл остаётся в темпе
def get_file_path_from_data(tmpdir, data):
    hashdata = hashlib.md5(data.encode("utf-8")).hexdigest()
    file_path = os.path.join(tempfile.gettempdir(), tmpdir, "fpfd_%s" % hashdata)
    if not os.path.isfile(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(data)
    return file_path
