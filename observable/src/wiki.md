---
title: Wiki Page
toc: false
---

<div id="base" style="padding: 20px;">
    <p id="wikiDescription"></p>
    <div id="histogram"></div>
</div>


```js
const base = document.getElementById('base');
const histogram = document.getElementById('histogram');
const urlParams = new URLSearchParams(window.location.search);
const wiki_id = urlParams.get('id');

async function fetchHumanOccurrenceHistogramData(wikiId) {
    const response = await fetch(`http://127.0.0.1:5000/histogram/occurrence?id=${wikiId}`);
    return response.json();
    
}

if (wiki_id) {
    document.title = `Wiki ID: ${wiki_id}`;
    fetchHumanOccurrenceHistogramData(wiki_id).then(data => {
        const chart = Plot.plot({
            x: {
                label: "Name"
            },
            y: {
                label: "Count"
            },
            marks: [
                Plot.rectY(data, {x: "name", y: "occurrence_count", fill: "steelblue"})
            ],
            width: 800
        });
        histogram.appendChild(chart);
    });
} else {
    histogram.textContent = 'No wiki ID provided, please provide a wiki id';
    
    
}

```




