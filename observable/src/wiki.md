---
title: Wiki Page
toc: false
---

<div id="base" style="padding: 20px;">
    <p id="wikiDescription"></p>
    <div id="histogram"></div>
    <div id="histogram_2"></div>
</div>


```js
const base = document.getElementById('base');
const histogram = document.getElementById('histogram');
const histogram_2 = document.getElementById('histogram_2');
const urlParams = new URLSearchParams(window.location.search);
const wiki_id = urlParams.get('id');

async function fetchHumanOccurrenceHistogramData(wikiId) {
    const response = await fetch(`http://127.0.0.1:5000/histogram/occurrence?id=${wikiId}`);
    return response.json();
    
}

async function fetchFeatureExtractionJSON(wikiId) {
    const response = await fetch(`http://127.0.0.1:5000/histogram/co-occurrence?id=${wikiId}`);
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
        
    fetchFeatureExtractionJSON(wiki_id).then(data => {
    const main_entity = data.main_entity.sentiments_extended;
    const compounds = main_entity.map(d => d.compound);
    const chart = Plot.plot({
        x: {
            label: "Value Range (0 to 1)"
        },
        y: {
            label: "Compound Value Occurrence Count"
        },
        marks: [
            Plot.rectY(compounds, Plot.binX({ // x ekseninde binleme yapıyoruz
                domain: [0, 1], // Aralığı 0 ile 1 olarak belirliyoruz
                thresholds: 20 // 20 parçaya bölünüyor
            }))
        ],
        width: 800
    });
    histogram_2.appendChild(chart); // 'histogram' isimli bir DOM elemanına grafiği ekliyoruz
    });
    
} else {
    histogram.textContent = 'No wiki ID provided, please provide a wiki id';
    
    
}

```




