import pyarrow.parquet as pq
import xlsxwriter

EXCEL_MAX_ROWS = 1_048_576

class ParquetService:

    @staticmethod
    def parquet_to_excel(parquet_path: str, excel_path: str, batch_size: int = 10000):
        
        parquet = pq.ParquetFile(parquet_path)

        workbook = xlsxwriter.Workbook(
            excel_path,
            {
                "constant_memory": True
            }
        )

        sheet_number = 1
        worksheet = None
        current_row = 0
        total_rows = 0

        headers = parquet.schema.names


        def create_sheet():
            nonlocal worksheet
            nonlocal current_row
            nonlocal sheet_number

            worksheet = workbook.add_worksheet(
                f"Reporte_{sheet_number}"
            )

            for col, name in enumerate(headers):
                worksheet.write(0, col, name)

            current_row = 1


        create_sheet()


        for batch in parquet.iter_batches(
            batch_size=batch_size
        ):

            data = batch.to_pydict()

            rows = zip(*data.values())


            for values in rows:

                # llegó al límite de Excel
                if current_row == EXCEL_MAX_ROWS:

                    sheet_number += 1

                    create_sheet()


                worksheet.write_row(
                    current_row,
                    0,
                    values
                )

                current_row += 1
                total_rows += 1


        workbook.close()


        return {
            "rows": total_rows,
            "sheets": sheet_number,
            "path": excel_path
        }