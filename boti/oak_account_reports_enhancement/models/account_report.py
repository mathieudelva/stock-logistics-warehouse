import io

from odoo import models
from odoo.tools.misc import xlsxwriter


class AccountReport(models.AbstractModel):
    _inherit = "account.report"
    _description = "Account Report"

    def get_add_lines(
        self,
        sheet,
        y_offset,
        date_default_col1_style,
        date_default_style,
        default_col1_style,
        default_style,
        level_0_style,
        level_1_style,
        level_2_col1_style,
        level_2_col1_total_style,
        level_2_style,
        level_3_col1_style,
        level_3_col1_total_style,
        level_3_style,
        lines,
    ):
        for y in range(0, len(lines)):
            level = lines[y].get("level")
            if lines[y].get("caret_options"):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = (
                    "total" in lines[y].get("class", "").split(" ")
                    and level_2_col1_total_style
                    or level_2_col1_style
                )
            elif level == 3:
                style = level_3_style
                col1_style = (
                    "total" in lines[y].get("class", "").split(" ")
                    and level_3_col1_total_style
                    or level_3_col1_style
                )
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == "date":
                sheet.write_datetime(
                    y + y_offset, 0, cell_value, date_default_col1_style
                )
            else:
                if (
                    len(cell_value.split(" ")) > 1
                    and cell_value.split(" ")[0].isnumeric()
                ):
                    code = "".join([i for i in cell_value.split(" ")[0] if i.isdigit()])
                    sheet.write(y + y_offset, 0, code, col1_style)
                    account = " ".join([i for i in cell_value.split(" ")[1:]])
                    sheet.write(y + y_offset, 1, account, col1_style)
                else:
                    sheet.write(y + y_offset, 0, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]["columns"]) + 1):
                cell_type, cell_value = self._get_cell_type_value(
                    lines[y]["columns"][x - 1]
                )
                if cell_type == "date":
                    sheet.write_datetime(
                        y + y_offset,
                        x + lines[y].get("colspan", 1),
                        cell_value,
                        date_default_style,
                    )
                else:
                    sheet.write(
                        y + y_offset, x + lines[y].get("colspan", 1), cell_value, style
                    )

    def export_to_xlsx(self, options, response=None):
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)

        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(
            output,
            {
                "in_memory": True,
                "strings_to_formulas": False,
            },
        )
        sheet = workbook.add_worksheet(self.name[:31])

        date_default_col1_style = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "font_color": "#666666",
                "indent": 2,
                "num_format": "yyyy-mm-dd",
            }
        )
        date_default_style = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "font_color": "#666666",
                "num_format": "yyyy-mm-dd",
            }
        )
        default_col1_style = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "font_color": "#666666",
                "indent": 2,
            }
        )
        default_style = workbook.add_format(
            {"font_name": "Arial", "font_size": 12, "font_color": "#666666"}
        )
        title_style = workbook.add_format(
            {"font_name": "Arial", "bold": True, "bottom": 2}
        )
        level_0_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 13,
                "bottom": 6,
                "font_color": "#666666",
            }
        )
        level_1_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 13,
                "bottom": 1,
                "font_color": "#666666",
            }
        )
        level_2_col1_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 12,
                "font_color": "#666666",
                "indent": 1,
            }
        )
        level_2_col1_total_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 12,
                "font_color": "#666666",
            }
        )
        level_2_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 12,
                "font_color": "#666666",
            }
        )
        level_3_col1_style = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "font_color": "#666666",
                "indent": 2,
            }
        )
        level_3_col1_total_style = workbook.add_format(
            {
                "font_name": "Arial",
                "bold": True,
                "font_size": 12,
                "font_color": "#666666",
                "indent": 1,
            }
        )
        level_3_style = workbook.add_format(
            {"font_name": "Arial", "font_size": 12, "font_color": "#666666"}
        )

        # Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        x_offset = 2  # 1 and not 0 to leave space for the line name
        lines = self.with_context(
            no_format=True, print_mode=True, prefetch_fields=False
        )._get_lines(options)

        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        column_headers_render_data = self._get_column_headers_render_data(options)
        for header_level_index, header_level in enumerate(options["column_headers"]):
            for header_to_render in (
                header_level
                * column_headers_render_data["level_repetitions"][header_level_index]
            ):
                colspan = header_to_render.get(
                    "colspan",
                    column_headers_render_data["level_colspan"][header_level_index],
                )
                write_with_colspan(
                    sheet,
                    x_offset,
                    y_offset,
                    header_to_render.get("name", ""),
                    colspan,
                    title_style,
                )
                x_offset += colspan
            y_offset += 1
            x_offset = 1

        for subheader in column_headers_render_data["custom_subheaders"]:
            colspan = subheader.get("colspan", 1)
            write_with_colspan(
                sheet,
                x_offset,
                y_offset,
                subheader.get("name", ""),
                colspan,
                title_style,
            )
            x_offset += colspan
        y_offset += 1
        x_offset = 1

        for column in options["columns"]:
            colspan = column.get("colspan", 1)
            x_offset += 1
            write_with_colspan(
                sheet, x_offset, y_offset, column.get("name", ""), colspan, title_style
            )
            x_offset += colspan
        y_offset += 1

        if options.get("order_column"):
            lines = self._sort_lines(lines, options)

        # Add lines.
        self.get_add_lines(
            sheet,
            y_offset,
            date_default_col1_style,
            date_default_style,
            default_col1_style,
            default_style,
            level_0_style,
            level_1_style,
            level_2_col1_style,
            level_2_col1_total_style,
            level_2_style,
            level_3_col1_style,
            level_3_col1_total_style,
            level_3_style,
            lines,
        )

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return {
            "file_name": self.get_default_report_filename("xlsx"),
            "file_content": generated_file,
            "file_type": "xlsx",
        }
