---
title: "Publications"
layout: gridlay
sitemap: false
permalink: /publications/
---

<style>.fade-in-section{opacity:1 !important;transform:none !important;}</style>

## Publications

<p>Updated automatically from the lab database. * corresponding author. Full list on <a href="https://tinyurl.com/daehyunkim-publications">Google Scholar</a>.</p>

<input type="text" class="pub-search" id="pubSearch" placeholder="Filter by title, author, or year...">

<div class="section-card" id="pubList">
<h3>In press and under review</h3>

{% bibliography --query @unpublished %}

<h3>Journal articles</h3>

{% bibliography --query @article %}

<h3>Book chapters</h3>

{% bibliography --query @incollection %}
</div>
