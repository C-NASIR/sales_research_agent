"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { ApiError, updateOutreachDraft } from "@/lib/api";
import type { OutreachDraft, OutreachDraftUpdate } from "@/lib/types";

import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Field } from "../ui/Field";
import { Input } from "../ui/Input";
import { Textarea } from "../ui/Textarea";

type DraftEditorProps = {
  campaignId: string;
  accountId: string;
  draft: OutreachDraft | null;
  onUpdated: (draft: OutreachDraft) => void;
};

type DraftFormState = {
  subject: string;
  body: string;
  personalization_source: string;
  personalization_source_url: string;
  sales_angle: string;
};

function toFormState(draft: OutreachDraft | null): DraftFormState {
  return {
    subject: draft?.subject ?? "",
    body: draft?.body ?? "",
    personalization_source: draft?.personalization_source ?? "",
    personalization_source_url: draft?.personalization_source_url ?? "",
    sales_angle: draft?.sales_angle ?? "",
  };
}

export function DraftEditor({
  campaignId,
  accountId,
  draft,
  onUpdated,
}: DraftEditorProps) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<DraftFormState>(() => toFormState(draft));
  const [savedMessage, setSavedMessage] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    setForm(toFormState(draft));
    setSavedMessage(null);
    setLocalError(null);
  }, [draft]);

  const mutation = useMutation({
    mutationFn: (input: OutreachDraftUpdate) =>
      updateOutreachDraft(campaignId, accountId, input),
    onSuccess: async (response) => {
      setSavedMessage("Draft saved.");
      onUpdated(response);
      await queryClient.invalidateQueries({
        queryKey: ["campaign-results", campaignId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["account-detail", campaignId, accountId],
      });
    },
  });

  if (!draft) {
    return (
      <Card className="stack-md">
        <h2>Draft editor</h2>
        <p>No outreach draft is available for this account.</p>
      </Card>
    );
  }

  async function handleSave() {
    setSavedMessage(null);
    setLocalError(null);
    if (!form.subject.trim()) {
      setLocalError("Subject cannot be empty.");
      return;
    }
    if (!form.body.trim()) {
      setLocalError("Body cannot be empty.");
      return;
    }
    const input: OutreachDraftUpdate = {
      subject: form.subject,
      body: form.body,
      personalization_source: form.personalization_source,
      personalization_source_url: form.personalization_source_url || null,
      sales_angle: form.sales_angle,
    };
    await mutation.mutateAsync(input);
  }

  const hasChanges =
    form.subject !== (draft.subject ?? "") ||
    form.body !== (draft.body ?? "") ||
    form.personalization_source !== (draft.personalization_source ?? "") ||
    form.personalization_source_url !== (draft.personalization_source_url ?? "") ||
    form.sales_angle !== (draft.sales_angle ?? "");

  return (
    <Card className="stack-md">
      <div className="card-row">
        <div>
          <h2>Draft editor</h2>
          <p className="supporting-text">
            Edit the generated draft before exporting. This does not send any email.
          </p>
        </div>
        {savedMessage ? <p className="success-message">{savedMessage}</p> : null}
      </div>

      <div className="stack-md">
        <Field label="Subject" htmlFor="draft-subject">
          <Input
            id="draft-subject"
            value={form.subject}
            onChange={(event) => {
              setSavedMessage(null);
              setLocalError(null);
              setForm((current) => ({ ...current, subject: event.target.value }));
            }}
          />
        </Field>

        <Field label="Body" htmlFor="draft-body">
          <Textarea
            id="draft-body"
            value={form.body}
            onChange={(event) => {
              setSavedMessage(null);
              setLocalError(null);
              setForm((current) => ({ ...current, body: event.target.value }));
            }}
          />
        </Field>

        <Field label="Personalization source" htmlFor="draft-personalization-source">
          <Input
            id="draft-personalization-source"
            value={form.personalization_source}
            onChange={(event) => {
              setSavedMessage(null);
              setLocalError(null);
              setForm((current) => ({
                ...current,
                personalization_source: event.target.value,
              }));
            }}
          />
        </Field>

        <Field
          label="Personalization source URL"
          htmlFor="draft-personalization-source-url"
        >
          <Input
            id="draft-personalization-source-url"
            value={form.personalization_source_url}
            onChange={(event) => {
              setSavedMessage(null);
              setLocalError(null);
              setForm((current) => ({
                ...current,
                personalization_source_url: event.target.value,
              }));
            }}
          />
        </Field>

        <Field label="Sales angle" htmlFor="draft-sales-angle">
          <Input
            id="draft-sales-angle"
            value={form.sales_angle}
            onChange={(event) => {
              setSavedMessage(null);
              setLocalError(null);
              setForm((current) => ({ ...current, sales_angle: event.target.value }));
            }}
          />
        </Field>
      </div>

      {localError ? <ErrorMessage message={localError} /> : null}

      {mutation.isError ? (
        <ErrorMessage
          message={
            mutation.error instanceof ApiError
              ? mutation.error.message
              : "Unable to save draft."
          }
        />
      ) : null}

      <Button disabled={!hasChanges || mutation.isPending} onClick={handleSave}>
        {mutation.isPending ? "Saving draft..." : "Save draft changes"}
      </Button>
    </Card>
  );
}
