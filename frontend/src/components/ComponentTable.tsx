import React from 'react'
import {
  useReactTable,
  createColumnHelper,
  flexRender,
  getCoreRowModel,
} from '@tanstack/react-table'
import { Component } from '../wsMessage'

interface Props {
  components: Component[]
}

const columnHelper = createColumnHelper<Component>()

export default function ComponentTable({ components }: Props) {
  const columns = [
    columnHelper.accessor('name', { header: 'Name' }),
    columnHelper.accessor('level', { header: 'Level' }),
    columnHelper.accessor('weight', { header: 'Weight' }),
    columnHelper.accessor('material_id', { header: 'Material' }),
  ]

  const table = useReactTable({
    data: components,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

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
