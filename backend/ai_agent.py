import re
import pandas as pd
import numpy as np

class BIAgent:
    def __init__(self, deals_df: pd.DataFrame, wos_df: pd.DataFrame):
        self.deals = deals_df
        self.wos = wos_df
        
    def answer_query(self, query: str) -> dict:
        q = query.lower().strip()
        
        # 1. Pipeline sector / health sector queries
        if 'pipeline' in q or 'deals' in q:
            # Check if specific sector is queried
            sector = None
            for s in ['energy', 'mining', 'powerline', 'solar', 'wind', 'infrastructure', 'agriculture']:
                if s in q:
                    sector = s
                    break
            
            if sector:
                # Filter deals by sector
                sector_title = sector.capitalize()
                subset = self.deals[self.deals['Sector/service'].str.lower().str.contains(sector)]
                total_val = subset['Masked Deal value'].sum()
                count = len(subset)
                by_stage = subset.groupby('Deal Stage')['Masked Deal value'].agg(['sum', 'count']).to_dict(orient='index')
                
                # Context generation
                stage_breakdown = ", ".join([f"{k}: INR {v['sum']:,.2f} ({v['count']} deals)" for k, v in by_stage.items()])
                
                # Data Caveat: Mentioning missing values/null fields in key attributes
                missing_vals = subset['Masked Deal value'].isna().sum() + (subset['Masked Deal value'] == 0).sum()
                caveats = []
                if missing_vals > 0:
                    caveats.append(f"Note: {missing_vals} deals in this sector have missing or zero values, which may understate the total pipeline.")
                
                answer = (
                    f"The pipeline for the **{sector_title}** sector has a total value of **INR {total_val:,.2f}** across **{count}** deals.\n\n"
                    f"**Breakdown by Stage:**\n{stage_breakdown if stage_breakdown else 'No stages found'}.\n"
                )
                if caveats:
                    answer += f"\n**Data Quality Caveats:**\n" + "\n".join([f"- {c}" for c in caveats])
                    
                return {
                    "answer": answer,
                    "metrics": {
                        "total_value": total_val,
                        "deal_count": count,
                        "by_stage": by_stage
                    },
                    "caveats": caveats
                }
            else:
                # General pipeline
                total_val = self.deals['Masked Deal value'].sum()
                count = len(self.deals)
                by_sector = self.deals.groupby('Sector/service')['Masked Deal value'].sum().sort_values(ascending=False).to_dict()
                
                sector_str = ", ".join([f"{k}: INR {v:,.2f}" for k, v in by_sector.items()])
                answer = (
                    f"Our overall pipeline contains **{count}** deals with a total masked value of **INR {total_val:,.2f}**.\n\n"
                    f"**Breakdown by Sector:**\n{sector_str}"
                )
                return {
                    "answer": answer,
                    "metrics": {
                        "total_value": total_val,
                        "deal_count": count,
                        "by_sector": by_sector
                    },
                    "caveats": []
                }
                
        # 2. Revenue / Billing queries
        elif 'revenue' in q or 'revenue collected' in q or 'collected' in q or 'billing' in q or 'invoice' in q:
            total_billed_incl = self.wos['Billed Value in Rupees (Incl of GST.) (Masked)'].sum()
            total_billed_excl = self.wos['Billed Value in Rupees (Excl of GST.) (Masked)'].sum()
            total_collected = self.wos['Collected Amount in Rupees (Incl of GST.) (Masked)'].sum()
            receivables = self.wos['Amount Receivable (Masked)'].sum()
            
            # Group by sector
            rev_by_sector = self.wos.groupby('Sector')['Collected Amount in Rupees (Incl of GST.) (Masked)'].sum().sort_values(ascending=False).to_dict()
            sector_str = ", ".join([f"{k}: INR {v:,.2f}" for k, v in rev_by_sector.items()])
            
            answer = (
                f"**Financial Operations Summary:**\n"
                f"- **Total Revenue Collected (Incl GST):** INR {total_collected:,.2f}\n"
                f"- **Total Billed (Excl GST):** INR {total_billed_excl:,.2f}\n"
                f"- **Total Billed (Incl GST):** INR {total_billed_incl:,.2f}\n"
                f"- **Total Outstanding Receivables:** INR {receivables:,.2f}\n\n"
                f"**Collected Revenue by Sector:**\n{sector_str}"
            )
            
            missing_coll = self.wos['Collected Amount in Rupees (Incl of GST.) (Masked)'].isna().sum()
            caveats = []
            if missing_coll > 0:
                caveats.append(f"There are {missing_coll} work orders without collection logs.")
                
            return {
                "answer": answer,
                "metrics": {
                    "total_collected": total_collected,
                    "total_billed_excl": total_billed_excl,
                    "total_billed_incl": total_billed_incl,
                    "receivables": receivables,
                    "by_sector": rev_by_sector
                },
                "caveats": caveats
            }
            
        # 3. Work Orders / Operational status queries
        elif 'work order' in q or 'execution' in q or 'status' in q or 'projects' in q:
            status_counts = self.wos['Execution Status'].value_counts().to_dict()
            status_str = ", ".join([f"{k}: {v}" for k, v in status_counts.items()])
            
            # Find cross-linkage to pipeline deals
            linked_deals = len(self.wos[self.wos['Deal name masked'].isin(self.deals['Deal Name'])])
            
            answer = (
                f"**Operational Execution Summary:**\n"
                f"Total active/tracked work orders: **{len(self.wos)}**\n"
                f"- **Status breakdown:** {status_str}\n"
                f"- **Linked with Sales Pipeline:** {linked_deals} work orders match deals by name."
            )
            return {
                "answer": answer,
                "metrics": {
                    "total_wos": len(self.wos),
                    "status_breakdown": status_counts,
                    "linked_deals": linked_deals
                },
                "caveats": []
            }
            
        # Fallback / Clarification Prompt
        else:
            return {
                "answer": (
                    "I could not fully match your question to a specific business metric.\n"
                    "Please try asking about one of the following:\n"
                    "1. **Pipeline health** (e.g., 'How is our pipeline looking for the energy sector this quarter?')\n"
                    "2. **Revenue and Billing** (e.g., 'What is our total collected revenue or outstanding receivables?')\n"
                    "3. **Work Order Execution** (e.g., 'What is the operational status of our work orders?')"
                ),
                "metrics": {},
                "caveats": [],
                "requires_clarification": True
            }
