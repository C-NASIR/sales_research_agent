import { z } from "zod";

export const createCampaignSchema = z.object({
  name: z.string().trim().min(1, "Campaign name is required"),
  product_description: z
    .string()
    .trim()
    .min(1, "Product description is required"),
  ideal_customer_profile: z
    .string()
    .trim()
    .min(1, "Ideal customer profile is required"),
  pain_statement: z.string().trim().min(1, "Pain statement is required"),
  target_persona: z.string().trim().min(1, "Target persona is required"),
  tone: z.string().trim().min(1, "Tone is required"),
  max_accounts: z
    .number()
    .min(1, "Max accounts must be at least 1")
    .max(100, "Max accounts must be at most 100"),
});

export type CreateCampaignFormValues = z.infer<typeof createCampaignSchema>;

export const createCampaignDefaults: CreateCampaignFormValues = {
  name: "AI code review outbound",
  product_description: "AI code review tool for engineering teams",
  ideal_customer_profile:
    "B2B SaaS companies and developer tool companies with active engineering teams",
  pain_statement: "Slow pull request review and inconsistent code quality",
  target_persona: "VP Engineering, CTO, Head of Platform",
  tone: "Direct, specific, no hype",
  max_accounts: 10,
};
