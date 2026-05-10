"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
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
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<UploadReportResponse | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (selectedFile: File) => uploadCampaignCsv(campaignId, selectedFile),
    onSuccess: async (nextReport) => {
      setLocalError(null);
      setReport(nextReport);
      await queryClient.invalidateQueries({
        queryKey: ["campaign-detail", campaignId],
      });
    },
  });

  async function handleUpload() {
    setLocalError(null);
    if (!file) {
      setLocalError("Choose a CSV file before uploading.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setLocalError("Uploaded file must use the .csv extension.");
      return;
    }

    await mutation.mutateAsync(file);
  }

  return (
    <div className="stack-md">
      <Input
        type="file"
        accept=".csv,text/csv"
        disabled={mutation.isPending}
        onChange={(event) => {
          const nextFile = event.target.files?.[0] ?? null;
          setFile(nextFile);
          setReport(null);
          setLocalError(null);
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

      {localError ? <ErrorMessage message={localError} /> : null}

      <Button onClick={handleUpload} disabled={!file || mutation.isPending}>
        {mutation.isPending ? "Uploading CSV..." : "Upload CSV"}
      </Button>

      {report ? <CsvUploadSummary report={report} /> : null}
    </div>
  );
}
