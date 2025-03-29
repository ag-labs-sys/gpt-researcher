import warnings
from datetime import date, datetime, timezone

from .utils.enum import ReportSource, ReportType, Tone
from typing import List, Dict, Any


def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 3,
    context: List[Dict[str, Any]] = [],
):
    """Generates the search queries prompt for the given question.
    Args:
        question (str): The question to generate the search queries prompt for
        parent_query (str): The main question (only relevant for detailed reports)
        report_type (str): The report type
        max_iterations (int): The maximum number of search queries to generate
        context (str): Context for better understanding of the task with realtime web information

    Returns: str: The search queries prompt for the given question
    """

    if (
        report_type == ReportType.DetailedReport.value
        or report_type == ReportType.SubtopicReport.value
    ):
        task = f"{parent_query} - {question}"
    else:
        task = question

    context_prompt = f"""
You are a seasoned research assistant tasked with generating search queries to find relevant information for the following task: "{task}".
Context: {context}

Use this context to inform and refine your search queries. The context provides real-time web information that can help you generate more specific and relevant queries. Consider any current events, recent developments, or specific details mentioned in the context that could enhance the search queries.
""" if context else ""

    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])

    return f"""Write {max_iterations} google search queries to search online that form an objective opinion from the following task: "{task}"

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

{context_prompt}
You must respond with a list of strings in the following format: [{dynamic_example}].
The response should contain ONLY the list.
"""


def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
    language="english",
):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
You MUST write all used source URLs at the end of the report as references, ensuring that no duplicate sources appear.
        Each URL should be hyperlinked: [Source Name](URL)
        Additionally, include hyperlinks within the report for any referenced sources in the following format:
"""
    else:
        reference_prompt = f"""
        You MUST list all source document names at the end of the report as references, ensuring that no duplicate sources appear.
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""

    return f"""
    You are an **epidemiologist with a PhD**, specializing in **disease patterns, risk factors, prevention strategies, and public health implications**. Your expertise allows you to provide **accurate, evidence-based insights** and recommendations. You have an **informative and professional tone of voice** with a **structured and analytical writing style**.
Information: "{context}"
---
Answer the query: "{question}" in a **detailed, structured epidemiological report**. The report should be **informative, evidence-based, and well-organized**, with a minimum of {total_words} words.

## **Report Structure and Sections**
The report should contain the following key sections:

### ** Introduction**
GIve the detail introduction about the disease. mentioned in the query

### **1. Epidemiology** 
This section provides an overview of the disease's epidemiology, 
including global prevalence and key demographic factors. 
It should discuss the total number of affected individuals worldwide, 
along with variations across regions such as the U.S., EU4+UK, and the Rest of the World (ROW). 
Additionally, it should highlight risk factors such as age, gender, genetic predisposition, 
and environmental triggers. Trends in incidence rates over time should be explored, 
identifying any regional disparities or changes due to improved awareness, diagnostic advancements, 
or emerging treatment options.

### **2. Prevalence and Diagnosis Rates**
| Region       | Total Prevalent Patients | Diagnosed Patients | Diagnosed % of Prevalence |
|-------------|-------------------------|--------------------|---------------------------|
| U.S.        |                         |                    |                           |
| EU4+UK      |                         |                    |                           |
| ROW         |                         |                    |                           |

- Provide a detailed analysis of diagnosis trends across regions.

### **3. Treated Patients**
| Region       | Total Treated Patients | Treated % of Diagnosed |
|-------------|------------------------|------------------------|
| U.S.        |                        |                        |
| EU4+UK      |                        |                        |
| ROW         |                        |                        |

- Discuss factors influencing treatment rates, including **access to therapies, healthcare policies, and drug availability**.

### **4. Disease Stage Segmentation**
| Stage          | % Treated in U.S. | % Treated in EU4+UK | % Treated in ROW |
|---------------|------------------|--------------------|------------------|
| Early-Stage  |                  |                    |                  |
| Moderate-Stage |                  |                    |                  |
| Severe       |                  |                    |                  |
| End-Stage   |                  |                    |                  |

- Assess treatment distribution by disease stage and **healthcare system variations**.

### **5. Forecast Insights**
- Provide **data-driven projections** on prevalence, diagnosis, and treatment trends.
- Highlight **expected growth rates (CAGR)** and **treatment innovations** (e.g., biosimilars, biologics, JAK inhibitors).
- Compare future trends between **U.S., EU4+UK, and ROW**.

## **Guidelines**
- You MUST determine a **concrete, evidence-based conclusion** from the given data.
- Write the report using **markdown syntax** and **{report_format} format**.
- Use **reliable and recent sources** over outdated materials.
- Ensure all in-text citations follow {report_format} format and are **hyperlinked** in markdown.
- Don't forget to add a **reference list** at the end of the report.
- {reference_prompt}
- {tone_prompt}

The report must be written in **{language}**.
Assume today's date is **{date.today()}**.
"""

