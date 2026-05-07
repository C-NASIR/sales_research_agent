import type { ReactNode } from "react";

type FieldProps = Readonly<{
  label: string;
  htmlFor: string;
  description?: string;
  error?: string;
  children: ReactNode;
}>;

export function Field({
  label,
  htmlFor,
  description,
  error,
  children,
}: FieldProps) {
  return (
    <div className="field">
      <label className="field-label" htmlFor={htmlFor}>
        {label}
      </label>
      {description ? <p className="field-description">{description}</p> : null}
      {children}
      {error ? <p className="field-error">{error}</p> : null}
    </div>
  );
}
