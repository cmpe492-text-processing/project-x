---
title: 'Project X'
toc: false
sidebar: false
---

<div style="display: flex; justify-content: center; align-items: center; height: 20vh;">
  <input type="text" id="search-bar" placeholder="Enter search term..." style="width: 100%; padding: 10px; font-size: 16px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
</div>
<div id="search-results" style="padding: 20px;" aria-placeholder="AAAA"></div>


<script>
document.getElementById('search-bar').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        const query = event.target.value;
        fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Search results:', data);
                const results = document.getElementById('search-results');
                results.innerHTML = '';
                
                /*
                    :return:        {
                        text: str,
                        entities: list of {
                                    name: str,
                                    mention: str,
                                    begin: int,
                                    end: int,
                                    confidence: float,
                                    wiki_id: float,
                                    wiki_info: dict
                                    },
                        scores: {
                            compound: float,
                            neu: float,
                            pos: float,
                            neg: float
                            }
                    }
                */ 
                    
                const scores = data.scores;
                const scoreDiv = document.createElement('div');
                scoreDiv.innerHTML = `
                    <h2>Sentiment scores</h2>
                    <ul>
                        <li>Compound: ${scores.compound}</li>
                        <li>Positive: ${scores.pos}</li>
                        <li>Negative: ${scores.neg}</li>
                        <li>Neutral: ${scores.neu}</li>
                    </ul>
                `;
                results.appendChild(scoreDiv);
                
                const text = data.text;
                const entities = data.entities;
                const textDiv = document.createElement('div');
                textDiv.innerHTML = '<h2>Text</h2>';
                let i = 0;
                entities.forEach(entity => {
                    textDiv.innerHTML += text.slice(i, entity.begin);
                    const link = document.createElement('a');
                    link.href = `http://localhost:3000/wiki?id=${entity.wiki_id}`;
                    link.textContent = entity.mention;
                    textDiv.appendChild(link);
                    i = entity.end;
                });
                textDiv.innerHTML += text.slice(i);
                results.appendChild(textDiv);
                });
    }
});
</script>


