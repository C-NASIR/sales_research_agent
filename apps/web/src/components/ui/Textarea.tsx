import { forwardRef } from "react";
import type { TextareaHTMLAttributes } from "react";

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  function Textarea({ className = "", ...props }, ref) {
    return <textarea ref={ref} className={`textarea ${className}`.trim()} {...props} />;
  },
);
