from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from app.schemas.upload import UploadDuplicateRow, UploadInvalidRow


REQUIRED_COLUMNS = {"company_name", "domain"}


class CSVValidationError(ValueError):
    pass


class MissingColumnsError(CSVValidationError):
    def __init__(self, missing_columns: set[str]):
        self.missing_columns = missing_columns
        columns = ", ".join(sorted(missing_columns))
        super().__init__(f"Missing required columns: {columns}")


@dataclass
class ParsedAccountRow:
    row_number: int
    company_name: str
    domain: str


@dataclass
class CSVParseResult:
    valid_accounts: list[ParsedAccountRow]
    invalid_rows: list[UploadInvalidRow]
    duplicate_rows: list[UploadDuplicateRow]


def normalize_domain(raw_domain: str) -> str:
    domain = raw_domain.strip().lower()
    if domain.startswith("http://"):
        domain = domain.removeprefix("http://")
    if domain.startswith("https://"):
        domain = domain.removeprefix("https://")
    if domain.startswith("www."):
        domain = domain.removeprefix("www.")
    domain = domain.split("?", maxsplit=1)[0]
    domain = domain.split("/", maxsplit=1)[0]
    return domain.rstrip("/").strip()


def parse_accounts_csv(file_bytes: bytes) -> CSVParseResult:
    try:
        decoded = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CSVValidationError("CSV must be valid UTF-8") from exc

    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames is None:
        raise MissingColumnsError(REQUIRED_COLUMNS)

    normalized_headers = [_normalize_header(name) for name in reader.fieldnames]
    reader.fieldnames = normalized_headers

    missing_columns = REQUIRED_COLUMNS.difference(normalized_headers)
    if missing_columns:
        raise MissingColumnsError(missing_columns)

    valid_accounts: list[ParsedAccountRow] = []
    invalid_rows: list[UploadInvalidRow] = []
    duplicate_rows: list[UploadDuplicateRow] = []
    seen_domains: set[str] = set()

    for row_number, row in enumerate(reader, start=2):
        raw = {key: (value or "") for key, value in row.items() if key is not None}
        if _is_empty_row(raw):
            continue

        company_name = raw.get("company_name", "").strip()
        normalized_domain = normalize_domain(raw.get("domain", ""))

        if not company_name:
            invalid_rows.append(
                UploadInvalidRow(
                    row_number=row_number,
                    reason="company_name is required",
                    raw=raw,
                )
            )
            continue

        if not normalized_domain:
            invalid_rows.append(
                UploadInvalidRow(
                    row_number=row_number,
                    reason="domain is required",
                    raw=raw,
                )
            )
            continue

        if normalized_domain in seen_domains:
            duplicate_rows.append(
                UploadDuplicateRow(
                    row_number=row_number,
                    company_name=company_name,
                    domain=normalized_domain,
                    duplicate_of_domain=normalized_domain,
                )
            )
            continue

        seen_domains.add(normalized_domain)
        valid_accounts.append(
            ParsedAccountRow(
                row_number=row_number,
                company_name=company_name,
                domain=normalized_domain,
            )
        )

    return CSVParseResult(
        valid_accounts=valid_accounts,
        invalid_rows=invalid_rows,
        duplicate_rows=duplicate_rows,
    )


def _normalize_header(header: str | None) -> str:
    return (header or "").strip().lower()


def _is_empty_row(row: dict[str, str]) -> bool:
    return all(not value.strip() for value in row.values())
