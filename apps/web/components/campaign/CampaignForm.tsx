"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { ApiError, createCampaign } from "@/lib/api";
import {
  createCampaignDefaults,
  createCampaignSchema,
  type CreateCampaignFormValues,
} from "@/lib/validators";

import { Button } from "../ui/Button";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Field } from "../ui/Field";
import { Input } from "../ui/Input";
import { Textarea } from "../ui/Textarea";

export function CampaignForm() {
  const router = useRouter();
  const form = useForm<CreateCampaignFormValues>({
    resolver: zodResolver(createCampaignSchema),
    defaultValues: createCampaignDefaults,
  });

  const mutation = useMutation({
    mutationFn: createCampaign,
    onSuccess: (campaign) => {
      router.push(`/campaigns/${campaign.id}`);
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    await mutation.mutateAsync(values);
  });

  return (
    <form className="stack-lg" onSubmit={onSubmit}>
      <Field
        label="Campaign name"
        htmlFor="name"
        error={form.formState.errors.name?.message}
      >
        <Input id="name" {...form.register("name")} />
      </Field>

      <Field
        label="Product description"
        htmlFor="product_description"
        error={form.formState.errors.product_description?.message}
      >
        <Textarea
          id="product_description"
          rows={4}
          {...form.register("product_description")}
        />
      </Field>

      <Field
        label="Ideal customer profile"
        htmlFor="ideal_customer_profile"
        error={form.formState.errors.ideal_customer_profile?.message}
      >
        <Textarea
          id="ideal_customer_profile"
          rows={4}
          {...form.register("ideal_customer_profile")}
        />
      </Field>

      <Field
        label="Pain statement"
        htmlFor="pain_statement"
        error={form.formState.errors.pain_statement?.message}
      >
        <Textarea id="pain_statement" rows={3} {...form.register("pain_statement")} />
      </Field>

      <Field
        label="Target persona"
        htmlFor="target_persona"
        error={form.formState.errors.target_persona?.message}
      >
        <Textarea id="target_persona" rows={3} {...form.register("target_persona")} />
      </Field>

      <Field
        label="Tone"
        htmlFor="tone"
        error={form.formState.errors.tone?.message}
      >
        <Textarea id="tone" rows={2} {...form.register("tone")} />
      </Field>

      <Field
        label="Max accounts"
        htmlFor="max_accounts"
        description="Choose between 1 and 100 accounts for the first run."
        error={form.formState.errors.max_accounts?.message}
      >
        <Input
          id="max_accounts"
          type="number"
          min={1}
          max={100}
          {...form.register("max_accounts", { valueAsNumber: true })}
        />
      </Field>

      {mutation.isError ? (
        <ErrorMessage
          message={
            mutation.error instanceof ApiError
              ? mutation.error.message
              : "Unable to create campaign."
          }
        />
      ) : null}

      <div className="form-actions">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Creating campaign..." : "Create campaign"}
        </Button>
        <Link className="button button-ghost" href="/campaigns">
          Back to campaign list
        </Link>
      </div>
    </form>
  );
}
