import { Skeleton, Table } from "@heroui/react";

function PreviewTable({ data, title = "Preview", message="Sin datos", loading = false }) {

  if (loading) {
    return (
      <div className="space-y-2">
        <div className="px-2 space-y-2">
          <Skeleton className="h-5 w-40 rounded-lg" />
          <Skeleton className="h-4 w-60 rounded-lg" />
        </div>

        <div className="border rounded-lg p-4 space-y-3">
          {/* Header */}
          <div className="grid grid-cols-5 gap-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-5 rounded-lg" />
            ))}
          </div>

          {/* Rows */}
          {[...Array(5)].map((_, row) => (
            <div key={row} className="grid grid-cols-5 gap-2">
              {[...Array(5)].map((_, col) => (
                <Skeleton key={col} className="h-4 rounded-lg" />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return <p>{message}</p>;
  }

  const columns = data.columns ?? [];
  const rows = data.rows ?? [];

return (
    <div className="space-y-2">

      <div className="px-2">
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm text-gray-500">
          {data.metadata?.table_name}
        </p>
      </div>

      <Table>

        <Table.ScrollContainer>
          <Table.Content className="min-w-max">

            <Table.Header>
              {columns.map((col) => (
                <Table.Column key={col.name} isRowHeader>
                  {col.name}
                </Table.Column>
              ))}
            </Table.Header>

            <Table.Body>
              {rows.map((row, i) => (
                <Table.Row key={i}>
                  {columns.map((col) => (
                    <Table.Cell key={col.name}>
                      {String(row[col.name])}
                    </Table.Cell>
                  ))}
                </Table.Row>
              ))}
            </Table.Body>

          </Table.Content>
        </Table.ScrollContainer>

      </Table>
    </div>
  );
}

export default PreviewTable;