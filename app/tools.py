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
import urllib.parse
import urllib.request
from typing import Dict, Any


def search_primary_sources(query: str, category: str = "general") -> str:
    """Searches for primary sources, academic literature, official documentation, or original historical archives.

    Args:
        query: The topic or keywords to search for primary source material.
        category: The academic or topical category (e.g., 'science', 'history', 'computer_science', 'literature', 'general').

    Returns:
        A JSON string containing a list of curated primary sources, official docs, or research references.
    """
    cleaned_query = query.strip()
    
    # Primary source search logic with category-tailored recommendations
    sources = []
    
    if category.lower() in ["science", "physics", "biology", "chemistry"]:
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
    elif category.lower() in ["computer_science", "coding", "programming"]:
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
    elif category.lower() in ["history", "historical", "archival"]:
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

    return json.dumps({
        "status": "success",
        "query": cleaned_query,
        "category": category,
        "primary_sources": sources,
        "guidance_for_student": "Examine these primary materials to find original evidence, formulas, or author arguments rather than relying on secondary summaries."
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
    pub_lower = publication_type.lower()
    
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

    return json.dumps({
        "source_title": source_title,
        "publication_type": publication_type,
        "author_credentials": author_credentials,
        "classification": classification,
        "recommendation": recommendation,
        "socratic_checklist": [
            "Was this created by a direct participant or eye-witness to the event/discovery?",
            "Does it present original empirical data, formal mathematical proofs, or raw historical records?",
            "Does it provide transparent methodology or citations to original artifacts?"
        ]
    }, indent=2)


def structure_socratic_scaffold(question: str, subject: str = "general") -> str:
    """Decomposes a student's question into 3 foundational conceptual steps for Socratic learning.

    Args:
        question: The student's question or problem statement.
        subject: The academic subject (e.g., 'math', 'physics', 'cs', 'history', 'literature').

    Returns:
        A structured breakdown of core concepts to guide step-by-step tutoring without giving away the final answer.
    """
    return json.dumps({
        "question": question,
        "subject": subject,
        "socratic_steps": [
            "Step 1: Identify key terms, variables, and given facts in the problem.",
            "Step 2: Connect the given facts to foundational principles or primary theories in this field.",
            "Step 3: Formulate a hypothesis or test calculation using original references/formulas."
        ],
        "instruction_to_tutor": "Present ONLY Step 1 to the student first. Wait for student input before moving to Step 2."
    }, indent=2)
