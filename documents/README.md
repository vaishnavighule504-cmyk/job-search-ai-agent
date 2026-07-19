# RAG Reference Documents

This directory is designated for storing reference materials (PDFs, text files, or markdown sheets) that the AI Career Assistant will retrieve context from during Retrieval-Augmented Generation (RAG).

## Folder Purpose in RAG:
During RAG queries:
1. The documents placed here will be split into smaller text chunks.
2. These chunks will be converted into vector embeddings and stored in a vector index.
3. When the user asks a career question, the assistant will search this directory to retrieve the most relevant advice and use it to formulate a accurate answer.