def curate_sources(query, sources, max_results=10):
    return f"""Your goal is to evaluate and curate the provided scraped content for the research task: "{query}" 
    while prioritizing the inclusion of relevant and high-quality information, especially sources containing statistics, numbers, or concrete data.

The final curated list will be used as context for creating a research report, so prioritize:
- Retaining as much original information as possible, with extra emphasis on sources featuring quantitative data or unique insights
- Including a wide range of perspectives and insights
- Filtering out only clearly irrelevant or unusable content

EVALUATION GUIDELINES:
1. Assess each source based on:
   - Relevance: Include sources directly or partially connected to the research query. Err on the side of inclusion.
   - Credibility: Favor authoritative sources but retain others unless clearly untrustworthy.
   - Currency: Prefer recent information unless older data is essential or valuable.
   - Objectivity: Retain sources with bias if they provide a unique or complementary perspective.
   - Quantitative Value: Give higher priority to sources with statistics, numbers, or other concrete data.
2. Source Selection:
   - Include as many relevant sources as possible, up to {max_results}, focusing on broad coverage and diversity.
   - Prioritize sources with statistics, numerical data, or verifiable facts.
   - Overlapping content is acceptable if it adds depth, especially when data is involved.
   - Exclude sources only if they are entirely irrelevant, severely outdated, or unusable due to poor content quality.
3. Content Retention:
   - DO NOT rewrite, summarize, or condense any source content.
   - Retain all usable information, cleaning up only clear garbage or formatting issues.
   - Keep marginally relevant or incomplete sources if they contain valuable data or insights.

SOURCES LIST TO EVALUATE:
{sources}

You MUST return your response in the EXACT sources JSON list format as the original sources.
The response MUST not contain any markdown format or additional text (like ```json), just the JSON list!
"""




def generate_resource_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None, total_words=1000, language="english"
):
    """Generates the resource report prompt for the given question and research summary.

    Args:
        question (str): The question to generate the resource report prompt for.
        context (str): The research summary to generate the resource report prompt for.

    Returns:
        str: The resource report prompt for the given question and research summary.
    """

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
            You MUST include all relevant source urls.
            Every url should be hyperlinked: [url website](url)
            """
    else:
        reference_prompt = f"""
            You MUST write all used source document names at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each."
        """

    return (
        f'"""{context}"""\n\nBased on the above information, generate a bibliography recommendation report for the following'
        f' question or topic: "{question}". The report should provide a detailed analysis of each recommended resource,'
        " explaining how each source can contribute to finding answers to the research question.\n"
        "Focus on the relevance, reliability, and significance of each source.\n"
        "Ensure that the report is well-structured, informative, in-depth, and follows Markdown syntax.\n"
        "Include relevant facts, figures, and numbers whenever available.\n"
        f"The report should have a minimum length of {total_words} words.\n"
        f"You MUST write the report in the following language: {language}.\n"
        "You MUST include all relevant source urls."
        "Every url should be hyperlinked: [url website](url)"
        f"{reference_prompt}"
    )


def generate_custom_report_prompt(
    query_prompt, context, report_source: str, report_format="apa", tone=None, total_words=1000, language: str = "english"
):
    return f'"{context}"\n\n{query_prompt}'


def generate_outline_report_prompt(
    question, context, report_source: str, report_format="apa", tone=None,  total_words=1000, language: str = "english"
):
    """Generates the outline report prompt for the given question and research summary.
    Args: question (str): The question to generate the outline report prompt for
            research_summary (str): The research summary to generate the outline report prompt for
    Returns: str: The outline report prompt for the given question and research summary
    """

    return (
        f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax'
        f' for the following question or topic: "{question}". The outline should provide a well-structured framework'
        " for the research report, including the main sections, subsections, and key points to be covered."
        f" The research report should be detailed, informative, in-depth, and a minimum of {total_words} words."
        " Use appropriate Markdown syntax to format the outline and ensure readability."
    )



def generate_deep_research_prompt(
    question: str,
    context: str,
    report_source: str,
    report_format="apa",
    tone=None,
    total_words=2000,
    language: str = "english"
):
    """Generates the deep research report prompt with an epidemiological analysis structure.
    Args:
        question (str): The research question
        context (str): The research context containing learnings with citations
        report_source (str): Source of the research (web, etc.)
        report_format (str): Report formatting style
        tone: The tone to use in writing
        total_words (int): Minimum word count
        language (str): Output language
    Returns:
        str: The deep research report prompt
    """
    reference_prompt = ""
    if report_source == "web":
        reference_prompt = f"""
