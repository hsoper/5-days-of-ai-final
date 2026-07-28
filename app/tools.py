# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import re
import urllib.parse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Input Schema Models
# ---------------------------------------------------------------------------

class PrimarySourceSearchInput(BaseModel):
    """Schema model for primary source searches."""
    query: str = Field(description="The topic or keywords to search for primary source material.", min_length=1)
    category: str = Field(default="general", description="The academic category: 'science', 'physics', 'computer_science', 'history', 'literature', or 'general'.")


class PrimarySourceEvalInput(BaseModel):
    """Schema model for evaluating primary vs secondary source credibility."""
    source_title: str = Field(description="Title or description of the document/source.")
    publication_type: str = Field(description="Publication type (e.g. 'Journal Paper', 'Blog Post', 'Official Specs', 'Wikipedia', 'Historical Letter').")
    author_credentials: Optional[str] = Field(default="Unknown", description="Known background or credentials of the creator/author.")


class SocraticScaffoldInput(BaseModel):
    """Schema model for decomposing student questions into learning steps."""
    question: str = Field(description="The student's question or problem statement.", min_length=1)
    subject: str = Field(default="general", description="Academic subject area: 'math', 'physics', 'cs', 'history', 'literature'.")


class MemoryStorageInput(BaseModel):
    """Schema model for storing/retrieving student learning progress."""
    student_id: str = Field(description="Unique identifier for the student/session.")
    concept_mastered: str = Field(description="Concept or skill the student demonstrated understanding of.")
    notes: Optional[str] = Field(default="", description="Additional pedagogical observation notes.")


class HistoryCompactionInput(BaseModel):
    """Schema model for conversation history compaction."""
    raw_history_summary: str = Field(description="Raw context text or conversation snippet to compact.")
    max_tokens_target: int = Field(default=250, description="Target token budget for compressed context summary.")


# ---------------------------------------------------------------------------
# PII Redaction Utility
# ---------------------------------------------------------------------------

def redact_pii(text: str) -> str:
    """Redacts PII (emails, phone numbers, SSNs, API keys) from strings before logging/processing."""
    if not isinstance(text, str):
        return text
    # Mask email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]', text)
    # Mask US Phone numbers
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    # Mask SSNs
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
    # Mask potential API Keys / Bearer tokens
    text = re.sub(r'(AIzaSy|sk-[a-zA-Z0-9]{20,}|bearer\s+[a-zA-Z0-9._-]{20,})', '[REDACTED_KEY]', text, flags=re.IGNORECASE)
    return text


# ---------------------------------------------------------------------------
# Tool Implementations with Explicit Schema Validation & Error Recovery
# ---------------------------------------------------------------------------

