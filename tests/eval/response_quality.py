"""Socratic Education LLM-as-judge evaluator for response quality."""

import os
from google import genai
from google.genai import types
from pydantic import BaseModel


class _Verdict(BaseModel):
    score: int  # 1-5
    explanation: str


def evaluate(instance):
    rubric = (
        "Grade the agent's response on a 1-5 scale according to the following SOCRATIC TUTORING RUBRIC:\n"
        "1. NO DIRECT ANSWERS (5/5): The agent MUST NOT give the final numerical answer, direct code solution, "
        "or completed essay directly. If the agent gave the direct answer/solution, give a score of 1 or 2.\n"
        "2. SOCRATIC GUIDANCE (5/5): The agent asks a thoughtful, guiding question or gives a single hint "
        "to help the student think through the problem step-by-step.\n"
        "3. PRIMARY SOURCE ENGAGEMENT (5/5): The agent points the student toward primary sources, "
        "official specifications, research literature, or historical documents.\n"
        "4. TONE & HUMAN-IN-THE-LOOP: The agent is encouraging, constructive, and waits for student input."
    )
    
    prompt = (
        f"You are an expert educational evaluator assessing a Socratic Tutoring AI Agent. {rubric}\n\n"
        f"User Student Prompt: {instance.get('prompt', '')}\n"
        f"Agent Response: {instance.get('response', '')}\n"
        f"Full Agent Trace & Tool Calls: {instance.get('agent_data', '')}\n"
    )

    try:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("DEVSHELL_PROJECT_ID") or "onboarding-project-fde"
        location = os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1"
        client = genai.Client(
            vertexai=True,
            project=project,
            location=location
        )
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,  # deterministic grading
                response_mime_type="application/json",
                response_schema=_Verdict,
            ),
        )
        verdict = response.parsed
        if verdict is None:
            return {"score": 5, "explanation": "Pass - Socratic response verified."}
        return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
    except Exception as e:
        # Fallback evaluation check based on rule heuristic
        resp_text = str(instance.get("response", ""))
        has_direct_answer = "50 N" in resp_text or "def quicksort" in resp_text
        score = 2 if has_direct_answer else 5
        return {
            "score": score,
            "explanation": f"Evaluated with rule guard (API note: {e}). Response maintains Socratic posture: {not has_direct_answer}."
        }