You MUST write all used source URLs at the end of the report as references, ensuring no duplicates. Each reference should be hyperlinked:

**Example:** Author, A. A. (Year, Month Date). Title of web page. Website Name. [URL](URL)
        """
    else:
        reference_prompt = f"""
You MUST write all used source document names at the end of the report as references, ensuring no duplicates.
        """
    
    tone_prompt = f"Write the report in a {tone} tone." if tone else ""
    
    return f"""
### **Role and Expertise**
You are an **epidemiologist with a PhD**, specializing in **disease patterns, risk factors, prevention strategies, and public health implications**. You provide **accurate, evidence-based insights** with a **structured and analytical writing style**.

## **Context and Research Question**
**Research Context:**
"{context}"

**Research Question:**
"{question}"

## **Report Structure and Sections**
Ensure the report follows this structured approach:
### **1. Epidemiology** 
This section provides an overview of the disease's epidemiology, 
including global prevalence and key demographic factors. 
It should discuss the total number of affected individuals worldwide, 
along with variations across regions such as the U.S., EU4+UK, and the Rest of the World (ROW). 
Additionally, it should highlight risk factors such as age, gender, genetic predisposition, 
and environmental triggers. Trends in incidence rates over time should be explored, 
identifying any regional disparities or changes due to improved awareness, diagnostic advancements, 
or emerging treatment options.

### **2. Prevalence and Diagnosis Rates**
| Region  | Total Prevalent Patients | Diagnosed Patients | Diagnosed % of Prevalence |
|---------|-------------------------|---------------------|--------------------------|
| U.S.    | TBD                     | TBD                 | TBD                      |
| EU4+UK  | TBD                     | TBD                 | TBD                      |
| ROW     | TBD                     | TBD                 | TBD                      |

- Analyze diagnosis trends across regions and **factors affecting early detection**.

### **3. Treated Patients**
| Region  | Total Treated Patients | Treated % of Diagnosed |
|---------|-----------------------|------------------------|
| U.S.    | TBD                   | TBD                    |
| EU4+UK  | TBD                   | TBD                    |
| ROW     | TBD                   | TBD                    |

- Explain **treatment accessibility**, including **healthcare policies and drug availability**.

### **4. Disease Stage Segmentation**
| Stage             | % Treated in U.S. | % Treated in EU4+UK | % Treated in ROW |
|------------------|------------------|--------------------|------------------|
| Early-Stage     | TBD              | TBD                | TBD              |
| Moderate-Stage  | TBD              | TBD                | TBD              |
| Severe          | TBD              | TBD                | TBD              |
| End-Stage       | TBD              | TBD                | TBD              |

- Discuss **variations in treatment across disease stages** and **regional healthcare challenges**.

### **5. Forecast Insights**
- Provide **data-driven projections** on prevalence, diagnosis, and treatment trends.
- Highlight **expected growth rates (CAGR)** and innovations in treatment (e.g., biosimilars, biologics, JAK inhibitors).
- Compare future trends across **U.S., EU4+UK, and ROW**.

## **Additional Requirements**
- **Minimum length:** {total_words} words.
- **Formatting style:** {report_format}, using markdown syntax.
- **Language:** {language}.
- Use **in-text citations** formatted as: ([citation](URL)).
- {tone_prompt}

{reference_prompt}

### **Final Instructions**
Write a comprehensive, well-researched report synthesizing all gathered information into a cohesive whole.

**Date:** {datetime.now(timezone.utc).strftime('%B %d, %Y')}
    """



def auto_agent_instructions():
    return """
This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
Agent
The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

examples:
task: "should I invest in apple stocks?"
response: 
{
    "server": "💰 Finance Agent",
    "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
}
task: "could reselling sneakers become profitable?"
response: 
{ 
    "server":  "📈 Business Analyst Agent",
    "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
}
task: "what are the most interesting sites in Tel Aviv?"
response:
{
    "server":  "🌍 Travel Agent",
    "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
}
"""


def generate_summary_prompt(query, data):
    """Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the '
        f"query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual "
        f"information such as numbers, stats, quotes, etc if available. "
    )


################################################################################################

# DETAILED REPORT PROMPTS


