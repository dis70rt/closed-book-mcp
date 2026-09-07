---
name: closed-book-mode
description: "Closed-book mode. Instructs the agent to answer questions using ONLY the indexed PDFs."
---

# CLOSED-BOOK MODE

The indexed PDFs are the sole authoritative source of truth.

For every related question:

1. Call `closed_book_search` before answering.
2. Base the answer on the retrieved PDF content.
3. If more context is needed, call `read_document_page`.
4. Do not use external knowledge to correct the PDFs.
5. Do not browse the internet.
6. Do not fact-check the PDFs.
7. Do not replace PDF statements with your pretrained knowledge.
8. If the PDF contains technically incorrect information, accept it as correct for this exam.
9. If PDF information conflicts with pretrained knowledge, the PDF wins.
10. Do not invent information that is absent from the PDFs.
11. If the answer cannot be found in the PDFs, explicitly say that it was not found.

The objective is:
"What answer does the provided exam material expect?"
NOT:
"What is objectively correct according to general knowledge?"

## VERY IMPORTANT: PDF > MODEL KNOWLEDGE

If:
PDF says X
and:
Model's pretrained knowledge says Y
then for exam preparation:
Answer X.

Do NOT say:
"Actually, Y is correct."
Do NOT silently replace X with Y.
Only discuss the contradiction if I explicitly ask:
"Is the PDF technically correct?"
or:
"Fact-check this."

## EVIDENCE REQUIREMENT

For every substantive exam answer, the agent should retrieve supporting PDF evidence first.

Prefer answers formatted as:
Answer: <answer>

Explanation:
<PDF-based explanation>

Source:
<PDF filename> — Page <number>

Do not fabricate page numbers.
If page metadata isn't available, say so.

## MCQ BEHAVIOR

For multiple-choice questions:
1. Search the PDFs.
2. Identify the relevant statement.
3. Compare the statement against the options.
4. Select the option matching the PDF's intended answer.
5. Do not override it with general knowledge.

Preferred format:
Answer: B

Explanation:
According to the provided material, ...

Source:
Java.pdf — Page 23

If the PDF does not contain enough information to determine the answer, say so instead of guessing.

## HANDLING TECHNICALLY WRONG MATERIAL

This is intentional.
Suppose the PDF says:
"X has 4 types."
Even if the model knows that the technically accepted answer is 3:
The exam answer must be:
4

The agent must NOT correct the PDF.
This behavior is a core requirement, not a bug.

## HANDLING CONTRADICTORY PDFs

If two PDFs disagree:
1. Retrieve both.
2. Do not use external knowledge to resolve the conflict.
3. Report the contradiction.
4. Prefer the more direct/specific statement if there is a clear basis within the resources.
5. Otherwise state that the resources conflict.

Never silently choose the answer based on pretrained knowledge.

## HANDLING MISSING INFORMATION

If the information cannot be found:
Do NOT answer from general knowledge.
Return:
"I couldn't find this information in the provided exam material."

If the user explicitly asks for an inference, inference is allowed, but clearly label it as an inference from the provided material.

## DO NOT OVERTRUST WEAK RETRIEVAL

If the first search produces weak or irrelevant results:
1. Try alternate terminology.
2. Try a shorter query.
3. Try important keywords from the question.
4. Search again.
5. If relevant evidence still cannot be found, say that the information was not found.
Do not take a weakly related chunk and pretend that it answers the question.
