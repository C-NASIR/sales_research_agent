"use client";

import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import Link from "next/link";
import { useState } from "react";

import { formatStatus, truncateText } from "@/lib/format";
import type { AccountResult } from "@/lib/types";

import { QualityStatusBadge } from "./QualityStatusBadge";
import { ScorePill } from "./ScorePill";

type AccountResultsTableProps = {
  campaignId: string;
  accounts: AccountResult[];
};

const columnHelper = createColumnHelper<AccountResult>();

function compareNullableNumbers(
  left: number | null | undefined,
  right: number | null | undefined,
) {
  if (left === null || left === undefined) {
    return right === null || right === undefined ? 0 : 1;
  }

  if (right === null || right === undefined) {
    return -1;
  }

  return left - right;
}

function buildColumns(campaignId: string) {
  return [
    columnHelper.accessor("company_name", {
      header: "Company",
      cell: ({ row }) => (
        <div className="stack-sm">
          <strong>{row.original.company_name}</strong>
        </div>
      ),
    }),
    columnHelper.accessor("domain", {
      header: "Domain",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("overall_score", {
      header: "Overall score",
      sortingFn: (left, right, columnId) =>
        compareNullableNumbers(left.getValue(columnId), right.getValue(columnId)),
      cell: (info) => <ScorePill score={info.getValue()} />,
    }),
    columnHelper.accessor("fit_score", {
      header: "Fit score",
      sortingFn: (left, right, columnId) =>
        compareNullableNumbers(left.getValue(columnId), right.getValue(columnId)),
      cell: (info) => <ScorePill score={info.getValue()} />,
    }),
    columnHelper.accessor("timing_score", {
      header: "Timing score",
      sortingFn: (left, right, columnId) =>
        compareNullableNumbers(left.getValue(columnId), right.getValue(columnId)),
      cell: (info) => <ScorePill score={info.getValue()} />,
    }),
    columnHelper.accessor("confidence_score", {
      header: "Confidence score",
      sortingFn: (left, right, columnId) =>
        compareNullableNumbers(left.getValue(columnId), right.getValue(columnId)),
      cell: (info) => <ScorePill score={info.getValue()} />,
    }),
    columnHelper.accessor("recommended_persona", {
      header: "Recommended persona",
      cell: (info) => info.getValue() ?? "Missing",
    }),
    columnHelper.accessor("sales_angle", {
      header: "Sales angle",
      cell: (info) => {
        const value = info.getValue();
        return value ? truncateText(value, 72) : "Missing";
      },
    }),
    columnHelper.accessor("research_status", {
      header: "Research status",
      cell: (info) => formatStatus(info.getValue()),
    }),
    columnHelper.accessor("draft_quality_status", {
      header: "Draft quality",
      cell: (info) => <QualityStatusBadge status={info.getValue()} />,
    }),
    columnHelper.display({
      id: "open_account",
      header: "Open account",
      cell: ({ row }) => (
        <Link
          className="button button-secondary inline-button"
          href={`/campaigns/${campaignId}/accounts/${row.original.account_id}`}
        >
          Open account
        </Link>
      ),
    }),
  ];
}

export function AccountResultsTable({
  campaignId,
  accounts,
}: AccountResultsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "overall_score", desc: true },
  ]);

  const table = useReactTable({
    data: accounts,
    columns: buildColumns(campaignId),
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    sortDescFirst: true,
  });

  return (
    <div className="table-wrap">
      <table className="table results-table">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                const canSort = header.column.getCanSort();
                const sortState = header.column.getIsSorted();

                return (
                  <th key={header.id}>
                    {canSort ? (
                      <button
                        className="table-sort-button"
                        type="button"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                        <span className="table-sort-indicator">
                          {sortState === "desc"
                            ? "Desc"
                            : sortState === "asc"
                              ? "Asc"
                              : "Sort"}
                        </span>
                      </button>
                    ) : (
                      flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.length ? (
            table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className="results-empty-cell" colSpan={11}>
                No accounts match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