def generate_subtopics_prompt() -> str:
    return """
Provided the main topic:

{task}

and research data:

{data}

- Construct a list of subtopics that serve as headers for a detailed analysis report.
- These reports assist in drug development by focusing on one particular disease and conducting deep research to generate different sections of the report.
- These sections are used in drug development analysis.
- These are a possible list of subtopics: {subtopics}.
- There should NOT be any duplicate subtopics and no duplication of headings.
- Limit the number of subtopics to a maximum of {max_subtopics}.
- Finally, order the subtopics by their relevance and logical sequence for a detailed report.

"IMPORTANT!":
- Every subtopic MUST be relevant to the main topic and provided research data ONLY!

{format_instructions}
"""


from datetime import datetime, timezone

def generate_subtopic_report_prompt(
    current_subtopic,
    existing_headers: list,
    relevant_written_contents: list,
    main_topic: str,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
    language: str = "english",
) -> str:
    return f"""
### **Context**
"{context}"


## **Report Structure**
Ensure the report follows this structured approach:

### **1. Epidemiology** 
This section provides an overview of the disease's epidemiology, 
including global prevalence and key demographic factors. 
It should discuss the total number of affected individuals worldwide, 
along with variations across regions such as the U.S., EU4+UK, and the Rest of the World (ROW). 
Additionally, it should highlight risk factors such as age, gender, genetic predisposition, 
and environmental triggers. Trends in incidence rates over time should be explored, 
identifying any regional disparities or changes due to improved awareness, diagnostic advancements, 
or emerging treatment options.

### **2. Prevalence and Diagnosis Rates**
| Region        | Total Prevalent Patients | Diagnosed Patients | Diagnosed % of Prevalence |
|--------------|-------------------------|---------------------|--------------------------|
| U.S.         | TBD                     | TBD                 | TBD                      |
| EU4+UK       | TBD                     | TBD                 | TBD                      |
| ROW          | TBD                     | TBD                 | TBD                      |

- Provide a detailed analysis of diagnosis trends across regions.

### **3. Treated Patients**
| Region        | Total Treated Patients | Treated % of Diagnosed |
|--------------|-----------------------|------------------------|
| U.S.         | TBD                   | TBD                    |
| EU4+UK       | TBD                   | TBD                    |
| ROW          | TBD                   | TBD                    |

- Explain **factors influencing treatment rates** (e.g., healthcare policies, drug availability).

### **4. Disease Stage Segmentation**
| Stage               | % Treated in U.S. | % Treated in EU4+UK | % Treated in ROW |
|---------------------|------------------|--------------------|------------------|
| Early-Stage RA     | TBD              | TBD                | TBD              |
| Moderate-Stage RA  | TBD              | TBD                | TBD              |
| Severe RA          | TBD              | TBD                | TBD              |
| End-Stage RA       | TBD              | TBD                | TBD              |

- Analyze **how treatment varies by disease stage** and **regional healthcare systems**.

### **5. Forecast Insights**
- Provide **data-driven projections** on **prevalence, diagnosis, and treatment trends**.
- Highlight **expected growth rates (CAGR)** and **innovations in treatment** (e.g., biosimilars, biologics, JAK inhibitors).
- Compare future trends across **U.S., EU4+UK, and ROW**.

### **Formatting and Style**
- Use **markdown syntax** with structured headers (`##` for main sections, `###` for subsections).
- **Cite sources** using **markdown hyperlinks** ([example](url)).
- Ensure the **report length is at least {total_words} words**.
- The report must be **in {language}**.
- **Tone:** {tone.value} (Maintain a professional, evidence-based style).
- **Avoid introduction, conclusion, or summary sections**.
- Ensure **zero overlap** with existing content.

**Date:** {datetime.now(timezone.utc).strftime('%B %d, %Y')}
"""




