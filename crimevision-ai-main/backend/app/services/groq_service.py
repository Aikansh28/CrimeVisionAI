"""
groq_service.py - All Groq API interactions for CrimeVision AI
This is the ONLY file that communicates with the Groq API.
"""

import os
import json
import base64
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def _get_client() -> Groq:
    """Create and return a Groq client. Raises error if API key is missing."""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
    return Groq(api_key=GROQ_API_KEY)


def _parse_json_response(text: str) -> dict:
    """
    Try to parse JSON from the LLM response.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Remove markdown code block formatting if present
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    return json.loads(cleaned)


def analyze_image(file_path: str) -> dict:
    """
    Analyze an image using Groq's vision model.
    Reads the image, encodes it in base64, and sends it for forensic analysis.
    Returns a dict with: people, weapons, objects, scene, observations.
    """
    try:
        client = _get_client()

        # Read and base64-encode the image
        with open(file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine the image MIME type
        extension = file_path.lower().split(".")[-1]
        mime_type = "image/jpeg" if extension in ["jpg", "jpeg"] else "image/png"

        # Send to Groq vision model with forensic analysis prompt
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Act as a forensic evidence analyst. Analyze this image and identify: "
                                "people visible, possible weapons, important objects, scene description, "
                                "and observations. Return ONLY valid JSON with keys: "
                                'people (list), weapons (list), objects (list), scene (string), '
                                'observations (list). '
                                'Use careful language like "appears to be", "possible", "visible". '
                                "Never identify anyone as a criminal. Never claim certainty."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )

        # Parse the JSON response from the model
        result_text = response.choices[0].message.content
        return _parse_json_response(result_text)

    except ValueError as e:
        # API key not set
        return {"error": str(e)}
    except json.JSONDecodeError:
        # Model didn't return valid JSON — return the raw text
        return {
            "people": [],
            "weapons": [],
            "objects": [],
            "scene": result_text if 'result_text' in dir() else "Analysis failed",
            "observations": ["Could not parse structured response from AI model."],
        }
    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using Groq's Whisper model.
    Returns the transcript text.
    """
    try:
        client = _get_client()

        # Open and send the audio file to Groq's transcription endpoint
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
            )

        return transcription.text

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: Audio transcription failed: {str(e)}"


def analyze_transcript(transcript: str) -> dict:
    """
    Analyze a transcript using Groq LLM to extract forensic information.
    Returns a dict with: key_events, witness_statements, important_information, summary, transcript.
    """
    try:
        client = _get_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a forensic analyst. Analyze this transcript and extract: "
                        "key_events (list of events with approximate times if mentioned), "
                        "witness_statements (list), important_information (list), "
                        "and summary (string). Return ONLY valid JSON. "
                        'If no time is mentioned, use "Time unavailable". '
                        "Label witness statements clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Analyze this transcript:\n\n{transcript}",
                },
            ],
            max_tokens=1024,
        )

        result_text = response.choices[0].message.content
        result = _parse_json_response(result_text)
        # Always include the full transcript in the result
        result["transcript"] = transcript
        return result

    except ValueError as e:
        return {"error": str(e), "transcript": transcript}
    except json.JSONDecodeError:
        return {
            "key_events": [],
            "witness_statements": [],
            "important_information": [],
            "summary": "Could not parse structured response from AI model.",
            "transcript": transcript,
        }
    except Exception as e:
        return {"error": f"Transcript analysis failed: {str(e)}", "transcript": transcript}


def chat_about_case(evidence_data: list, chat_history: list, user_message: str) -> str:
    """
    Chat with the AI about a case, using evidence as context.
    Returns the assistant's response text.
    """
    try:
        client = _get_client()

        # Build evidence context string from all analyzed evidence
        context = "CASE EVIDENCE:\n\n"
        for i, evidence in enumerate(evidence_data, 1):
            context += f"Evidence #{i}:\n{json.dumps(evidence, indent=2)}\n\n"

        # Build message list with system prompt, history, and user message
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a forensic AI assistant for CrimeVision AI. "
                    "Answer questions ONLY based on the evidence provided. "
                    "If the evidence doesn't contain enough information, say: "
                    '"The available evidence does not provide enough information '
                    'to answer this question." '
                    "Use cautious language. Never make accusations.\n\n"
                    f"{context}"
                ),
            }
        ]

        # Add chat history for context
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["message"]})

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
        )

        return response.choices[0].message.content

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: Chat failed: {str(e)}"


def generate_summary(case_info: dict, evidence_analyses: list) -> dict:
    """
    Generate a forensic case summary from all evidence.
    Returns a dict with: overview, key_observations, evidence_summary, uncertainties.
    """
    try:
        client = _get_client()

        # Build the prompt with case info and all evidence
        evidence_text = ""
        for i, analysis in enumerate(evidence_analyses, 1):
            evidence_text += f"Evidence #{i}:\n{json.dumps(analysis, indent=2)}\n\n"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a forensic case summary with: "
                        "overview (string), key_observations (list), "
                        "evidence_summary (list), uncertainties (list). "
                        "Use cautious language. Return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Case Information:\n{json.dumps(case_info, indent=2)}\n\n"
                        f"Evidence Analyses:\n{evidence_text}"
                    ),
                },
            ],
            max_tokens=1024,
        )

        result_text = response.choices[0].message.content
        return _parse_json_response(result_text)

    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {
            "overview": "Could not parse structured response from AI model.",
            "key_observations": [],
            "evidence_summary": [],
            "uncertainties": ["AI response could not be parsed."],
        }
    except Exception as e:
        return {"error": f"Summary generation failed: {str(e)}"}
