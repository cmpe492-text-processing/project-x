---
title: Wiki Page
toc: false
---

[//]: # (<div id="base" style="padding: 20px;">)

[//]: # (    <div>)

[//]: # (        <div id="tableContainer"></div>        )

[//]: # (        <div id="histogram_2"></div>)

[//]: # (    </div>)

[//]: # (</div>)

<div class="grid grid-cols-12">
  <div class="card">
    <h2>Most Occurred Entities Table</h2>
    <div id="tableContainer"></div>
  </div>
  <div class="card">
    <h2>Sentiment Occurrence Count</h2>
    <div id="histogram_2"></div>
  </div>
</div>

```js
    
   function createTable(data) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Add CSS styles
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';

    const headerRow = document.createElement('tr');
    const headers = ['Occurrence Count', 'Name', 'Wiki Info'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.style.border = '1px solid black';
        th.style.padding = '10px';
        th.style.backgroundColor = '#f2f2f2';
        th.style.textAlign = 'left';
        th.style.fontWeight = 'bold';
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    data.forEach(item => {
        const row = document.createElement('tr');

        const cellCount = document.createElement('td');
        cellCount.textContent = item.n;
        cellCount.style.border = '1px solid black';
        cellCount.style.padding = '10px';
        row.appendChild(cellCount);

        const cellName = document.createElement('td');
        cellName.textContent = item.name;
        cellName.style.border = '1px solid black';
        cellName.style.padding = '10px';
        row.appendChild(cellName);

        const cellWiki = document.createElement('td');
        const link = document.createElement('a');
        link.href = item.wiki_info;
        link.textContent = 'View Info';
        link.style.color = '#1a73e8';
        cellWiki.appendChild(link);
        cellWiki.style.border = '1px solid black';
        cellWiki.style.padding = '10px';
        row.appendChild(cellWiki);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    return table;
}




    
```

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
        
    fetchFeatureExtractionJSON(wiki_id).then(data => {
    const most_occurred_entities = data.most_occurred_entities;
    const main_entity = data.main_entity?.sentiments_extended;
    const negatives = main_entity.map(d => -d?.negative).filter(d => d?.negative != 0)
    const positives = main_entity.map(d => d?.positive).filter(d => d?.positive != 0)
        
    const tableContainer = document.getElementById('tableContainer');
    const table = createTable(most_occurred_entities);
    console.log(most_occurred_entities);
    tableContainer.appendChild(table);
    
    

    const positiveBinGenerator = d3.bin().domain([0.001, 1]).thresholds(20);
    const negativeBinGenerator = d3.bin().domain([-1, -0.001]).thresholds(20);

    const binsPositives = positiveBinGenerator(positives);
    const binsNegatives = negativeBinGenerator(negatives);

    const chart = Plot.plot({
        x: {
            label: "Value Range (0 to 1)",
            domain: [-1, 1]
        },
        y: {
            label: "Occurrence Count"
        },
        marks: [
            Plot.rectY(binsPositives, {
                x1: d => d.x0,
                x2: d => d.x1,
                y: d => d.length,
                fill: "green",
                title: "Positive Values",
            }),
            Plot.rectY(binsNegatives, {
                x1: d => d.x0,
                x2: d => d.x1,
                y: d => d.length,
                fill: "red",
                title: "Negative Values"
            }),
            Plot.ruleY([0])
        ],
        width: 1200,
        height: 600,
    });
    document.getElementById('histogram_2').appendChild(chart);
    });
    
} else {
    histogram.textContent = 'No wiki ID provided, please provide a wiki id';
    
    
}

```




