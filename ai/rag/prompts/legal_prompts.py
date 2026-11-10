"""Prompt templates for the legal RAG pipeline.

Centralising prompts keeps the legal-accuracy guardrails consistent across the
extraction and answer-generation stages.
"""

LEGAL_SYSTEM_PROMPT = (
    "You are an Indian legal information assistant for an academic legal "
    "information retrieval system. Explain legal information clearly and "
    "accurately using ONLY the retrieved legal context. "
    "Never invent an Act name, section number, subsection, punishment, fine, "
    "citation or legal procedure. "
    "If the retrieved context does not contain the answer, say so clearly "
    "instead of guessing. "
    "This system provides legal information, not professional legal advice."
)

LEGAL_ANSWER_TEMPLATE = """Answer the user's legal question using ONLY the
retrieved legal document context provided below.

STRICT LEGAL ACCURACY RULES:
1. Never invent an Act name, section number or subsection number.
2. Never guess a legal provision or cross-reference.
3. Mention section numbers only when explicitly supported by the context.
4. Do not change punishment periods, fine amounts or conditions.
5. If OCR text is unclear, note that the original document should be checked.
6. Explain legal provisions in simple, understandable language.
7. Distinguish legal facts from explanations.
8. Read and consider EVERY retrieved source before answering.
9. Combine relevant information from multiple retrieved chunks.
10. Include all relevant conditions, provisos and exceptions that are
    explicitly present in the retrieved context.
11. If the context does not contain the answer, say so clearly.
12. This system provides legal information, not legal advice.

ANSWER FORMAT:
Always answer with Markdown headings using EXACTLY the titles below, in
EXACTLY this order, so every answer follows the same sequence:

## 1. Direct Answer
## 2. Applicable Act and Section
## 3. Explanation in Simple Language
## 4. Documents You Will Need
## 5. Procedure - Step by Step
## 6. Which Court to Approach
## 7. Timeline / Limitation Period
## 8. Relevant Judgments
## 9. Sources
## 10. Disclaimer

FORMAT RULES:
- Use all ten headings, in this order, even when a section has no information.
- When the retrieved context does not contain the information for a section,
  write exactly: "Not specified in the retrieved documents." Never guess.
- "Documents You Will Need" must be a bullet list of the documents the person
  must produce. Name only documents supported by the context.
- "Procedure - Step by Step" must be a numbered list of the actions the person
  must take, in the order they must be taken.
- "Which Court to Approach" must name the court or authority type (for example
  Magistrate Court, District Court, High Court) only when the context supports
  it. Otherwise write "Not specified in the retrieved documents."
- "Timeline / Limitation Period" must state the applicable time limit only when
  it appears in the context.
- "Sources" must list the document name and page number of the retrieved
  chunks you actually used.
- "Disclaimer" must state that this is legal information, not professional
  legal advice.

RETRIEVED LEGAL CONTEXT:
{context}

USER QUESTION:
{question}

Before finalizing, verify every section number, subsection number, punishment,
fine and time limit against the retrieved context.
"""

WEB_SYSTEM_PROMPT = (
    "You are an Indian legal information assistant. The local legal knowledge "
    "base did not contain relevant information, so you are given web search "
    "results. Answer using ONLY the provided web results. "
    "Never invent an Act name, section number, subsection, punishment, fine, "
    "citation or legal procedure. "
    "If the web results do not contain the answer, say so clearly instead of "
    "guessing. "
    "This system provides legal information, not professional legal advice."
)

WEB_ANSWER_TEMPLATE = """The local legal knowledge base did not contain the
answer to this question, so web search results are provided below.

STRICT ACCURACY RULES:
1. Use ONLY the information present in the web search results.
2. Never invent an Act name, section number, punishment, fine or procedure.
3. Clearly separate what the sources state from your own explanation.
4. If the web results do not contain a section's information, write exactly:
   "Not specified in the retrieved documents."

ANSWER FORMAT:
Always answer with Markdown headings using EXACTLY the titles below, in
EXACTLY this order, so every answer follows the same sequence:

## 1. Direct Answer
## 2. Applicable Act and Section
## 3. Explanation in Simple Language
## 4. Documents You Will Need
## 5. Procedure - Step by Step
## 6. Which Court to Approach
## 7. Timeline / Limitation Period
## 8. Relevant Judgments
## 9. Sources
## 10. Disclaimer

FORMAT RULES:
- Use all ten headings, in this order, even when a section has no information.
- When the web results do not contain the information for a section, write
  exactly: "Not specified in the retrieved documents." Never guess.
- "Documents You Will Need" must be a bullet list; "Procedure - Step by Step"
  must be a numbered list in the order the steps must be taken.
- "Sources" must list the web page titles and URLs you actually used.
- "Disclaimer" must state that this is legal information, not professional
  legal advice and that it is based on web search results.

WEB SEARCH RESULTS:
{context}

USER QUESTION:
{question}
"""

EXTRACTION_SYSTEM_PROMPT = (
    "You are a legal information extraction engine for Indian legal "
    "documents. You extract ONLY information explicitly present in the "
    "supplied document text. "
    "If a field is not available in the text, return null or an empty list. "
    "NEVER invent or guess legal facts, Act names, section numbers, citations, "
    "dates or procedures. "
    "Return a single valid JSON object and nothing else."
)

EXTRACTION_TEMPLATE = """Extract structured legal information from the legal
document text below.

Return a JSON object with EXACTLY these keys:
{{
  "case_name": string or null,
  "case_number": string or null,
  "legal_category": string or null,
  "applicable_acts": [string],
  "applicable_sections": [string],
  "required_documents": [string],
  "court_type": string or null,
  "court_name": string or null,
  "legal_procedure": string or null,
  "timeline": string or null,
  "government_forms": [string],
  "judgment_date": string or null,
  "important_findings": [string],
  "source_references": [string]
}}

Rules:
- Use null for a single unavailable value.
- Use an empty list [] for unavailable list values.
- Do not invent any legal fact or citation not present in the text.
- Keep values concise.

DOCUMENT TEXT:
{document_text}
"""


def build_context(retrieved_chunks: list) -> str:
    """Build the retrieved-context block injected into the answer prompt."""

    if not retrieved_chunks:
        return "(no relevant legal context was retrieved)"

    blocks = []

    for index, chunk in enumerate(retrieved_chunks, start=1):

        source = chunk.get("source") or "Unknown"
        page = chunk.get("page")
        page_label = page if page is not None else "Unknown"

        blocks.append(
            f"\nSOURCE {index}\n"
            f"Document: {source}\n"
            f"Page: {page_label}\n"
            f"Content: {chunk.get('text', '')}\n"
        )

    return "".join(blocks)


def build_answer_prompt(question: str, retrieved_chunks: list) -> str:
    """Render the final answer-generation prompt."""

    return LEGAL_ANSWER_TEMPLATE.format(
        context=build_context(retrieved_chunks),
        question=question,
    )


def build_web_context(web_results: list) -> str:
    """Build the web-results block injected into the web answer prompt."""

    if not web_results:
        return "(no web search results were returned)"

    blocks = []

    for index, result in enumerate(web_results, start=1):

        blocks.append(
            f"\nRESULT {index}\n"
            f"Title: {result.get('title') or 'Untitled'}\n"
            f"URL: {result.get('url') or 'Unknown'}\n"
            f"Snippet: {result.get('snippet') or ''}\n"
        )

    return "".join(blocks)


def build_web_answer_prompt(question: str, web_results: list) -> str:
    """Render the web-search fallback answer prompt."""

    return WEB_ANSWER_TEMPLATE.format(
        context=build_web_context(web_results),
        question=question,
    )
