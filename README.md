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

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What tips exist for registering for classes successfully? | Plan ahead using prerequisites of the class through your academic class application platform. Use the waitlist if a course is full, but try your best to sign up for classes early. | ..|.. |.. |
| 2 |What fields of work are most common for college gratuates? |The top fields of work most common for college graduates are Business, Healthcare, Education, STEM, with specific employment % data | ...| ..| ..|
| 3 | What study habits or behaviors is recommended for academic success? | It is best to attend office hours, manage time efficiently, and form study groups within your class to result in better academic success. | ..| ..| ..|
| 4 | What dining halls or meal plan options are avaiable at GMU?|There are many dining halls available such as Southside, Ike's, The Spot, and several small food franchises scattered across the GMU Campus. Look into the Meal Plans website to learn more about the possible meal plans. | .| .| .|
| 5 |What specific resources does GMU offer to help students find internships? |There are different platforms available for students to find internships includeing Handshake, Career Services, and Employer Events. |.. | .| .|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

### Chunk Output
Source : Marquette Freshman Advice
Chunk  : What Piece of Advice Would You Give to Your Freshman Self? | by Andi Sirokman | We Are Marquette>
Stories of Marquette University students and alumni
What Piece of Advice Would You Give to Your Freshman Self?
Press enter or click to view image in full size
Photo by Rachel Morrison from the
Marquette
------------------------------------------------------------

Source : Marquette Freshman Advice
Chunk  : your inbox
You will meet more people in the first few weeks of college than you’ve met in the previous year, if not longer.
The trick to getting the confidence to talk to new people is to assume that they already like you before you’ve even talked to them.
That changes your entire mindset before the
------------------------------------------------------------

Source : Marquette Freshman Advice
Chunk  : al and mental well being.
You’re going to be exposed to so many new things, places, people and experiences that it’ll be very easy to overstress yourself. Make sure to look after your health. Go to bed early. Take a half hour everyday to do something you enjoy. If something’s on your mind, go talk t
------------------------------------------------------------

Source : Marquette Freshman Advice
Chunk  : ous, but they’re massively important.
You are going to make so, so many mistakes in college.
That is a perfectly normal part of life. It’s your first time living on your own, you’re not going to get a lot of things even close to perfect. Learn from your mistakes, but do not dwell on them. A failed e
------------------------------------------------------------

Source : Marquette Freshman Advice
Chunk  : n on your worth as a human being.
Go out of your way to make an impression on faculty members.
You may not like or agree with some of them, but they know things that you don’t and desperately want to see you succeed. Go to their office hours at least once per semester, if only to introduce yourself.>
------------------------------------------------------------
---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

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

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
