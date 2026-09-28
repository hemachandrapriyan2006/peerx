"""
PeerX Knowledge Service
RAG-ready abstraction for retrieving topic context.
MVP: Curated knowledge base. Ready for vector search expansion.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Curated knowledge base for common CS topics (MVP)
KNOWLEDGE_BASE = {
    "inheritance": {
        "subject": "Java",
        "concepts": [
            "Inheritance allows a class to inherit properties and methods from another class",
            "The 'extends' keyword is used in Java for inheritance",
            "Java supports single inheritance (one parent class)",
            "Method overriding: redefining a parent method in a child class",
            "Method overloading: same method name, different parameters",
            "The 'super' keyword accesses parent class members",
            "Access modifiers affect inheritance: public, protected, private",
            "Abstract classes can have both abstract and concrete methods",
            "Constructors are not inherited but can be called via super()"
        ]
    },
    "oop": {
        "subject": "Java",
        "concepts": [
            "Four pillars: Encapsulation, Inheritance, Polymorphism, Abstraction",
            "Encapsulation: bundling data and methods, hiding internal state",
            "Polymorphism: one interface, multiple implementations",
            "Abstraction: hiding complex implementation details",
            "Classes are blueprints; objects are instances",
            "Interfaces define contracts without implementation"
        ]
    },
    "data structures": {
        "subject": "Computer Science",
        "concepts": [
            "Arrays: fixed-size, contiguous memory, O(1) access",
            "Linked Lists: dynamic size, O(n) access, O(1) insertion",
            "Stacks: LIFO (Last In, First Out)",
            "Queues: FIFO (First In, First Out)",
            "Trees: hierarchical, binary trees, BST",
            "Hash Tables: key-value pairs, O(1) average lookup",
            "Graphs: nodes and edges, directed/undirected"
        ]
    },
    "algorithms": {
        "subject": "Computer Science",
        "concepts": [
            "Time complexity: Big O notation",
            "Sorting: Bubble, Selection, Insertion, Merge, Quick sort",
            "Searching: Linear O(n), Binary O(log n)",
            "Recursion: base case and recursive case",
            "Dynamic Programming: overlapping subproblems, memoization",
            "Greedy algorithms: locally optimal choices",
            "Divide and Conquer: break into subproblems"
        ]
    },
    "python basics": {
        "subject": "Python",
        "concepts": [
            "Python is dynamically typed and interpreted",
            "Data types: int, float, str, list, dict, tuple, set",
            "List comprehensions for concise iteration",
            "Functions: def keyword, *args, **kwargs",
            "Classes and objects in Python",
            "Exception handling: try, except, finally",
            "Modules and imports"
        ]
    },
    "databases": {
        "subject": "Computer Science",
        "concepts": [
            "SQL: Structured Query Language for relational databases",
            "CRUD: Create, Read, Update, Delete operations",
            "Normalization: reducing data redundancy",
            "Primary Key: unique identifier for rows",
            "Foreign Key: references another table",
            "Joins: INNER, LEFT, RIGHT, FULL",
            "Indexes: improve query performance"
        ]
    }
}


class KnowledgeService:
    """
    RAG-ready knowledge retrieval service.

    MVP: Keyword-based lookup from curated knowledge base.
    Future: Vector similarity search with Supabase pgvector.
    """

    def retrieve_context(self, query: str, subject: str = None) -> str:
        """
        Retrieve relevant context for a given query.

        Args:
            query: The topic or question to retrieve context for
            subject: Optional subject to narrow down results

        Returns:
            Relevant context string for the AI agents
        """
        query_lower = query.lower().strip()
        context_parts = []

        # Search through knowledge base
        for topic_key, topic_data in KNOWLEDGE_BASE.items():
            # Match by topic key or if query contains the key
            if topic_key in query_lower or query_lower in topic_key:
                # Optionally filter by subject
                if subject and subject.lower() not in topic_data["subject"].lower():
                    continue

                concepts = topic_data["concepts"]
                context_parts.append(f"Key concepts for {topic_key}:")
                for concept in concepts:
                    context_parts.append(f"  • {concept}")

        if context_parts:
            return "\n".join(context_parts)

        # Fallback: search for query terms in all concepts
        for topic_key, topic_data in KNOWLEDGE_BASE.items():
            for concept in topic_data["concepts"]:
                if any(word in concept.lower() for word in query_lower.split() if len(word) > 3):
                    context_parts.append(f"  • {concept}")

        if context_parts:
            return "Related concepts:\n" + "\n".join(context_parts[:10])

        return ""

    def get_topics_for_subject(self, subject: str) -> list:
        """Get available topics for a given subject."""
        topics = []
        subject_lower = subject.lower()
        for topic_key, topic_data in KNOWLEDGE_BASE.items():
            if subject_lower in topic_data["subject"].lower():
                topics.append(topic_key.title())
        return topics

    def get_available_subjects(self) -> list:
        """Get list of all available subjects."""
        subjects = set()
        for topic_data in KNOWLEDGE_BASE.values():
            subjects.add(topic_data["subject"])
        return sorted(list(subjects))


knowledge_service = KnowledgeService()
