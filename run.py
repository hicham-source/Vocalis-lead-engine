import argparse
from dotenv import load_dotenv
from database import init_db
from discovery import fetch_places
from enrichment import enrich_leads
from audit_drafts import generate_audit_and_drafts

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="B2B Lead Generation Pipeline")
    parser.add_argument("--niche", required=True, help="E.g., 'dental clinic'")
    parser.add_argument("--district", required=True, help="E.g., 'Al Olaya'")
    args = parser.parse_args()
    
    print("\n--- Phase 1: Init Database ---")
    init_db()
    
    print("\n--- Phase 2: Discovery ---")
    fetch_places(args.niche, args.district)
    
    print("\n--- Phase 3: Enrichment ---")
    enrich_leads()
    
    print("\n--- Phase 4: AI Audit & Drafting ---")
    generate_audit_and_drafts()
    
    print("\n Pipeline complete. Run `streamlit run dashboard.py` to review leads.")

if __name__ == "__main__":
    main()
