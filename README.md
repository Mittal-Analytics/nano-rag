# About nano-rag

This a experimental project to implement RAG using nano-django.


## Problem statement

We can use RAG to answer things like:

```
- What are major potholes in the company?
- How is the management?
- Why are their margins improving?
- What new the company is doing?
- How have their volumes been over the years?
- What is their market share? How is it changing over the years?
- Ranking over the years (eg in Screener we can check ranks on many websites)
- How the competition been doing? How have their numbers been?
- Who are major customers?
- Who are major competitors?
- A table of what the company has been saying, vs how they have been doing
```

**Why not use off-the-shelf solutions like LlamaIndex / NotebookLLM?**

1. To squeeze out performance
2. For using better chunks for PDFs
3. Use `pgvector`
4. Write own agents
5. More customisations and power
6. Better understanding



## Getting the local server running

```bash
# creating virtual env
uv venv
source .venv/bin/activate

# install dependencies
uv pip install -r requirements.txt
```
