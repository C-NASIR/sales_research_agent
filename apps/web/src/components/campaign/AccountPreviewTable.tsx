import type { Account } from "@/lib/types";

import { EmptyState } from "../ui/EmptyState";

type AccountPreviewTableProps = {
  accounts: Account[];
};

export function AccountPreviewTable({ accounts }: AccountPreviewTableProps) {
  if (accounts.length === 0) {
    return (
      <EmptyState
        title="No accounts uploaded"
        message="Upload a CSV to create accounts for this campaign."
      />
    );
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Company name</th>
            <th>Domain</th>
            <th>Research status</th>
            <th>Review status</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((account) => (
            <tr key={account.id}>
              <td>{account.company_name}</td>
              <td>{account.domain}</td>
              <td>{account.research_status}</td>
              <td>{account.review_status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
