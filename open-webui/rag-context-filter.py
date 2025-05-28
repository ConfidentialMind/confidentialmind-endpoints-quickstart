"""
title: RAG Context Filter
author: your-name
version: 0.1
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import requests
import json
import re


class Filter:
    class Valves(BaseModel):
        enabled: bool = Field(default=True, description="Enable RAG context injection")
        rag_endpoint: str = Field(
            default="http://localhost:8000",
            description="Base URL of your RAG backend (without /context)",
        )
        api_key: str = Field(default="", description="API key for RAG backend")
        max_chunks: int = Field(default=5, description="Max chunks to retrieve")
        timeout: int = Field(default=10, description="Request timeout in seconds")
        include_metadata: bool = Field(
            default=False, description="Include chunk metadata in context"
        )
        keep_context_in_history: bool = Field(
            default=False, description="Keep RAG context visible in chat history"
        )
        context_template: str = Field(
            default="Relevant Context:\n{context}\n\nUser Query: {query}",
            description="Template for injecting context",
        )
        # Optional filtering parameters
        group_id: str = Field(
            default="", description="Filter to documents in specific group"
        )
        user_id: str = Field(
            default="", description="Filter to documents owned by specific user"
        )

    def __init__(self):
        self.valves = self.Valves()
        # Track which messages we've modified
        self.modified_messages = set()

    def get_rag_context(self, query: str) -> tuple[List[str], List[float], dict]:
        """
        Call RAG backend to retrieve context chunks
        Returns (chunks, scores, metadata)
        """
        try:
            # Build request payload
            payload = {"query": query, "max_chunks": self.valves.max_chunks}

            # Add optional filters
            if self.valves.group_id:
                payload["group_id"] = self.valves.group_id
            if self.valves.user_id:
                payload["user_id"] = self.valves.user_id

            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.valves.api_key:
                headers["Authorization"] = f"Bearer {self.valves.api_key}"

            endpoint = f"{self.valves.rag_endpoint}/context"
            print(f"RAG: Calling {endpoint}")

            response = requests.post(
                endpoint, json=payload, timeout=self.valves.timeout, headers=headers
            )

            print(f"RAG: Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                chunks = data.get("chunks", [])
                scores = data.get("scores", [])
                files = data.get("files", [])

                print(f"RAG: Retrieved {len(chunks)} chunks")

                # Add metadata if requested
                if self.valves.include_metadata and files:
                    enhanced_chunks = []
                    for i, chunk in enumerate(chunks):
                        if i < len(files) and files[i].get("metadata"):
                            metadata_str = json.dumps(files[i]["metadata"], indent=2)
                            enhanced_chunk = (
                                f"{chunk}\n\n[Source Metadata: {metadata_str}]"
                            )
                            enhanced_chunks.append(enhanced_chunk)
                        else:
                            enhanced_chunks.append(chunk)
                    chunks = enhanced_chunks

                for i, chunk in enumerate(chunks):
                    print(f"chunk {i}: {chunk}")

                return chunks, scores, {"files": files}
            else:
                print(f"RAG: Error {response.status_code}: {response.text}")
                return [], [], {}

        except Exception as e:
            print(f"RAG: Exception during context retrieval: {str(e)}")
            return [], [], {}

    def extract_original_query(self, enhanced_content: str) -> str:
        """
        Extract the original user query from the enhanced content using the template
        """
        try:
            # Create a regex pattern from the template
            template = self.valves.context_template

            # Escape special regex characters and replace placeholders
            pattern = re.escape(template)
            pattern = pattern.replace(r"\{context\}", r".*?")
            pattern = pattern.replace(r"\{query\}", r"(.*)")

            # Try to match and extract the query
            match = re.search(pattern, enhanced_content, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                # Fallback: look for common patterns
                # Try to find content after "User Query:" or similar
                query_patterns = [
                    r"User Query:\s*(.*?)$",
                    r"Query:\s*(.*?)$",
                    r"Question:\s*(.*?)$",
                ]

                for pattern in query_patterns:
                    match = re.search(
                        pattern, enhanced_content, re.DOTALL | re.MULTILINE
                    )
                    if match:
                        return match.group(1).strip()

                # If no pattern matches, return the content as-is
                return enhanced_content

        except Exception as e:
            print(f"RAG: Error extracting original query: {str(e)}")
            return enhanced_content

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        print(f"RAG FILTER: inlet called, enabled={self.valves.enabled}")

        if not self.valves.enabled:
            return body

        try:
            messages = body.get("messages", [])
            if not messages:
                return body

            # Clean up any previously enhanced messages if we're not keeping context
            if not self.valves.keep_context_in_history:
                for msg in messages:
                    if msg.get("role") == "user" and id(msg) in self.modified_messages:
                        # This message was previously enhanced, extract original query
                        original_query = self.extract_original_query(msg["content"])
                        msg["content"] = original_query
                        print(f"RAG: Restored original query for message")

            # Find the last user message
            last_user_msg = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg
                    break

            if not last_user_msg or not last_user_msg.get("content"):
                return body

            original_query = last_user_msg["content"]

            # Skip if this message was already processed (avoid double-processing)
            if id(last_user_msg) in self.modified_messages:
                print("RAG: Message already processed, skipping")
                return body

            print(f"RAG: Processing query: {original_query[:100]}...")

            # Get RAG context
            chunks, scores, metadata = self.get_rag_context(original_query)

            if chunks:
                # Format context chunks
                formatted_chunks = []
                for i, chunk in enumerate(chunks):
                    chunk_header = f"[Context {i+1}]"
                    formatted_chunks.append(f"{chunk_header}\n{chunk}")

                formatted_context = "\n\n".join(formatted_chunks)

                # Inject context using template
                enhanced_query = self.valves.context_template.format(
                    context=formatted_context, query=original_query
                )

                # Update the message
                last_user_msg["content"] = enhanced_query

                # Track that we modified this message
                self.modified_messages.add(id(last_user_msg))

                print(f"RAG: Injected {len(chunks)} context chunks")
                if scores:
                    avg_score = sum(scores) / len(scores)
                    print(f"RAG: Average relevance score: {avg_score:.3f}")

            else:
                print("RAG: No context retrieved, using original query")

        except Exception as e:
            print(f"RAG: Error in inlet: {str(e)}")
            # Don't modify the message if there's an error

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        print(f"RAG FILTER: outlet called")
        print(f"body: {body}")
        return body