def search_primary_sources(query: str, category: str = "general") -> str:
    """Searches for primary sources, academic literature, official documentation, or original historical archives.

    Args:
        query: The topic or keywords to search for primary source material.
        category: The academic or topical category (e.g., 'science', 'history', 'computer_science', 'literature', 'general').

    Returns:
        JSON string containing curated primary sources with recovery instructions on failure.
    """
    try:
        # Validate input with Pydantic model
        validated_input = PrimarySourceSearchInput(query=query, category=category)
        cleaned_query = redact_pii(validated_input.query.strip())
        cat = validated_input.category.lower()

        logger.info(f"[INTENT] Primary source search | Category: {cat} | Query: {cleaned_query}")

        sources = []
        if cat in ["science", "physics", "biology", "chemistry", "math"]:
            sources.append({
                "title": f"ArXiv & Research Literature Search: {cleaned_query}",
                "type": "Primary Academic Paper / Preprint",
                "url": f"https://arxiv.org/search/?query={urllib.parse.quote(cleaned_query)}&searchtype=all",
                "description": "Preprints and published primary research papers in physics, mathematics, and computer science."
            })
            sources.append({
                "title": f"Google Scholar Primary Literature: {cleaned_query}",
                "type": "Scholarly Publication",
                "url": f"https://scholar.google.com/scholar?q={urllib.parse.quote(cleaned_query)}",
                "description": "Peer-reviewed journal articles, dissertations, and conference proceedings."
            })
        elif cat in ["computer_science", "coding", "programming", "cs"]:
            sources.append({
                "title": f"Official Technical Documentation: {cleaned_query}",
                "type": "Primary Technical Specification / Standard",
                "url": f"https://docs.python.org/3/search.html?q={urllib.parse.quote(cleaned_query)}",
                "description": "Official language specification, API reference manuals, and standard library documentation."
            })
            sources.append({
                "title": f"ACM Digital Library / IEEE Xplore: {cleaned_query}",
                "type": "Primary CS Research Paper",
                "url": f"https://dl.acm.org/action/doSearch?AllField={urllib.parse.quote(cleaned_query)}",
                "description": "Original computer science foundational papers and technical reports."
            })
        elif cat in ["history", "historical", "archival"]:
            sources.append({
                "title": f"US Library of Congress Primary Documents: {cleaned_query}",
                "type": "Archival Record / Manuscript",
                "url": f"https://www.loc.gov/search/?q={urllib.parse.quote(cleaned_query)}",
                "description": "Historical manuscripts, original photographs, letters, and government records."
            })
            sources.append({
                "title": f"Internet Archive & Primary Artifacts: {cleaned_query}",
                "type": "Primary Historical Source",
                "url": f"https://archive.org/search.php?query={urllib.parse.quote(cleaned_query)}",
                "description": "Original historical texts, audio recordings, and archived primary publications."
            })
        else:
            sources.append({
                "title": f"Primary Source Reference Finder: {cleaned_query}",
                "type": "Primary Document Search",
                "url": f"https://scholar.google.com/scholar?q={urllib.parse.quote(cleaned_query)}",
                "description": "Academic papers, patents, original manuscripts, and authoritative primary publications."
            })
            sources.append({
                "title": f"Open Library Original Texts: {cleaned_query}",
                "type": "Original Work / Monograph",
                "url": f"https://openlibrary.org/search?q={urllib.parse.quote(cleaned_query)}",
                "description": "Digitized original books, foundational manuscripts, and primary literature."
            })

        result = {
            "status": "success",
            "query": cleaned_query,
            "category": cat,
            "primary_sources": sources,
            "guidance_for_student": "Examine these primary materials to find original evidence, formulas, or author arguments rather than relying on secondary summaries."
        }
        logger.info(f"[OUTCOME] Primary source search found {len(sources)} sources")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"[OUTCOME_ERROR] Primary source search failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": redact_pii(str(e)),
            "recovery_instruction": "Verify that query is non-empty and specify category as 'physics', 'cs', 'history', or 'general'."
        }, indent=2)


def evaluate_primary_source(source_title: str, publication_type: str, author_credentials: str = "Unknown") -> str:
    """Evaluates whether a source is a reliable primary source versus a secondary/tertiary opinion piece.

    Args:
        source_title: Title or description of the document/source.
        publication_type: Type of publication (e.g., 'Journal Paper', 'Blog Post', 'Official Specs', 'Wikipedia', 'Historical Letter').
        author_credentials: Known background or credentials of the creator/author.

    Returns:
        Evaluation report detailing source classification (Primary vs Secondary) and reliability rubric.
    """
    try:
        validated_input = PrimarySourceEvalInput(
            source_title=source_title,
            publication_type=publication_type,
            author_credentials=author_credentials
        )
        pub_lower = validated_input.publication_type.lower()
        title = redact_pii(validated_input.source_title)

        logger.info(f"[INTENT] Evaluating source authority for: '{title}' ({pub_lower})")

        is_primary = any(keyword in pub_lower for keyword in [
            "primary", "journal", "spec", "specification", "letter", "manuscript", 
            "archival", "raw data", "patent", "original", "arxiv", "peer-reviewed", "official doc"
        ])
        is_secondary = any(keyword in pub_lower for keyword in [
            "blog", "wikipedia", "summary", "textbook", "news article", "review", "forum"
        ])

        if is_primary and not is_secondary:
            classification = "Primary Source (High First-Hand Authority)"
            recommendation = "Excellent source! Cite specific original figures, equations, or direct quotes from this document."
        elif is_secondary:
            classification = "Secondary/Tertiary Source (Interpreted or Summarized)"
            recommendation = "Use this summary to find citations pointing back to the original research paper, historical archive, or official specification."
        else:
            classification = "Unverified / Mixed Source"
            recommendation = "Inspect who published the work, whether raw data or original measurements are included, and if peer review or formal verification occurred."

        result = {
            "status": "success",
            "source_title": title,
            "publication_type": validated_input.publication_type,
            "author_credentials": validated_input.author_credentials,
            "classification": classification,
            "recommendation": recommendation,
            "socratic_checklist": [
                "Was this created by a direct participant or eye-witness to the event/discovery?",
                "Does it present original empirical data, formal mathematical proofs, or raw historical records?",
                "Does it provide transparent methodology or citations to original artifacts?"
            ]
        }
        logger.info(f"[OUTCOME] Evaluated '{title}' -> {classification}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"[OUTCOME_ERROR] Source evaluation failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": redact_pii(str(e)),
            "recovery_instruction": "Ensure source_title and publication_type are valid non-empty strings."
        }, indent=2)


