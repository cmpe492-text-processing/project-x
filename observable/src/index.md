---
title: 'Project X'
---

<div style="display: flex; justify-content: center; align-items: center; height: 20vh;">
  <input type="text" id="search-bar" placeholder="Enter search term..." style="width: 100%; padding: 10px; font-size: 16px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
</div>

<script>
document.getElementById('search-bar').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        const query = event.target.value;
        fetch(`http://localhost:8080/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Search results:', data);

            })
        .catch(error => console.error('Error fetching data:', error));
    }
});
</script>
