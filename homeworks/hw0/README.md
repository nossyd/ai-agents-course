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
- [Part 1: Search and Value Iteration](part-1-search-and-value-iteration)
- [Part 2: LM training with Huggingface](part-2-huggingface-LM-training)

### Submission
Submissions should be done on [Gradescope]({{page.submission_link}}).


