# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
> The topic I chose for this project was a guide to help college students. When you are an incoming freshman at a university, you are fed so much information or none at all. Sometimes we don't even know who to ask or where to find the resources, so this tools is just what you need! This tool is created to help freshmen (or any student) find the answers to their questions.
> This project will be based on George Mason University and will use other external sources for information on advice for college students.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 |Medium - Marquette University | University Freshmen Advice Article | https://stories.marquette.edu/what-piece-of-advice-would-you-give-to-your-freshman-self-fc84d53af190 |
| 2 | South Mountain Community College | College Advice | https://www.southmountaincc.edu/current-students/top-tips-college-success |
| 3 | CSUN - University Article | Registration Advice | https://www.csun.edu/current-students/register/tips |
| 4 | GMU Website | Dining Hall Information | https://www.gmu.edu/student-life/living-and-dining |
| 5 | GMU Website | GMU Parking | https://transportation.gmu.edu/parking/ |
| 6 | GMU Website | GMU Clubs & Organizations | https://si.gmu.edu/rso/ |
| 7 | GMU Website | GMU IT Degree | https://catalog.gmu.edu/colleges-schools/engineering-computing/school-computing/information-sciences-technology/information-technology-bs/ |
| 8 | GMU Website | Student Life | https://www.gmu.edu/student-life |
| 9 | GMU Website | Internships | https://careers.gmu.edu/find-job-or-internship |
| 10 | USBLS | Careers & College Majors | https://www.bls.gov/careeroutlook/2021/article/field-of-degree-and-careers.htm |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** This is eough characters to capture 1 complete tip or idea without merging unrelated topics. The character overlap will preserve the contect at boundries so a fact split across two chunks is retrievable.

**Final chunk count:** 276

---
## Architecture - Pipline Diagram
```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Document Ingestion │────▶│      Chunking        │────▶│  Embedding +        │────▶│     Retrieval       │────▶│     Generation      │
│─────────────────────│     │─────────────────────│     │   Vector Store      │     │─────────────────────│     │─────────────────────│
│ requests            │     │ Custom paragraph-   │     │─────────────────────│     │ Semantic similarity │     │ Groq API            │
│ BeautifulSoup4     │     │ aware splitter      │     │ all-MiniLM-L6-v2    │     │ search              │     │ llama-3.3-70b       │
│ 10 source URLs      │     │ Chunk: 400 chars    │     │ (sentence-          │     │ top-k = 4           │     │ -versatile          │
│                     │     │ Overlap: 50 chars   │     │  transformers)      │     │                     │     │ Grounded prompt     │
│                     │     │                     │     │ ChromaDB            │     │ Returns chunks +    │     │ Source attribution  │
│                     │     │                     │     │ (persistent local)  │     │ source metadata     │     │ in every response   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** ll-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** 
- Context Length: all-MiniLM-L6-v2 has a 256-token limit, so the longer chunks get cut off meaning less information loss per chunk.
- Cost vs. accuracy: Local models are free but less accurate. API-hosted models cost per token but return better retrieval results at a larger scale.
- Multilingual support: all-MiniLM-L6-v2 is English-only. A university serving international students would need a multilingual model.
- Latency: Local models run on your CPU and API models offload computation but add network delay.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** You are a guiding college student advisor at George Mason University. Answer the student's question using only the information provided in the documents listed below. Do not use any knowledge from your training data. By any chance the documents do not contain enough information to answer, then respond with: "I don't have enough information in my documents to answer that question.".

**How source attribution is surfaced in the response:** The source names were appended after the generation by extracting the source label metadata field from the ChromaDB chunk, then it was formatted as a numbered list. The attribution was guaranteed by the pipline structure in the query python file.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What tips exist for registering for classes successfully? | Plan ahead using prerequisites of the class through your academic class application platform. Use the waitlist if a course is full, but try your best to sign up for classes early. | Correct - Listed 6 specific tips from CSUN source|Partialy Relevant |Accurate |
| 2 |What fields of work are most common for college gratuates? |The top fields of work most common for college graduates are Business, Healthcare, Education, STEM, with specific employment % data | Correct - listed the specific occupations categories listed from the BLS website| Relevant| Accurate|
| 3 | What study habits or behaviors is recommended for academic success? | It is best to attend office hours, manage time efficiently, and form study groups within your class to result in better academic success. | Correct - Provided details that were specified in several articles (class engagement, communication w/ professors, etc.)| Relevant| Accurate
| 4 | What dining halls or meal plan options are avaiable at GMU?|There are many dining halls available such as Southside, Ike's, The Spot, and several small food franchises scattered across the GMU Campus. Look into the Meal Plans website to learn more about the possible meal plans. | Correct - Described the different options available at GMU (different food groups, Starship robots, Residence Halls/ Dining Halls)| Relevant| Accurate|
| 5 |What specific resources does GMU offer to help students find internships? |There are different platforms available for students to find internships includeing Handshake, Career Services, and Employer Events. |Correct - Provided the tools/ resources available | Partially Relevant| Accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** What tips exist for registering for classes successfully?

**What the system returned:** Returned the correct answere but there was a weak semantic match. 

**Root cause (tied to a specific pipeline stage):** This can be due to the CSUN registration page that I included. Yes, this source was not a gmu source and I probably should have changed it before continuing forward. The other reason could be beacuse the it wasn't able to distinguish between a registration tip and a general academic advice hence mixing it all together.

**What you would change to fix it:** Increase the chunk size to 800 or more (initially I had it at 400, but there were errors in the answers so I changed it later to 800) so that each chunk contains more information/ context.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Write the chunk strategy in readme/ planning.md before coding. I initially had it at 400 characters but after testing it out, I realized I had to increase the chunk size to 800 characters to get the best answers possible.

**One way your implementation diverged from the spec, and why:** I assumed the spec for chunk size would stay fixed at 400 characeters, but when working on Milestone 4 for retrieval testing, I noticided it carried sufficient semantic signal. This is why I increaded it to 800 characters which improved the retrieval quality.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My Document Sources table, Chunking Strategy section, and pipeline diagram from planning.md
- *What it produced:* ingest.py with scraping via requests/BeautifulSoup, paragraph-aware chunking, and ChromaDB storage with source metadata
- *What I changed or overrode:* The initial cleaner didnt filter the navigation text aggressively/ well enough. I made the AI filter and drop lines which contained: skip to, open in app, sign in. This reduced the total chunks a lot.

**Instance 2**

- *What I gave the AI:*  Retrieval Approach section and grounding requirement
- *What it produced:* query.py with a retrieve() function, generate() function using Groq llama-3.3-70b-versatile, and an ask() wrapper
- *What I changed or overrode:* Initially the prompt only suggesting grounding instead of enforcing it, so I changed it to explicitly forbit using any training knowledge and only forcus on the documents provided. If there was a question which was not trained to be answered from the documents, then it will let the user know they cannot answer it.
