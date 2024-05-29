import * as d3 from "https://cdn.jsdelivr.net/npm/d3@6/+esm";

export async function createForceGraph(wikiId, onClick) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/graph?id=${wikiId}`);
        const data = await response.json();

        console.log('Fetched data:', data);  // Debugging line

        // Check if data has nodes and links
        if (!data.nodes || !data.links) {
            throw new Error("Data format error: 'nodes' or 'links' is missing");
        }

        const nodes = data.nodes.map(d => ({
            id: d.id,
            title: d.name,  // Ensure you use the correct property name
            sentiment: +d.sentiment
        }));

        const links = data.links.map(d => ({
            source: d.source,
            target: d.target,
            thickness: +d.thickness,
            weight: +d.weight
        }));

        const graph = ForceGraph({
            nodes,
            links
        }, {
            nodeId: d => d.id,
            nodeGroup: d => d.sentiment > 0 ? "positive" : "negative",
            nodeTitle: d => `${d.title}\nSentiment: ${d.sentiment}`,
            linkStrokeWidth: l => l.thickness,
            width: 800,
            height: 600,
            onClick: onClick // Pass the click handler
        });

        return graph;
    } catch (error) {
        console.error('Error in createForceGraph:', error);
        throw error;  // Rethrow the error after logging it
    }
}

// Define the ForceGraph function
function ForceGraph({nodes, links}, options = {}) {
    let {
        nodeId = d => d.id,
        nodeGroup,
        nodeGroups,
        nodeTitle,
        nodeFill = "currentColor",
        nodeStroke = "#fff",
        nodeStrokeWidth = 1.5,
        nodeStrokeOpacity = 1,
        nodeRadius = 5,
        nodeStrength,
        linkSource = ({source}) => source,
        linkTarget = ({target}) => target,
        linkStroke = "#999",
        linkStrokeOpacity = 0.6,
        linkStrokeWidth = 1.5,
        linkStrokeLinecap = "round",
        linkStrength,
        colors = d3.schemeTableau10,
        width = 640,
        height = 400,
        invalidation,
        onClick // Add onClick option
    } = options;

    const N = d3.map(nodes, nodeId).map(intern);
    const G = nodeGroup == null ? null : d3.map(nodes, nodeGroup).map(intern);
    const T = nodeTitle == null ? null : d3.map(nodes, nodeTitle);
    const LS = d3.map(links, linkSource).map(intern);
    const LT = d3.map(links, linkTarget).map(intern);
    const W = typeof linkStrokeWidth !== "function" ? null : d3.map(links, linkStrokeWidth);
    const L = typeof linkStroke !== "function" ? null : d3.map(links, linkStroke);

    nodes = d3.map(nodes, (_, i) => ({id: N[i], title: nodes[i].title, sentiment: nodes[i].sentiment}));
    links = d3.map(links, (_, i) => ({source: LS[i], target: LT[i], thickness: links[i].thickness, weight: links[i].weight}));

    if (G && nodeGroups === undefined) nodeGroups = d3.sort(G);

    const color = nodeGroup == null ? null : d3.scaleOrdinal(nodeGroups, colors);

    const forceNode = d3.forceManyBody();
    const forceLink = d3.forceLink(links).id(({index: i}) => N[i]);
    if (nodeStrength !== undefined) forceNode.strength(nodeStrength);
    if (linkStrength !== undefined) forceLink.strength(linkStrength);

    const simulation = d3.forceSimulation(nodes)
        .force("link", forceLink)
        .force("charge", forceNode)
        .force("center", d3.forceCenter())
        .on("tick", ticked);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

    const link = svg.append("g")
        .attr("stroke", typeof linkStroke !== "function" ? linkStroke : null)
        .attr("stroke-opacity", linkStrokeOpacity)
        .attr("stroke-width", typeof linkStrokeWidth !== "function" ? linkStrokeWidth : null)
        .attr("stroke-linecap", linkStrokeLinecap)
        .selectAll("line")
        .data(links)
        .join("line");

    const node = svg.append("g")
        .attr("fill", nodeFill)
        .attr("stroke", nodeStroke)
        .attr("stroke-opacity", nodeStrokeOpacity)
        .attr("stroke-width", nodeStrokeWidth)
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", nodeRadius)
        .call(drag(simulation))
        .on("click", onClick); // Add click event listener

    if (W) link.attr("stroke-width", ({index: i}) => W[i]);
    if (L) link.attr("stroke", ({index: i}) => L[i]);
    if (G) node.attr("fill", ({index: i}) => color(G[i]));
    if (T) node.append("title").text(({index: i}) => T[i]);
    if (invalidation != null) invalidation.then(() => simulation.stop());

    function intern(value) {
        return value !== null && typeof value === "object" ? value.valueOf() : value;
    }

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    }

    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    return Object.assign(svg.node(), {scales: {color}});
}
