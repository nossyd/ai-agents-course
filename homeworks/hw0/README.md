---
layout: default
img:
img_link: 
caption: 
title: Pre-reqs
type: Homework
number: 0
active_tab: homework
release_date: 01-06-2025
due_date: 01-13-2025
materials:
submission_link:
readings:
---

{% if page.materials %}
<div class="alert alert-info">
You can download the materials for this assignment here:
<ul>
{% for item in page.materials %}
<li><a href="{{item.url}}">{{ item.name }}</a></li>
{% endfor %}
</ul>
</div>
{% endif %}

---

### HW0

HW0 consists of two parts:
- [Part 1: Search and Value Iteration](part-1-search-and-value-iteration) (50pts)
- [Part 2: LM training with Huggingface](part-2-huggingface-LM-training) (50pts)

### Submission
Submissions should be done on [Gradescope](https://www.gradescope.com).
You need to submit code for Part 1 and Part 2, and a PDF file for Part 2.

**Submit your code**

You need to submit **4** files to Gradescope: "HW 0 - Code".

- `search.py`
- `searchAgents.py`
- `valueIterationAgents.py`
- `hw0-part-2.ipynb`

Part 1 will be automatically graded by the Gradescope system. The score displayed immediately after submission will be your final score for Part 1.

**Submit your PDF (only for Part 2)**

1. Re-run all cells in order. Ensure that all cell outputs are displayed correctly.
2. Convert the notebook to PDF: 
- Download the .ipynb file to your local machine.
- Use a tool like `nbconvert` to convert the notebook to PDF.
- Alternatively, if you encounter issues with nbconvert, you can save the notebook webpage as a PDF.
3. Review the PDF file: Look at the PDF file and make sure all your codes are displayed correctly. 
5. Submit your PDF and the notebook file on Gradescope: "HW 0 - Part 2 PDF"
