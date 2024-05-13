---
title: Wiki
toc: false
---
<div id="base" style="padding: 20px;"></div>

```js

const base = document.getElementById('base');
// get the query from the URL


const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get('id');



```

```js
base.innerHTML = id;
```



