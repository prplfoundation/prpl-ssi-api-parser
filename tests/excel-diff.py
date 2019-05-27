# adapted from: https://github.com/mkudija/blog/blob/master/content/downloads/code/excel-diff/excel-diff-2.py

import pandas as pd
from pathlib import Path


def diff_files(path_ORIGINAL, path_GENERATED):

    # open files and load all sheets
    df_ORIGINAL = pd.read_excel(path_ORIGINAL, None)
    df_GENERATED = pd.read_excel(path_GENERATED, None)

    dropped_sheets = []
    diffed_sheets = []

    # Save output and format
    fname = '{} vs {}.xlsx'.format(path_ORIGINAL.stem, path_GENERATED.stem)
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    # get xlsxwriter objects
    workbook = writer.book

    # define formats
    date_fmt = workbook.add_format({'align': 'center', 'num_format': 'yyyy-mm-dd'})
    center_fmt = workbook.add_format({'align': 'center'})
    number_fmt = workbook.add_format({'align': 'center', 'num_format': '#,##0.00'})
    cur_fmt = workbook.add_format({'align': 'center', 'num_format': '$#,##0.00'})
    perc_fmt = workbook.add_format({'align': 'center', 'num_format': '0%'})
    grey_fmt = workbook.add_format({'font_color': '#E0E0E0'})
    highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color':'#B1B3B3'})
    new_fmt = workbook.add_format({'font_color': '#32CD32','bold':True})

    dashboard_df = pd.DataFrame({"Dropped Sheets": dropped_sheets})
    dashboard_df.to_excel(writer,
                          sheet_name="Dashboard",
                          index=False)

    # iterate over sheets from ORIGINAL to and create diff to GENERATED
    for sheet in df_ORIGINAL:
        # print(sheet)
        original_sheet = df_ORIGINAL[sheet]

        # check if the sheet exists in the generated file
        # if yes, generate diff sheet
        if sheet in df_GENERATED:
            generated_sheet = df_GENERATED[sheet]
            diff_sheet, newRows, droppedRows =\
                generate_sheet_diff(
                                    original_sheet,
                                    generated_sheet
                                    )

            diff_sheet_name = "DIFF {}".format(sheet)

            diff_sheet.to_excel(writer,
                                sheet_name=diff_sheet_name,
                                index=False)

            generated_sheet.to_excel(writer,
                                     sheet_name='{} - GENERATED'.format(sheet),
                                     index=False)

            original_sheet.to_excel(writer,
                                    sheet_name='{} - ORIGINAL'.format(sheet),
                                    index=False)
            
            worksheet = writer.sheets[diff_sheet_name]
            worksheet.hide_gridlines(2)
            worksheet.set_default_row(15)

            # set format over range
            # highlight changed cells
            worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                                    'criteria': 'containing',
                                                    'value':'→',
                                                    'format': highlight_fmt})

            # highlight new/changed rows
            for row in range(diff_sheet.shape[0]):
                if row+1 in newRows:
                    worksheet.set_row(row+1, 15, new_fmt)
                if row+1 in droppedRows:
                    worksheet.set_row(row+1, 15, grey_fmt)

        # if not, add it to dropped_sheets
        else:
            worksheet = writer.sheets["Dashboard"]
            dropped_sheets.append(sheet)
            worksheet.write(len(dropped_sheets), 0, sheet)

    writer.save()


def generate_sheet_diff(sheet_ORIGINAL, sheet_GENERATED):
    sheet_ORIGINAL = sheet_ORIGINAL.fillna(0)
    sheet_GENERATED = sheet_GENERATED.fillna(0)

    # index_col = sheet_GENERATED.column[0]

    # Perform Diff
    sheet_DIFF = sheet_GENERATED.copy()
    droppedRows = []
    newRows = []

    cols_ORIGINAL = sheet_ORIGINAL.columns
    cols_GENERATED = sheet_GENERATED.columns
    sharedCols = list(set(cols_ORIGINAL).intersection(cols_GENERATED))

    for row in sheet_DIFF.index:
        if (row in sheet_ORIGINAL.index) and (row in sheet_GENERATED.index):
            for col in sharedCols:
                value_ORIGINAL = sheet_ORIGINAL.loc[row, col]
                value_GENERATED = sheet_GENERATED.loc[row, col]
                if value_ORIGINAL == value_GENERATED:
                    sheet_DIFF.loc[row, col] = sheet_GENERATED.loc[row, col]
                else:
                    sheet_DIFF.loc[row, col] = ('{}→{}').format(
                                                                value_ORIGINAL,
                                                                value_GENERATED
                                                            )
        else:
            newRows.append(row)

    for row in sheet_ORIGINAL.index:
        if row not in sheet_GENERATED.index:
            droppedRows.append(row)
            sheet_DIFF = sheet_DIFF.append(sheet_ORIGINAL.loc[row, :])

    sheet_DIFF = sheet_DIFF.sort_index().fillna('')

    return (sheet_DIFF, newRows, droppedRows)


def main():
    path_ORIGINAL = Path('../specs/input/3.8.2.7RC.xlsx')
    path_GENERATED = Path('../specs/generated/Prpl-SSI-API_v3.8.2.7.xlsx')

    diff_files(path_ORIGINAL, path_GENERATED)

if __name__ == '__main__':
    main()