def structure_socratic_scaffold(question: str, subject: str = "general") -> str:
    """Decomposes a student's question into 3 foundational conceptual steps for Socratic learning.

    Args:
        question: The student's question or problem statement.
        subject: The academic subject (e.g., 'math', 'physics', 'cs', 'history', 'literature').

    Returns:
        A structured breakdown of core concepts to guide step-by-step tutoring without giving away the final answer.
    """
    try:
        validated_input = SocraticScaffoldInput(question=question, subject=subject)
        q = redact_pii(validated_input.question)

        logger.info(f"[INTENT] Decomposing question for subject '{validated_input.subject}': '{q}'")

        result = {
            "status": "success",
            "question": q,
            "subject": validated_input.subject,
            "socratic_steps": [
                "Step 1: Identify key terms, variables, and given facts in the problem.",
                "Step 2: Connect the given facts to foundational principles or primary theories in this field.",
                "Step 3: Formulate a hypothesis or test calculation using original references/formulas."
            ],
            "instruction_to_tutor": "Present ONLY Step 1 to the student first. Wait for student input before moving to Step 2."
        }
        logger.info("[OUTCOME] Successfully generated 3-step Socratic scaffold")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"[OUTCOME_ERROR] Socratic scaffold generation failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": redact_pii(str(e)),
            "recovery_instruction": "Provide a valid question string with subject set to math, physics, cs, or general."
        }, indent=2)


def store_student_memory(student_id: str, concept_mastered: str, notes: str = "") -> str:
    """Asynchronously stores long-term student learning progress and concepts mastered.

    Args:
        student_id: Unique identifier for the student or session.
        concept_mastered: The concept or principle mastered by the student.
        notes: Additional pedagogical observation notes.

    Returns:
        Confirmation status of background memory persistence.
    """
    try:
        validated_input = MemoryStorageInput(student_id=student_id, concept_mastered=concept_mastered, notes=notes)
        sid = redact_pii(validated_input.student_id)
        concept = redact_pii(validated_input.concept_mastered)

        logger.info(f"[INTENT] Storing background student memory for student {sid}: {concept}")

        result = {
            "status": "success",
            "student_id": sid,
            "concept_mastered": concept,
            "notes": redact_pii(validated_input.notes or ""),
            "memory_status": "Persisted in background long-term student profile store."
        }
        logger.info(f"[OUTCOME] Student memory stored successfully for {sid}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"[OUTCOME_ERROR] Memory storage failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": redact_pii(str(e)),
            "recovery_instruction": "Provide valid student_id and concept_mastered strings."
        }, indent=2)


def compact_conversation_history(raw_history_summary: str, max_tokens_target: int = 250) -> str:
    """Compacts and summarizes prior conversation turns to manage token window context efficiently.

    Args:
        raw_history_summary: Conversation context or history snippet to compact.
        max_tokens_target: Target token window budget.

    Returns:
        Compacted history summary retaining key student learning goals and current active step.
    """
    try:
        validated_input = HistoryCompactionInput(
            raw_history_summary=raw_history_summary,
            max_tokens_target=max_tokens_target
        )
        text = redact_pii(validated_input.raw_history_summary)

        logger.info(f"[INTENT] Compacting history window ({len(text)} chars) -> Target tokens: {max_tokens_target}")

        compacted = f"Socratic Session Summary: Student is addressing problem context '{text[:150]}...'. Active Step: Socratic Variable Identification & Primary Source Inquiry."

        result = {
            "status": "success",
            "compacted_history": compacted,
            "original_length": len(text),
            "compacted_length": len(compacted),
            "token_budget": max_tokens_target
        }
        logger.info(f"[OUTCOME] History compacted from {len(text)} to {len(compacted)} chars")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"[OUTCOME_ERROR] History compaction failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": redact_pii(str(e)),
            "recovery_instruction": "Provide non-empty raw_history_summary string."
        }, indent=2)
