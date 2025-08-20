import datetime
import io
import re
from decimal import Decimal
from fractions import Fraction

try:
    import xlsxwriter
    from xlsxwriter.utility import xl_cell_to_rowcol
except ImportError as exc:
    raise ImportError("couldn't import xlsxwriter") from exc

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# список типов на основе анализа модуля worksheet<...>_write
def convert_val_to_simple(token):
    num_types = (float, int, Decimal, Fraction)
    token_type = type(token)
    if (
        token is None
        or token_type is bool
        or token_type in num_types
        or token_type is str
        or token_type in (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)
        or isinstance(token, num_types)
        or isinstance(token, str)
        or isinstance(token, bool)
        or isinstance(token, (datetime.datetime, datetime.date, datetime.time, datetime.timedelta))
    ):
        return token
    try:
        return str(token)
    except Exception as _:
        pass
    return token


# может нарисовать прямоугольную таблицу с некоторой сложности шапкой
# возвращает BytesIO открытый и сброшенный к началу
def make_excel(header_data, header_default_format=None, table_start_cell=None, table_data=None):
    """
    header_data - итерабл таких элементов:
    [
        ['A1:B2', '№'],
        ['R2', 'забраковано', {опции}],
    ]
    опции - набор свойств:
    * {
        "width": целое-число-ширина-столбца,
        "height": целое-число-высота-строки (достаточно установить для одной ячейки, применится ко всей строке)
        "freeze_row": True/False - закрепить столбец (достаточно установить для одной ячейки)
        "freeze_col": True/False - закрепить строку (достаточно установить для одной ячейки)
        "cell_format": {"align": "left", "bg_color": red, ...}
       }

    header_default_format - набор свойств общих для ячеек заголовка:
    * {"align": "center", "valign": "vcenter", ...}

    table_start_cell - ячейка с которой начинается рисование таблицы (вправо-вниз)

    table_data - итерабл строк, каждая из которых - тоже итерабл по ячейкам
    ячейки - кортеж ('data', cell_style), список ['data', cell_style] или просто строка 'data'

    вариант вызова для многолистового:
    [
        ("Отчёт", (header_data1, header_default_style1, table_start_cell1, table_data1)),
        ("Итого", (header_data2, header_default_style2, table_start_cell2, table_data2)),
    ]
    """

    if (
        isinstance(header_data, list)
        and header_default_format is None
        and table_start_cell is None
        and table_data is None
    ):
        sheets = header_data
    elif (
        header_data is not None
        and header_default_format is not None
        and table_start_cell is not None
        and table_data is not None
    ):
        sheets = [(None, (header_data, header_default_format, table_start_cell, table_data))]
    else:
        raise ValueError("must be 4 params or list of tuples")

    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # он всё равно будет юзать временные файлы, если не нужно - сделать 'in_memory'
    workbook = xlsxwriter.Workbook(output, {"default_date_format": "dd.mm.yyyy", "remove_timezone": True})
    for sheeet in sheets:
        sheet_name, sheet_params = sheeet
        header_data, header_default_format, table_start_cell, table_data = sheet_params

        worksheet = workbook.add_worksheet(name=sheet_name)
        header_def_format = workbook.add_format(header_default_format) if header_default_format else None

        # write header
        for celldata in header_data:
            try:
                cell, title, options = celldata
                if options is None:
                    options = {}
            except ValueError as _:
                cell, title = celldata
                options = {}
            # prepare options
            width = options.get("width", None)
            height = options.get("height", None)
            freeze_row = options.get("freeze_row", None)
            freeze_col = options.get("freeze_col", None)
            # "cell_format" prepare
            if "cell_format" in options:
                # если задан "cell_format", то мы в любом случае будем юзать свой format вместо header_def_format, но
                # если был задан общий - мы его используем для основы создания своего формата
                header_cell_format = header_default_format or {}
                header_cell_format.update(options["cell_format"])
                header_cell_format = workbook.add_format(header_cell_format)
            else:
                header_cell_format = None
            # cell
            if ":" in cell:  # if range ("merged")
                worksheet.merge_range(cell, title, cell_format=header_cell_format or header_def_format)
            else:
                worksheet.write(cell, title, header_cell_format or header_def_format)
            # width
            if width:
                # имя столбца, если несколько то первого только мы шириной управляем, несколько букв тоже может быть
                # (ширина ставится на "столбец" в виде "A:A")
                firstwcell = re.findall("[a-zA-Z]+", cell)[0]  # 'AA1:AA2' -> ['AA', 'AA']
                worksheet.set_column("%s:%s" % (firstwcell, firstwcell), width=width)

            _row, _col = xl_cell_to_rowcol(cell)
            if height:
                worksheet.set_row(_row, height)
            # freeze row/col+1, т.к. указывается ячейка для разделения (следующая), см.доку на worksheet.freeze_panes
            if freeze_row:
                worksheet.freeze_panes(_row + 1, 0)
            if freeze_col:
                worksheet.freeze_panes(0, _col + 1)

        # write data
        table_start_row, table_start_col = xl_cell_to_rowcol(table_start_cell)
        for table_row in table_data:
            col = table_start_col
            for token in table_row:
                if isinstance(token, (list, tuple)):
                    token, style = token
                else:
                    token = token
                    style = {}
                cell_format = add_format(workbook, style) if style else None
                token = convert_val_to_simple(token)
                worksheet.write(table_start_row, col, token, cell_format)
                col += 1
            table_start_row += 1

    # close workbook & rewind buffer
    workbook.close()
    output.seek(0)

    return output


def add_format(workbook, properties=None):
    """Переопределенный метод добавления формат.

    Добавляем в форматы книги, только если его там нет, чтобы не хранить сотни одинаковых форматов.
    """

    format_properties = workbook.default_format_properties.copy()
    if properties:
        format_properties.update(properties)
    xf_format = xlsxwriter.format.Format(format_properties, workbook.xf_format_indices, workbook.dxf_format_indices)
    if xf_format not in workbook.formats:
        workbook.formats.append(xf_format)

    return xf_format
