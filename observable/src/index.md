---
title: 'Project X'
toc: false
sidebar: false
---
<div style="display: flex; justify-content: center; align-items: center; height: 20vh; flex-direction: column">
    <h2>Search any sentence</h2>
    <br>
    <input type="text" id="search-bar" placeholder="Donald Trump called Joe Biden 'Dumb Joe'" style="width: 100%; padding: 10px; font-size: 16px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
</div>
<div id="results-table"></div>
<br/>
<div id="results-sentiment"></div>
<br/>
<div id="results-nltk"></div>

```js
function sentimentChart(data, {width}) {
  return Plot.plot({
      width: width,
      height: 300,
      marginTop: 20,
      marginLeft: 50,
      x: {domain: [-1,1],grid: true, label: "Score"},
      y: {domain: data.map(d => d.sentiment), label: null},
      marks: [
          Plot.barX(data, {x: "score", y: "sentiment", fill: "color", tip: true}),
          Plot.ruleX([0])
      ]
  });
}




document.getElementById('search-bar').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        const query = event.target.value;
        fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Search results:', data);
                const results_sentiment = document.getElementById('results-sentiment');
                const results_table = document.getElementById('results-table');
                results_sentiment.innerHTML = '';
                results_table.innerHTML = '';

                
                const plotData = [
                  {sentiment: ' Compound', score: data.scores.compound, color: data.scores.compound >= 0 ? '#4caf50' : '#f44336'},
                  {sentiment: ' Positive', score: data.scores.pos, color: '#2196f3'},
                  {sentiment: ' Negative', score: -data.scores.neg, color: '#f44336'},
                  {sentiment: ' Neutral', score: data.scores.neu, color: '#ffeb3b'}
                ];

                const chart = sentimentChart(plotData, {width: 900});

                const text = data.text;
                const entities = data.entities;
                const textDiv = document.createElement('div');
                textDiv.innerHTML = '<h2>Text</h2>';
                let i = 0;
                entities.forEach(entity => {
                    textDiv.innerHTML += text.slice(i, entity.begin);
                    const link = document.createElement('a');
                    link.href = `http://127.0.0.1:3000/wiki?id=${entity.wiki_id}`;
                    link.textContent = entity.mention;
                    textDiv.appendChild(link);
                    i = entity.end;
                });
                textDiv.innerHTML += text.slice(i);
                results_table.appendChild(textDiv);
                
                results_sentiment.appendChild(chart);
                
            })
            .catch(error => console.error('Error fetching search results:', error));
    }
});
```
