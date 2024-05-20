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
<div id="search-results" style="padding: 20px;"></div>
<div id="results"></div>

<script>
document.getElementById('search-bar').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        const query = event.target.value;
        fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Search results:', data);
                const results = document.getElementById('results');
                results.innerHTML = '';

                const scores = data.scores;
                const scoreDiv = document.createElement('div');
                scoreDiv.innerHTML = `
                    <h2>Sentiment scores</h2>
                    <div style="width: 100%; text-align: left;">
                        <div style="height: 30px; margin: 5px 0; background-color: green; color: white; text-align: left; line-height: 30px; width: ${scores.pos * 50 + 10}%; max-width: 100%;">Positive: ${scores.pos}</div>
                        <div style="height: 30px; margin: 5px 0; background-color: red; color: white; text-align: left; line-height: 30px; width: ${scores.neg * 50 + 10}%; max-width: 100%;">Negative: ${scores.neg}</div>
                        <div style="height: 30px; margin: 5px 0; background-color: gray; color: white; text-align: left; line-height: 30px; width: ${scores.neu * 50 + 10}%; max-width: 100%;">Neutral: ${scores.neu}</div>
                        <div style="height: 30px; margin: 5px 0; background-color: ${scores.compound > 0 ? `green` : `red`}; color: white; text-align: left; line-height: 30px; width: ${Math.abs(scores.compound) * 50 + 10}%; max-width: 100%;">Compound: ${scores.compound}</div>
                    </div>
                    <br></br>
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
                    link.href = `http://127.0.0.1:3000/wiki?id=${entity.wiki_id}`;
                    link.textContent = entity.mention;
                    textDiv.appendChild(link);
                    i = entity.end;
                });
                textDiv.innerHTML += text.slice(i);
                results.appendChild(textDiv);
            })
            .catch(error => console.error('Error fetching search results:', error));
    }
});
</script>
