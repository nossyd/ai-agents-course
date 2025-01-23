---
layout: default
img:
img_link: 
caption: 
title: PDDL and Planning
type: Homework
number: 1
active_tab: homework
release_date: 01-23-2025
due_date: 02-06-2025
materials:
submission_link: https://www.gradescope.com
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

### HW1

This HW has 4 parts, 3 are required and one is extra credit.

- [Part 1: Making a text game / simulation environment (40pts)](/homeworks/hw1/part-1-textgame)
- Part 2: Search algorithms in said simulation environment (30pts)
- Part 3: PDDL based classical planning in text games (30pts)
- Part 4 (extra credit): Making novel text simulations from WikiHow articles (20pts)


Submissions should be done on [Gradescope]({{page.submission_link}}).

## Grading
<div class="alert alert-warning" markdown="1">

</div>

{% if page.readings %} 
## Recommended readings
{% for reading in page.readings %}
* {{ reading.authors }}, <a href="{{ reading.url }}">{{ reading.title }}</a>.  <i>{{ reading.note }}</i>
{% endfor %}
{% endif %}
