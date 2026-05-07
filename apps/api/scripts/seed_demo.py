from __future__ import annotations

import argparse
from pathlib import Path

from app.config import PROJECT_ROOT, settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.campaign import CampaignCreate
from app.services import account_service, campaign_service, csv_service, event_service, run_service, workspace_service

DEFAULT_SAMPLE = PROJECT_ROOT / "samples" / "devtools_companies.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a demo Prospecting Agent campaign.")
    parser.add_argument(
        "--sample",
        default=str(DEFAULT_SAMPLE),
        help="Path to a CSV file with company_name and domain columns.",
    )
    parser.add_argument(
        "--run-fake-workflow",
        action="store_true",
        help="Execute the fake workflow after seeding accounts. Requires RESEARCH_MODE=fake.",
    )
    args = parser.parse_args()

    sample_path = Path(args.sample).expanduser().resolve()
    if not sample_path.is_file():
        raise SystemExit(f"Sample CSV not found: {sample_path}")

    init_db()
    db = SessionLocal()
    try:
        campaign = campaign_service.create_campaign(
            db,
            CampaignCreate(
                name="Phase 10 demo campaign",
                product_description="AI code review tool for engineering teams",
                ideal_customer_profile="B2B SaaS and developer tool companies with active engineering teams",
                pain_statement="Slow pull request review and inconsistent code quality",
                target_persona="VP Engineering, CTO, Head of Platform",
                tone="Direct, specific, no hype",
                max_accounts=10,
            ),
        )
        event_service.record_event(
            db,
            campaign_id=campaign.id,
            type="campaign_created",
            message="Campaign created",
        )
        event_service.record_event(
            db,
            campaign_id=campaign.id,
            type="campaign_workspace_created",
            message="Campaign workspace created",
            payload={"workspace_path": campaign.workspace_path},
        )

        file_bytes = sample_path.read_bytes()
        parsed = csv_service.parse_accounts_csv(file_bytes)
        created_accounts = account_service.create_accounts_for_campaign(
            db,
            campaign.id,
            [
                {"company_name": row.company_name, "domain": row.domain}
                for row in parsed.valid_accounts[: campaign.max_accounts]
            ],
        )
        workspace_service.write_uploaded_csv(campaign, file_bytes)
        workspace_service.write_normalized_accounts(
            campaign,
            [
                {"company_name": account.company_name, "domain": account.domain}
                for account in account_service.list_accounts_for_campaign(db, campaign.id)
            ],
        )
        event_service.record_event(
            db,
            campaign_id=campaign.id,
            type="accounts_created",
            message="Accounts created",
            payload={"created_accounts": len(created_accounts)},
        )
        if created_accounts:
            campaign = campaign_service.update_campaign_status(db, campaign.id, "ready") or campaign
            event_service.record_event(
                db,
                campaign_id=campaign.id,
                type="campaign_ready",
                message="Campaign is ready for the next phase",
                payload={"status": campaign.status},
            )

        run_note = "Seeded campaign and accounts only."
        if args.run_fake_workflow:
            if settings.research_mode != "fake":
                run_note = "Skipped fake workflow because RESEARCH_MODE is not set to fake."
            else:
                run = run_service.create_campaign_run(db, campaign.id)
                campaign_service.update_campaign_status(db, campaign.id, "running")
                run_service.execute_campaign_run(run.id, campaign.id)
                run_note = "Fake workflow completed."

        print("Demo campaign created.\n")
        print("Frontend:")
        print(f"http://localhost:3000/campaigns/{campaign.id}")
        print("\nRun progress:")
        print(f"http://localhost:3000/campaigns/{campaign.id}/run")
        print("\nResults:")
        print(f"http://localhost:3000/campaigns/{campaign.id}/results")
        print(f"\n{run_note}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
