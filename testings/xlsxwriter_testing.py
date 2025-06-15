#!/usr/bin/python3
import xlsxwriter


# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('demo.xlsx', {'use_future_functions': True})
worksheet = workbook.add_worksheet()

# Widen the first column to make the text clearer.
worksheet.set_column('A:A', 20)

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': True})

# Write some simple text.
worksheet.write('A1', 'Hello')

# Text with formatting.
worksheet.write('A2', 'World', bold)

# Write some numbers, with row/column notation.
worksheet.write(2, 0, 123)
worksheet.write(3, 0, 242)

# Insert an image.
worksheet.insert_image('B5', 'uptime_view_colored.png')

formatage = workbook.add_format({'bold': True, 'bg_color': 'yellow'})

# Données à ajouter en bloc dans une ligne
data = ['Nom', 'Âge', 'Ville', 'Pays']

# Ajoute la ligne 1 (index 0) en bloc avec formatage
worksheet.write_row('A1', data, formatage)
worksheet.write_row(6,7, data, formatage)
worksheet.write_formula('A8', '=SOMME(A3:A4)')



workbook.close()
