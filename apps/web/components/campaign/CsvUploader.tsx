"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ApiError, uploadCampaignCsv } from "@/lib/api";
import type { UploadReportResponse } from "@/lib/types";

import { Button } from "../ui/Button";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Input } from "../ui/Input";
import { CsvUploadSummary } from "./CsvUploadSummary";

type CsvUploaderProps = {
  campaignId: string;
};

export function CsvUploader({ campaignId }: CsvUploaderProps) {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<UploadReportResponse | null>(null);

  const mutation = useMutation({
    mutationFn: (selectedFile: File) => uploadCampaignCsv(campaignId, selectedFile),
    onSuccess: (nextReport) => {
      setReport(nextReport);
      router.refresh();
    },
  });

  return (
    <div className="stack-md">
      <Input
        type="file"
        accept=".csv,text/csv"
        onChange={(event) => {
          const nextFile = event.target.files?.[0] ?? null;
          setFile(nextFile);
          setReport(null);
        }}
      />

      <p className="supporting-text">
        {file ? `Selected file: ${file.name}` : "Choose a CSV file to upload."}
      </p>

      {mutation.isError ? (
        <ErrorMessage
          message={
            mutation.error instanceof ApiError
              ? mutation.error.message
              : "Unable to upload CSV."
          }
        />
      ) : null}

      <Button
        onClick={async () => {
          if (!file) {
            return;
          }

          await mutation.mutateAsync(file);
        }}
        disabled={!file || mutation.isPending}
      >
        {mutation.isPending ? "Uploading CSV..." : "Upload CSV"}
      </Button>

      {report ? <CsvUploadSummary report={report} /> : null}
    </div>
  );
}
