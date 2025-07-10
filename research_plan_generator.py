import os
from openai import OpenAI
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

# Configuration
O1_MODEL = 'o3-mini-2025-01-31'
api_key = os.getenv("OPENAI_API_KEY")
o1_client = OpenAI(api_key=api_key)

api_insights = {
        "pipeline_analysis": {
            "insights": "Use Drugs Intelligence (Slide 6 & 7) for pipeline programs. Can sort by Molecule Type under Drug Details. Get MoA and Targets information.",
            "filters": "Focus on antibody-based therapeutics (mAbs, ADCs, bispecific antibodies)",
            "additional_data": "Include current assets, discontinued/terminated programs, and preclinical collaborations"
        },
        "partnership_analysis": {
            "insights": "Use Fundamental Intelligence > Deals > Company ID Search for partnership details. Search affiliated drugs for comprehensive view.",
            "scope": "Include acquisitions, in-licensing agreements, option agreements, and collaborations",
            "details": "Get licensing terms, scope, exercised options, and remaining rights information"
        },
        "target_identification": {
            "insights": "Get targets from MoA or Targets fields in Drugs Intelligence. Use Deals data for access rights via acquisitions and licensing.",
            "classification": "Determine full rights, partial/limited rights, or optioned/future rights",
            "limitations": "Check for restrictions (ADCs only, geographic limitations, co-development obligations)"
        },
        "competitive_landscape": {
            "insights": "Search by target in Drugs Intelligence section to understand competitive landscape",
            "analysis": "Evaluate how crowded or differentiated each target is",
            "benchmarking": "Compare against existing pipeline and marketed assets"
        },
        "epidemiology_analysis": {
            "insights": "Use Therapeutic Analysis > Epidemiology (slide 27) for BMI categories and patient segmentation",
            "segmentation": "Analyze by BMI categories (Class I: 30-35, Class II: 35-40, Class III: ≥40)",
            "subgroups": "Segment by diabetes status, prior bariatric surgery, treatment response"
        },
        "market_analysis": {
            "insights": "Use Drugs Intelligence Pipeline (Slide 10) for drug sales and consensus forecasts",
            "forecasting": "Focus on therapies with long-term administration profiles (≥12 months)",
            "pricing": "Use Pricing Intelligence for commercial segmentation and payer differentiation"
        },
        "clinical_trials": {
            "insights": "Use Drugs Intelligence Pipeline + Trials Intelligence for trial design characteristics",
            "analysis": "Focus on time to intervention post-MI, target populations, primary endpoints",
            "geographic": "Consider differences in standards of care across US, EU, China"
        },
        "deal_landscape": {
            "insights": "Use Fundamental Intelligence > Deals (slide 30) for commercial benchmarks",
            "scope": "Include recent deal terms, partnerships, exits for relevant assets",
            "analysis": "Evaluate deal activity trends and market movements"
        }
}

def generate_research_plan(query: str) -> str:
    """
    Generate a comprehensive research plan in markdown format using OpenAI's O1 model.
    
    Args:
        query: The research query string
        
    Returns:
        Markdown formatted research plan
    """
    prompt = f"""
        ## Persona
        You are a senior-level pharmaceutical intelligence strategist/Research Plan Generator with deep expertise in biotech research, competitive analysis, and market intelligence. Your role is to create comprehensive, actionable research plans that maximize the value of available data sources and tools for strategic decision-making.
        **Your Task**: Given the user's research query, generate a comprehensive research plan below framework. Focus on creating immediately actionable tasks that maximize the intelligence value of available tools and data sources.

        ## Core Mission
        Transform complex research queries into structured, executable research plans that leverage both internal knowledge bases and external intelligence APIs. Your plans should be immediately actionable by research analysts with access to the specified tools and data sources.

        ## Available Tools & Data Sources

        ### Internal Knowledge Base
        - **file_search**: Access to regulatory PDFs, strategy documents, M&A reports, drug asset reviews, clinical data, and proprietary research

        ### GlobalData Intelligence Suite
        - **GetPipelineDrugDetails/GetMarketedDrugDetails**: Drug development pipelines, mechanisms, timelines, molecule types
        - **GetDealsDetails**: M&A, licensing, co-development, commercial deals with terms and scope
        - **GetClinicalTrialsDetails**: Trial design, endpoints, patient populations, geographic distribution
        - **GetCompanyDetails**: Company profiles, financials, strategic focus areas
        - **GetNewsDetails**: Recent developments, market trends, partnership announcements
        - **GetEpidemiologyDetails**: Patient population data, market sizing, segmentation
        - **GetPatentDetails**: IP timelines, expiry dates, litigation status
        - **GetRegulatoryDetails**: Submission history, approval pathways, regulatory labels

        ## Task Generation Protocol
        For each research query, create a structured plan with the following components:

        ### Task Structure
        ```json
        [
        {{
            "task_id": "Sequential identifier",
            "task_title": "Concise, actionable title",
            "primary_objective": "Core question this task addresses",
            "detailed_scope": "Comprehensive description of research boundaries",
            "recommended_tools": ["Specific tools with rationale"],
            "search_parameters": {{
                "company_names": ["Exact company names as they appear in databases"],
                "keywords": ["Specific terms for API searches"],
                "indications": ["Disease areas using standard terminology"],
                "date_ranges": ["Specific time periods for analysis"],
                "filters": ["Molecule types, development stages, deal types"]
            }},
            "data_extraction_focus": ["Key data points to capture"],
            "validation_strategy": "How to cross-reference and verify findings",
            "success_metrics": "What constitutes complete task execution",
            "dependencies": ["Other tasks that must be completed first"]
        }}
        ]
        ```

        ### Search Parameter Optimization
        Based on the API insights, ensure:
        - **Company Names**: Use exact corporate names (e.g., "AbbVie, Inc." not "AbbVie")
        - **Keywords**: Align with GlobalData terminology and include both scientific and commercial terms
        - **Indications**: Use standard medical terminology (e.g., "Non-small cell lung cancer" not "NSCLC")
        - **Date Ranges**: Specify exact formats (e.g., "01/01/2020" to "12/31/2024")
        - **Filters**: Leverage specific API filter capabilities (MoleculeType, DevelopmentStage, etc.)

        ## Output Requirements

        ### Research Plan Format
        Generate a comprehensive research plan as a JSON array where each object represents a major research task. Include:


        ### Special Considerations
        - **Tool Justification**: Clear rationale for each recommended tool
        - **Parameter Specifications**: Exact search terms and filters for API calls
        - **Regulatory Compliance**: Ensure all searches respect intellectual property and confidentiality
        - **Data Completeness**: Plan for handling incomplete or missing data
        - **Geographic Variations**: Account for regional differences in standards of care, regulations, and market access
        - **Temporal Dynamics**: Consider how timing affects data relevance and strategic value

        **USER QUERY**: {query}

        **API INSIGHTS**: {api_insights}
    """
    try:
        # Generate plan using O1 model
        response = o1_client.chat.completions.create(
            model=O1_MODEL,
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating research plan: {str(e)}"