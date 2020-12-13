import io
import re

try:
    import xlsxwriter
    from xlsxwriter.utility import xl_cell_to_rowcol
except ImportError as exc:
    raise ImportError("couldn't import xlsxwriter") from exc

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# может нарисовать квадратную таблицу с некоторой сложности шапкой
# возвращает BytesIO открытый и сброшенный к началу
def make_excel(header_data, header_default_style, table_start_cell, table_data):
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
    """

    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # он всё равно будет юзать временные файлы, если не нужно - сделать 'in_memory'
    workbook = xlsxwriter.Workbook(output, {"default_date_format": "dd.mm.yyyy"})
    worksheet = workbook.add_worksheet()

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
            worksheet.write(table_start_row, col, token)
            col += 1
        table_start_row += 1

    # close workbook & rewind buffer
    workbook.close()
    output.seek(0)

    return output
