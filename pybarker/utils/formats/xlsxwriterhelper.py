import io
import re
import datetime
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
    if token is None or token_type is bool or token_type in num_types or token_type is str \
            or token_type in (datetime.datetime, datetime.date, datetime.time, datetime.timedelta) \
            or isinstance(token, num_types) or isinstance(token, str) or isinstance(token, bool) \
            or isinstance(token, (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)):
        return token
    try:
        return str(token)
    except Exception as _:
        pass
    return token


# может нарисовать квадратную таблицу с некоторой сложности шапкой
# возвращает BytesIO открытый и сброшенный к началу
def make_excel(header_data, header_default_style=None, table_start_cell=None, table_data=None):
    """
    header_data - итерабл таких элементов:
    [
        ['A1:B2', '№'],
        ['R2', 'забраковано', (опции)],
    ]
    опции - набор свойств:
    * целое число: ширина

    header_default_style - набор свойств общих для ячеек, поддерживаются:
    * center
    * vcenter

    table_start_cell - ячейка с которой начинается рисование таблицы (вправо-вниз)

    table_data - итерабл строк, каждая из которых - тоже итерабл по ячейкам

    вариант вызова для многолистового:
    [
        ("Отчёт", (header_data1, header_default_style1, table_start_cell1, table_data1)),
        ("Итого", (header_data2, header_default_style2, table_start_cell2, table_data2)),
    ]
    """

    if isinstance(header_data, list) and header_default_style is None and table_start_cell is None and table_data is None:
        sheets = header_data
    elif header_data is not None and header_default_style is not None and table_start_cell is not None and table_data is not None:
        sheets = [(None, (header_data, header_default_style, table_start_cell, table_data))]
    else:
        raise ValueError("must be 4 params or list of tuples")

    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # он всё равно будет юзать временные файлы, если не нужно - сделать 'in_memory'
    workbook = xlsxwriter.Workbook(output, {"default_date_format": "dd.mm.yyyy"})
    for sheeet in sheets:
        sheet_name, sheet_params = sheeet
        header_data, header_default_style, table_start_cell, table_data = sheet_params

        worksheet = workbook.add_worksheet(name=sheet_name)

        header_def_style = set()
        header_def_format = None
        if header_default_style:
            header_def_style = set(header_default_style)
            h = {}
            if "center" in header_def_style:
                h["align"] = "center"
            if "vcenter" in header_def_style:
                h["valign"] = "vcenter"
            header_def_format = workbook.add_format(h)

        for celldata in header_data:
            try:
                cell, title, options = celldata
            except ValueError as _:
                cell, title = celldata
                options = []
            # prepare options
            width = None
            for option in options:
                if isinstance(option, int):
                    width = option
            # cell
            if ":" in cell:  # merged
                worksheet.merge_range(cell, title, cell_format=header_def_format)
            else:
                worksheet.write(cell, title, header_def_format)
            # width
            if width:
                # имя столбца, если несколько то первого, несколько букв тоже может быть
                firstwcell = re.findall("[a-zA-Z]+", cell)[0]  # 'AA1:AA2' -> ['AA', 'AA']
                worksheet.set_column("%s:%s" % (firstwcell, firstwcell), width)

        table_start_row, table_start_col = xl_cell_to_rowcol(table_start_cell)
        for table_row in table_data:
            # worksheet.write_row(table_start_row, table_start_col, table_row, cell_format=None)
            col = table_start_col
            for token in table_row:
                token = convert_val_to_simple(token)
                worksheet.write(table_start_row, col, token)
                col += 1
            table_start_row += 1

    # close workbook & rewind buffer
    workbook.close()
    output.seek(0)

    return output
