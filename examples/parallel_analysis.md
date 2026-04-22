Build a parallel document analysis pipeline:
- A coordinator agent that receives a document and splits analysis tasks
- Three parallel specialist agents: one for sentiment analysis, one for key entity extraction, and one for topic classification
- A merger agent that collects all three outputs and produces a unified report

Use parallel execution strategy since the three specialists are independent.
