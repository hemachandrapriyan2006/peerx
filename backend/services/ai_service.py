"""
PeerX AI Service
Handles all communication with the Gemini LLM.
Includes mock mode for demo/testing when API key is unavailable.
"""

import json
import re
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini client
_client = None


def _get_client():
    """Get or create Gemini client."""
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Running in MOCK mode.")
            return None
        from google import genai
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def is_mock_mode() -> bool:
    """Check if running in mock/demo mode."""
    return not settings.GEMINI_API_KEY


def generate(system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
    """
    Generate content using Gemini LLM.

    Args:
        system_prompt: System instructions for the agent role
        user_prompt: The actual user/context prompt
        expect_json: If True, attempt to parse JSON from response

    Returns:
        The generated text response
    """
    if is_mock_mode():
        return _get_mock_response(system_prompt, user_prompt, expect_json)

    models_to_try = [settings.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
    client = _get_client()
    if not client:
        return _get_mock_response(system_prompt, user_prompt, expect_json)

    from google.genai import types

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"Gemini API attempt with model '{model_name}' failed: {e}")
            continue

    logger.warning("All Gemini API models failed. Falling back to mock generator.")
    return _get_mock_response(system_prompt, user_prompt, expect_json)



def generate_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Generate structured JSON from the LLM.
    Includes parsing and retry logic.
    """
    if is_mock_mode():
        mock_text = _get_mock_response(system_prompt, user_prompt, expect_json=True)
        return _parse_json_safe(mock_text)

    json_system = system_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no extra text."
    models_to_try = [settings.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]

    for model_name in models_to_try:
        try:
            from google.genai import types

            client = _get_client()
            if not client:
                break

            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=json_system,
                    temperature=0.5,
                    max_output_tokens=2000,
                    response_mime_type="application/json",
                )
            )

            result = _parse_json_safe(response.text)
            if result:
                return result

            # Retry without response_mime_type
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=json_system,
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )

            result = _parse_json_safe(response.text)
            if result:
                return result

        except Exception as e:
            logger.warning(f"Gemini API attempt with model '{model_name}' failed: {e}")
            continue

    logger.warning("Failed to parse JSON from LLM after trying models. Falling back to dynamic mock generator.")
    mock_text = _get_mock_response(system_prompt, user_prompt, expect_json=True)
    return _parse_json_safe(mock_text) or {"message": "Fallback content"}


def _parse_json_safe(text: str) -> Optional[dict]:
    """Safely parse JSON from LLM output, handling markdown code fences."""
    if not text:
        return None

    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code fences
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding JSON object in text
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


# ── Mock Responses (Demo Mode) ─────────────────────────────

def _extract_topic_and_subject(system_prompt: str, user_prompt: str):
    combined = system_prompt + "\n" + user_prompt

    # Look for topic patterns in prompt strings
    m_topic = re.search(r"following topic:\s*([^\n\.\?]+)", combined, re.IGNORECASE)
    if not m_topic:
        m_topic = re.search(r"concept of ['\"]([^'\"]+)['\"]", combined, re.IGNORECASE)
    if not m_topic:
        m_topic = re.search(r"perspective on ['\"]([^'\"]+)['\"]", combined, re.IGNORECASE)
    if not m_topic:
        m_topic = re.search(r"understanding of ['\"]([^'\"]+)['\"]", combined, re.IGNORECASE)
    if not m_topic:
        m_topic = re.search(r"about ['\"]([^'\"]+)['\"]", combined, re.IGNORECASE)
    if not m_topic:
        m_topic = re.search(r'"topic":\s*"([^"]+)"', combined)

    topic = m_topic.group(1).strip() if m_topic else "General Topic"

    m_subject = re.search(r"in ['\"]?([A-Za-z0-9\s]+)['\"]? for a", combined, re.IGNORECASE)
    if not m_subject:
        m_subject = re.search(r"in ['\"]?([A-Za-z0-9\s]+)['\"]? at a", combined, re.IGNORECASE)
    if not m_subject:
        m_subject = re.search(r'"subject":\s*"([^"]+)"', combined)
    subject = m_subject.group(1).strip() if m_subject else "General"

    return topic, subject


def _get_mock_response(system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
    """Return dynamic mock responses for demo/testing mode."""
    prompt_lower = system_prompt.lower()
    topic, subject = _extract_topic_and_subject(system_prompt, user_prompt)
    topic_lower = topic.lower()

    if "name: challenger ai" in prompt_lower or "you are the challenger ai" in prompt_lower:
        if "python function" in topic_lower:
            q = "What is the difference between positional and keyword arguments in Python functions, and how does the `return` statement pass data back to the caller?"
        elif "normaliz" in topic_lower or "dbms" in topic_lower:
            q = "Explain the difference between 2NF and 3NF in DBMS normalization. How do transitive dependencies break 3NF?"
        elif "hook" in topic_lower or "react" in topic_lower:
            q = "Why must React Hooks only be called at the top level of function components, and how does `useEffect` handle cleanup?"
        elif "deadlock" in topic_lower:
            q = "What are the four necessary conditions for an Operating System deadlock, and how can resource ordering prevent circular wait?"
        elif "machine learning" in topic_lower:
            q = "What is the key difference between supervised and unsupervised learning, and how do training vs validation datasets prevent overfitting?"
        elif "html form" in topic_lower:
            q = "What is the difference between GET and POST methods in HTML forms, and why should sensitive data never be submitted via GET?"
        else:
            q = f"Explain how {topic} works in {subject}. What are its primary mechanics, rules, and practical benefits?"

        if expect_json:
            return json.dumps({
                "question": q,
                "purpose": f"Testing core understanding of {topic} principles, syntax, and practical benefits.",
                "follow_up_hint": f"Consider the core rules, execution flow, and edge cases of {topic}."
            })
        return q

    elif "name: creative peer ai" in prompt_lower or "you are the creative peer ai" in prompt_lower:
        if "python function" in topic_lower:
            p = "Think of a Python function like a recipe or a kitchen appliance! You pass ingredients (parameters) into it, it processes them internally, and it serves up a finished dish (return value)."
            a = "It operates like a microwave: press a button with inputs, run the internal cooking logic, and get the processed result out."
        elif "normaliz" in topic_lower or "dbms" in topic_lower:
            p = "Think of DBMS Normalization like Marie Kondo organizing a messy closet! Instead of dumping clothes, shoes, and paperwork into one huge box, you sort related items into separate labeled containers so nothing is duplicated."
            a = "It works like filing documents into specialized folders rather than piling every single piece of paper onto a single desk."
        elif "hook" in topic_lower or "react" in topic_lower:
            p = "Think of React Hooks like plug-and-play power modules for a UI component! Instead of writing heavy class components, you plug in `useState` for memory and `useEffect` for external connections."
            a = "Like attachments on a Swiss Army knife — each hook adds a precise capability to your function component without extra class boilerplate."
        else:
            p = f"Think of {topic} like a well-designed modular blueprint in {subject}! Each component has a designated role to ensure smooth execution."
            a = f"Like building blocks in architectural design — {topic} organizes logic cleanly."

        if expect_json:
            return json.dumps({
                "perspective": p,
                "analogy": a,
                "real_world_example": f"In real-world {subject} systems, {topic} is essential for maintainable, clean architecture."
            })
        return p

    elif "name: reviewer ai" in prompt_lower or "you are the reviewer ai" in prompt_lower:
        return json.dumps({
            "score": 85,
            "correctness": "mostly_correct",
            "reasoning_quality": "good",
            "strengths": [
                f"Accurately explained core mechanics of {topic}",
                f"Correctly identified key benefits within {subject}"
            ],
            "weaknesses": [
                f"Could expand on edge-case scenarios or advanced applications in {topic}"
            ],
            "knowledge_gaps": [
                f"Advanced edge-case handling in {topic}"
            ],
            "feedback": f"Great job explaining {topic}! You demonstrated clear understanding of its main principles in {subject}.",
            "recommended_difficulty": 3
        })

    elif "name: problem solver ai" in prompt_lower or "you are the problem solver ai" in prompt_lower or "problem" in prompt_lower:
        return json.dumps({
            "question": f"Given a real-world scenario involving {topic}, how would you handle a boundary condition or unexpected input in {subject}? Explain your solution.",
            "difficulty": 3,
            "concept": f"Applied problem solving in {topic}",
            "expected_skill": f"Implement robust {topic} strategies under complex constraints",
            "hint": f"Consider how {topic} handles edge cases and error states."
        })

    elif "name: mentor ai" in prompt_lower or "you are the mentor ai" in prompt_lower or "mentor" in prompt_lower:
        # Generate specific teaching content per topic
        if "python function" in topic_lower:
            exp = (
                "### 1. What are Python Functions?\n"
                "A function in Python is a reusable block of code that performs a specific task. "
                "Functions help break code into smaller, modular chunks, avoiding duplication and improving readability.\n\n"
                "### 2. Core Concepts & Syntax\n"
                "- **Defining a Function**: Use the `def` keyword followed by the function name and parentheses.\n"
                "- **Parameters & Arguments**: Values passed into functions to customize their execution.\n"
                "- **Return Values**: Use the `return` keyword to pass output back to the caller.\n"
                "- **Scope**: Variables declared inside a function are local to that function.\n\n"
                "### 3. Types of Arguments\n"
                "- **Positional Arguments**: Matched by order.\n"
                "- **Default Arguments**: Provide fallback values if no argument is supplied.\n"
                "- **Arbitrary Arguments (`*args`, `**kwargs`)**: Allow accepting variable numbers of positional or keyword arguments."
            )
            code = (
                "# Python Functions Example\n"
                "def calculate_total(price, tax_rate=0.08):\n"
                "    \"\"\"Calculate total price including tax.\"\"\"\n"
                "    total = price + (price * tax_rate)\n"
                "    return round(total, 2)\n\n"
                "# Function calls\n"
                "item_total = calculate_total(100.0)      # Uses default tax rate\n"
                "custom_total = calculate_total(100.0, 0.10) # Overrides default tax rate\n"
                "print(f'Total: ${item_total}') # Outputs: Total: $108.0"
            )
            ex = "In a shopping cart application, a `calculate_total()` function takes cart items, computes discounts and taxes, and returns the final invoice total."
            takeaway = "Python functions organize code into reusable modules, taking parameters as input and returning computed results using the `def` and `return` keywords."
            hint = "Always keep functions focused on a single responsibility for better testing and reuse."

        elif "normaliz" in topic_lower or "dbms" in topic_lower:
            exp = (
                "### 1. What is DBMS Normalization?\n"
                "Database Normalization is the systematic process of organizing data in a relational database to minimize redundancy and prevent data anomalies (insertion, update, and deletion anomalies).\n\n"
                "### 2. Normal Forms (1NF, 2NF, 3NF)\n"
                "- **First Normal Form (1NF)**: Requires atomic (indivisible) column values and unique row identification (Primary Key). No repeating groups.\n"
                "- **Second Normal Form (2NF)**: Meets 1NF and eliminates partial dependencies — all non-key attributes must depend on the *entire* composite primary key.\n"
                "- **Third Normal Form (3NF)**: Meets 2NF and eliminates transitive dependencies — non-key attributes must depend *only* on the primary key, not on other non-key attributes.\n\n"
                "### 3. Why Normalization Matters\n"
                "Normalizing database schemas ensures data consistency, saves storage space, and prevents data corruption when updating records."
            )
            code = (
                "-- Unnormalized Table -> Normalized (3NF) Tables\n"
                "-- 1. Customers Table (Primary Key: customer_id)\n"
                "CREATE TABLE Customers (\n"
                "    customer_id INT PRIMARY KEY,\n"
                "    customer_name VARCHAR(100),\n"
                "    email VARCHAR(100)\n"
                ");\n\n"
                "-- 2. Orders Table (Foreign Key references Customers)\n"
                "CREATE TABLE Orders (\n"
                "    order_id INT PRIMARY KEY,\n"
                "    customer_id INT REFERENCES Customers(customer_id),\n"
                "    order_date DATE,\n"
                "    total_amount DECIMAL(10, 2)\n"
                ");"
            )
            ex = "Instead of storing customer address on every order row in an Orders table, store customer details once in a `Customers` table and reference `customer_id` in `Orders`."
            takeaway = "Normalization reduces redundancy and ensures data integrity by dividing large tables into smaller, logically related tables linked by foreign keys."
            hint = "Remember the rule of thumb for 3NF: Every non-key field must depend on the key, the whole key, and nothing but the key."

        elif "hook" in topic_lower or "react" in topic_lower:
            exp = (
                "### 1. What are React Hooks?\n"
                "React Hooks are built-in functions introduced in React 16.8 that allow function components to manage state, side effects, and lifecycle behaviors without writing class components.\n\n"
                "### 2. Essential React Hooks\n"
                "- **`useState`**: Adds state variables to function components. Returns current state and an updater function.\n"
                "- **`useEffect`**: Performs side effects such as data fetching, subscriptions, or DOM updates after rendering.\n"
                "- **`useContext`**: Consumes values from a React Context without nested consumer components.\n"
                "- **`useRef`**: Persists mutable values across renders without causing re-renders.\n\n"
                "### 3. Rules of Hooks\n"
                "1. Only call Hooks at the **top level** (never inside loops, conditions, or nested functions).\n"
                "2. Only call Hooks from **React function components** or custom Hooks."
            )
            code = (
                "import React, { useState, useEffect } from 'react';\n\n"
                "function Counter() {\n"
                "  const [count, setCount] = useState(0);\n\n"
                "  // Runs after render when count changes\n"
                "  useEffect(() => {\n"
                "    document.title = `Clicked ${count} times`;\n"
                "  }, [count]); // Dependency array\n\n"
                "  return (\n"
                "    <button onClick={() => setCount(count + 1)}>\n"
                "      Clicks: {count}\n"
                "    </button>\n"
                "  );\n"
                "}"
            )
            ex = "Using `useState` to manage user input fields in a search box and `useEffect` to trigger an API fetch when the search query changes."
            takeaway = "React Hooks bring statefulness and lifecycle handling to function components, creating cleaner, composable code."
            hint = "Always specify dependency arrays in `useEffect` to control when side effects run."

        elif "deadlock" in topic_lower:
            exp = (
                "### 1. What is an Operating System Deadlock?\n"
                "A deadlock occurs in an operating system when a set of processes are blocked because each process holds a resource and waits for another resource held by another process in the same set.\n\n"
                "### 2. Four Coffman Conditions for Deadlock\n"
                "1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode.\n"
                "2. **Hold and Wait**: A process holds resources while requesting additional resources held by others.\n"
                "3. **No Preemption**: Resources cannot be forcibly taken from a process; they must be released voluntarily.\n"
                "4. **Circular Wait**: A closed chain of processes exists where each waits for a resource held by the next process."
            )
            code = (
                "// Deadlock illustration with threads in C/C++\n"
                "// Thread 1 locks Mutex A, then requests Mutex B\n"
                "// Thread 2 locks Mutex B, then requests Mutex A\n"
                "// Result: Both threads wait indefinitely (Circular Wait)"
            )
            ex = "Two trains approaching each other on a single track: neither can move forward until the other backs up, resulting in a deadlock."
            takeaway = "Deadlocks occur when processes enter a circular wait condition holding un-shareable resources. Deadlock prevention strategies eliminate at least one of the four Coffman conditions."
            hint = "Resource ordering (enforcing an ascending order for requesting mutexes) is a common way to prevent circular wait."

        elif "machine learning" in topic_lower:
            exp = (
                "### 1. What is Machine Learning?\n"
                "Machine Learning (ML) is a branch of artificial intelligence focused on building algorithms that learn patterns from data to make predictions or decisions without explicit step-by-step programming.\n\n"
                "### 2. Core Learning Paradigms\n"
                "- **Supervised Learning**: Models learn from labeled training data (e.g. Classification, Regression).\n"
                "- **Unsupervised Learning**: Models discover hidden patterns or clusters in unlabeled data (e.g. K-Means, PCA).\n"
                "- **Reinforcement Learning**: Agents learn optimal actions through trial, reward, and penalty in an environment."
            )
            code = (
                "# Supervised Learning with scikit-learn\n"
                "from sklearn.linear_model import LogisticRegression\n"
                "from sklearn.model_selection import train_test_split\n\n"
                "# 1. Split data\n"
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n"
                "# 2. Train model\n"
                "model = LogisticRegression()\n"
                "model.fit(X_train, y_train)\n\n"
                "# 3. Evaluate accuracy\n"
                "accuracy = model.score(X_test, y_test)"
            )
            ex = "Spam filtering systems analyze thousands of emails labeled 'spam' or 'ham' to learn keywords and header patterns that identify future spam automatically."
            takeaway = "Machine Learning relies on data-driven training to map inputs to accurate predictions across supervised, unsupervised, and reinforcement paradigms."
            hint = "Always keep training and test data strictly separate to avoid data leakage and measure true generalization performance."

        elif "html form" in topic_lower:
            exp = (
                "### 1. What are HTML Forms?\n"
                "HTML Forms are used to collect user inputs on a webpage and send that data to a server for processing or storage.\n\n"
                "### 2. Key Elements & Attributes\n"
                "- **`<form>` Tag**: Wraps all input controls. Key attributes: `action` (target URL) and `method` (`GET` or `POST`).\n"
                "- **Input Elements**: `<input type=\"text\">`, `<input type=\"password\">`, `<input type=\"checkbox\">`, `<select>`, `<textarea>`.\n"
                "- **Submit Button**: `<button type=\"submit\">` or `<input type=\"submit\">` triggers form submission."
            )
            code = (
                "<!-- Standard User Registration Form -->\n"
                "<form action=\"/api/register\" method=\"POST\">\n"
                "  <label for=\"username\">Username:</label>\n"
                "  <input type=\"text\" id=\"username\" name=\"username\" required />\n\n"
                "  <label for=\"email\">Email:</label>\n"
                "  <input type=\"email\" id=\"email\" name=\"email\" required />\n\n"
                "  <button type=\"submit\">Register</button>\n"
                "</form>"
            )
            ex = "A login page collecting a user's email and password, submitting them securely via HTTP POST to an authentication server endpoint."
            takeaway = "HTML forms capture user input through structured control elements and submit them using GET or POST HTTP methods."
            hint = "Always use `POST` for sensitive input like passwords to avoid exposing parameters in the URL."

        else:
            # Dynamic fallback tailored to the specific topic name and subject
            exp = (
                f"### 1. Understanding {topic}\n"
                f"{topic} in {subject} is an essential educational concept that defines core mechanisms, rules, and operational structures.\n\n"
                f"### 2. Important Concepts of {topic}\n"
                f"- **Core Definition**: {topic} establishes a clear framework for managing logic and data within {subject}.\n"
                f"- **Working Principles**: By breaking {topic} into key components, learners can understand how data flows and functions operate.\n"
                f"- **Practical Benefits**: Applying {topic} improves maintainability, reduces errors, and yields structured solutions.\n\n"
                f"### 3. Implementation Steps\n"
                f"Mastering {topic} requires understanding foundational rules, syntax/schemas, and real-world execution flow."
            )
            code = (
                f"// Code/Query example demonstrating {topic} in {subject}\n"
                f"function demonstrate{re.sub(r'[^a-zA-Z0-9]', '', topic).capitalize()}() {{\n"
                f"    // Demonstrating core mechanics of {topic}\n"
                f"    const status = '{topic} initialized successfully';\n"
                f"    console.log(status);\n"
                f"    return status;\n"
                f"}}"
            )
            ex = f"In real-world {subject} projects, {topic} is applied to build reliable, scalable system architecture."
            takeaway = f"Mastering {topic} provides fundamental competence in {subject}, establishing solid operational skills."
            hint = f"Focus on understanding the core purpose and boundary conditions of {topic} before diving into complex configurations."

        if expect_json:
            return json.dumps({
                "explanation": exp,
                "code_example": code,
                "example": ex,
                "key_takeaway": takeaway,
                "hint": hint
            })
        return exp

    return f"Demo mode active for {topic} in {subject}."


def _get_mock_json(system_prompt: str) -> dict:
    """Return mock JSON for demo mode."""
    text = _get_mock_response(system_prompt, "", expect_json=True)
    result = _parse_json_safe(text)
    return result or {"message": "Demo mode active", "status": "mock"}

