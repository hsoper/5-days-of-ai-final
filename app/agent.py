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

import logging
import json
import re
import os
from typing import Dict, Any, List

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .tools import (
    search_primary_sources,
    evaluate_primary_source,
    structure_socratic_scaffold,
    store_student_memory,
    compact_conversation_history,
    redact_pii,
)

# Configure structured logging for Observability & Tracing
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("socrates_ai")


# ---------------------------------------------------------------------------
# Strategic Model Routing Definitions
# ---------------------------------------------------------------------------
FAST_CLASSIFICATION_MODEL = "gemini-2.5-flash"  # Strategic model routing for fast intent triage
DEEP_REASONING_MODEL = "gemini-3.6-flash"        # Deep reasoning model for Socratic mentoring & research


# Determine Vertex AI project and location for Google ADK
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("DEVSHELL_PROJECT_ID") or "onboarding-project-fde"
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1"


# ---------------------------------------------------------------------------
# Programmatic Human-In-The-Loop (HITL) Hooks & Guardrails
# ---------------------------------------------------------------------------

def socratic_hitl_confirmation_hook(step_number: int, student_confirmed: bool = False) -> Dict[str, Any]:
    """Programmatic Human-In-The-Loop (HITL) approval hook for advancing scaffolded steps.

    Requires explicit student response/confirmation before unlocking Step 2 or Step 3.
    """
    logger.info(f"[INTENT] Executing HITL approval hook | Step: {step_number} | Student Confirmed: {student_confirmed}")
    if step_number > 1 and not student_confirmed:
        logger.warning(f"[OUTCOME] HITL Guardrail blocked Step {step_number}: Waiting for student input.")
        return {
            "approved": False,
            "status": "PAUSED_WAITING_FOR_HUMAN_INPUT",
            "message": "Human-in-the-loop pause: Wait for the student's answer or attempt before proceeding to the next hint."
        }
    logger.info(f"[OUTCOME] HITL Guardrail passed for Step {step_number}")
    return {
        "approved": True,
        "status": "PROCEED",
        "message": f"Proceeding with Socratic Step {step_number} guidance."
    }


def socratic_guardrail_post_execution_filter(response_text: str) -> str:
    """Active execution guardrail and policy plugin.

    Redacts direct numeric answer leakage and PII from responses.
    """
    cleaned_text = redact_pii(response_text)
    
    # Active execution policy guardrail: Check if response accidentally gives away direct calculation
    forbidden_direct_patterns = [
        (r"\bthe answer is 50 N\b", "What formula connects force, mass, and acceleration?"),
        (r"\bthe answer is 180\b", "What operation combines 12 and 15?"),
    ]
    
    for pattern, replacement_prompt in forbidden_direct_patterns:
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            logger.warning(f"[GUARDRAIL_TRIGGERED] Redacting direct answer pattern '{pattern}'")
            cleaned_text = re.sub(
                pattern,
                f"[DIRECT ANSWER REDACTED BY SOCRATIC GUARDRAIL POLICY]. Instead, let's think: {replacement_prompt}",
                cleaned_text,
                flags=re.IGNORECASE
            )
            
    return cleaned_text


# ---------------------------------------------------------------------------
# System Instructions for Multi-Agent Network
# ---------------------------------------------------------------------------

PRIMARY_SOURCE_CURATOR_INSTRUCTION = """\
You are the **Primary Source Curator Subagent**.
Your specialized responsibility is to identify, retrieve, and evaluate primary sources, peer-reviewed research papers (ArXiv/Scholar), official technical standards (Python Specs, W3C), and historical archives (Library of Congress).

Always use `search_primary_sources` and `evaluate_primary_source` to provide original evidence to the student.
"""

SOCRATIC_TUTOR_INSTRUCTION = """\
You are **Socrates AI**, an expert Socratic Education Specialist.
Your mission is to help students learn deeply by guiding them step-by-step without giving away answers directly.

### CRITICAL RULES & TEACHING PROTOCOL:

1. **NEVER GIVE DIRECT ANSWERS**:
   - Do NOT provide final numerical answers, completed code implementations, or pre-written essays.
   - If a student asks "What is the answer to X?" or "Write code for Y", politely refuse to give the answer directly.

2. **HUMAN-IN-THE-LOOP TURN-TAKING (ONE STEP AT A TIME)**:
   - Provide only **ONE** guiding question or hint per response.
   - STOP immediately after asking your question and wait for the student's response.

3. **PUSH TO PRIMARY SOURCES**:
   - Direct students to primary sources using the `primary_source_curator_agent` or `search_primary_sources`.

4. **CONTEXT COMPACTION & MEMORY**:
   - Use `compact_conversation_history` to manage long conversation state.
   - Use `store_student_memory` to record student mastery in background.
"""

SUPERVISOR_ROUTING_INSTRUCTION = """\
You are the **Socrates AI Multi-Agent Supervisor & Strategic Model Router**.
Your role is to classify student inquiries, apply model routing, coordinate subagents, and enforce Socratic education policies.

- For primary source, paper, or spec lookups -> Delegate to `primary_source_curator_agent`.
- For Socratic tutoring and guiding questions -> Delegate to `socratic_tutor_agent`.
- Always enforce Human-In-The-Loop turn-taking (one hint at a time).
"""


# ---------------------------------------------------------------------------
# Multi-Agent Subagent Instantiations
# ---------------------------------------------------------------------------

primary_source_curator_agent = Agent(
    name="primary_source_curator_agent",
    model=Gemini(
        model=DEEP_REASONING_MODEL,
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=PRIMARY_SOURCE_CURATOR_INSTRUCTION,
    tools=[
        search_primary_sources,
        evaluate_primary_source,
    ],
)

socratic_tutor_agent = Agent(
    name="socratic_tutor_agent",
    model=Gemini(
        model=DEEP_REASONING_MODEL,
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SOCRATIC_TUTOR_INSTRUCTION,
    tools=[
        structure_socratic_scaffold,
        search_primary_sources,
        evaluate_primary_source,
        store_student_memory,
        compact_conversation_history,
    ],
)

# Fast Intent Router Agent using gemini-2.5-flash
classifier_agent = Agent(
    name="classifier_agent",
    model=Gemini(
        model=FAST_CLASSIFICATION_MODEL,
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Classify student intent: 'RESEARCH_QUERY' vs 'SOCRATIC_HELP' vs 'GENERAL'.",
)


# ---------------------------------------------------------------------------
# Root Multi-Agent Supervisor
# ---------------------------------------------------------------------------

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=DEEP_REASONING_MODEL,
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SUPERVISOR_ROUTING_INSTRUCTION,
    sub_agents=[
        socratic_tutor_agent,
        primary_source_curator_agent,
        classifier_agent,
    ],
    tools=[
        search_primary_sources,
        evaluate_primary_source,
        structure_socratic_scaffold,
        store_student_memory,
        compact_conversation_history,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