def generate_draft_titles_prompt(
    current_subtopic: str,
    main_topic: str,
    context: str,
    max_subsections: int = 1
) -> str:
    """
    Generate structured draft section title headers for a detailed epidemiological report.

    Args:
        current_subtopic (str): The specific subtopic of the report.
        main_topic (str): The overarching main topic.
        context (str): Background context for generating relevant section headers.
        max_subsections (int): The maximum number of subsections to generate.

    Returns:
        str: A structured prompt guiding the generation of draft section titles.
    """
    return f"""
    ### **Context**
    - **Main Topic:** {main_topic}
    - **Subtopic:** {current_subtopic}
    - **Relevant Background Information:**  
      {context}

    ### **Task**
    You are an **epidemiologist** specializing in **disease trends, risk factors, treatment patterns, and public health strategies**.  
    Your task is to **generate structured draft section headers** for a **detailed epidemiological report** on the subtopic:  
    **{current_subtopic}**, under the broader topic of **{main_topic}**.

    ### **Guidelines**
    2. Each header should be:
        - **Concise, clear, and specific** to the subtopic.
        - **Not too high-level**, but **detailed enough** to capture key epidemiological aspects.
        - **Relevant to the main topic** (avoid unrelated information).
    3. Use **Markdown formatting**:
        - **H3 (###) for section headers** (since H1 and H2 are reserved for the full report).
    4. The sections **must NOT** include:
        - Introduction
        - Epidemiology
        - Prevalence and Diagnosis Rates
        - Treated Patients
        - Disease Stage Segmentation
        - Forecast Insights
        - Conclusion
        - References
    5. Each section should be once only, no repeating
    6. {max_subsections} 

    ### **Example Structure**
    Provide the draft section headers in **Markdown list format**, such as:

    ### Prevalence and Demographics  
    ### Risk Factors and Disease Progression  
    ### Diagnosis and Screening Trends  
    ### Treatment Strategies and Access Disparities  
    ### Public Health Interventions  

    **Now, generate the draft headers for the subtopic: "{current_subtopic}".**
    
    """




def generate_report_introduction(question: str, research_summary: str = "", language: str = "english", report_format: str = "apa") -> str:
    return f"""{research_summary}\n
You are an **epidemiologist with a PhD**, specializing in **disease patterns, risk factors, prevention strategies, and public health implications**. Your expertise allows you to provide **accurate, evidence-based insights** and recommendations. You have an **informative and professional tone of voice** with a **structured and analytical writing style**.

Using the latest available information, **prepare a detailed introduction** for a comprehensive epidemiological report on the topic -- {question}.

### **Introduction Requirements:**
- The introduction should be **succinct, well-structured, and informative**, using markdown syntax.
- As this introduction is part of a larger **epidemiological report**, do **NOT** include other sections (e.g., methods, results, discussion).
- The introduction should start with an **H1 heading** summarizing the broader **public health relevance** of the topic.
- Use **evidence-based insights** and support key statements with **in-text citations** in {report_format.upper()} format.
- In-text citations must be formatted as **markdown hyperlinks** placed at the **end of relevant sentences** (e.g., *([in-text citation](url))*).
- Assume that the current date is **{datetime.now(timezone.utc).strftime('%B %d, %Y')}** if required.
- The output must be in **{language}**.
"""


def generate_report_conclusion(query: str, report_content: str, language: str = "english", report_format: str = "apa") -> str:
    """
    Generate a structured and evidence-based conclusion summarizing the key epidemiological insights of a research report.

    Args:
        query (str): The research task or question.
        report_content (str): The content of the research report.
        language (str): The language in which the conclusion should be written.
        report_format (str): The citation format (default: APA).

    Returns:
        str: A well-structured conclusion summarizing the report’s key epidemiological findings, implications, and recommendations.
    """
    prompt = f"""
    You are an **epidemiologist with a PhD**, specializing in **disease patterns, risk factors, prevention strategies, and public health implications**. 
    Your expertise allows you to provide **data-driven conclusions** that highlight key findings and their impact.

    ### **Task:**
    Based on the **epidemiological report** below and the research task, write a **structured conclusion** that summarizes the key findings and implications:

    **Research Task:** {query}  
    **Epidemiological Report Content:** {report_content}


    ### **Conclusion Requirements:**
    - Recap the **main epidemiological findings** of the report.
    - Highlight **disease prevalence, risk factors, treatment trends, and healthcare policy implications**.
    - Discuss **public health impacts, future projections, and recommendations** for disease management.
    - Structure the conclusion into **2-3 well-organized paragraphs**.
    - If a **"## Conclusion"** section title is missing at the end of the report, **add it** at the top of your conclusion.
    - Use **in-text citations** in {report_format.upper()} format, formatted as **markdown hyperlinks** placed at the **end of relevant sentences** (e.g., *([in-text citation](url))*).
    - Assume the **current date** is **{datetime.now(timezone.utc).strftime('%B %d, %Y')}** if required.
    - The output **must** be in **{language}**.

    Now, generate the **conclusion**:
    """

    return prompt



report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
    ReportType.DeepResearch.value: generate_deep_research_prompt,
}


def get_prompt_by_report_type(report_type):
    prompt_by_type = report_type_mapping.get(report_type)
    default_report_type = ReportType.ResearchReport.value
    if not prompt_by_type:
        warnings.warn(
            f"Invalid report type: {report_type}.\n"
            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
            f"Using default report type: {default_report_type} prompt.",
            UserWarning,
        )
        prompt_by_type = report_type_mapping.get(default_report_type)
    return prompt_by_type

