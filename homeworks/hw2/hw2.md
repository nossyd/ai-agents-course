---
layout: default
img: zork.jpg
img_link: https://en.wikipedia.org/wiki/Zork#/media/
caption: Zork, an early intractive fiction game released in 1977.
title: RL for Language Agents
type: Homework
number: 2
active_tab: homework
release_date:
due_date:
materials:
    - 
        name: Text Adventure Game starter code (Zip file)
        url: 
submission_link:
readings:
    -
      title: Textworld
      authors: Cote et al. 2019
      url: https://github.com/microsoft/TextWorld
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
