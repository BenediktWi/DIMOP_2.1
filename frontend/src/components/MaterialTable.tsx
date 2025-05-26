import React from 'react'
import { useReactTable, createColumnHelper, flexRender } from '@tanstack/react-table'

interface Material {
  id: number
  name: string
  weight: number
}

interface Props {
  materials: Material[]
  onDelete: (id: number) => void
}

const columnHelper = createColumnHelper<Material>()

export default function MaterialTable({ materials, onDelete }: Props) {
  const columns = [
    columnHelper.accessor('name', { header: 'Material' }),
    columnHelper.accessor('weight', { header: 'Weight' }),
    columnHelper.display({
      id: 'delete',
      cell: info => (
        <button onClick={() => onDelete(info.row.original.id)}>🗑️</button>
      ),
    }),
  ]

  const table = useReactTable({ data: materials, columns })

  return (
    <table className="min-w-full text-sm">
      <thead>
        {table.getHeaderGroups().map(hg => (
          <tr key={hg.id}>
            {hg.headers.map(header => (
              <th key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
