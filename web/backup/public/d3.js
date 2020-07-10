var scale = 1;
var xPosition = 0;
var yPosition = 0;
var svg = d3.select("#container")
	.append("div")
	.attr("id","wrapper")
	.append("svg")
	.call(d3.zoom().on("zoom", function () {
		scale = 1/d3.event.transform.k;
		tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ") scale(" + scale + ",1)");
		svg.attr("transform", "translate(" + d3.event.transform.x + ",0) scale(" + d3.event.transform.k + ",1)");
	}))
	.attr("width", "100%")
	.append("g")

var margin = {top: 20, right: 20, bottom: 30, left: 200},
    width = +document.body.getElementsByTagName('svg')[0].getBoundingClientRect().width - margin.left - margin.right,
    height = +document.body.getElementsByTagName('svg')[0].getBoundingClientRect().height - margin.top - margin.bottom;    //This is a hack and need to ba changed.
    g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var tooltip = svg.append("g")
  .attr("class","tippy")
  .style("display", "none");

var tooltipRect = tooltip.append("rect")
  .attr("width", 50)
  .attr("height", 30)
  .attr("fill", "white")
  .style("opacity", 0.5)

var tooltipText =tooltip.append("text")
  .attr("x", 25)
  .attr("dy", "1.2em")
  .style("text-anchor", "middle")
  .attr("font-size", "20px")
  .attr("font-weight", "bold");

var y = d3.scaleBand()			// x = d3.scaleBand()	
    .rangeRound([0, height])	// .rangeRound([0, width])
    .paddingInner(0.7)
    .align(0.1);

var x = d3.scaleLinear()		// y = d3.scaleLinear()
    .range([0, width]).nice();	// .rangeRound([height, 0]);

var domain = [];
var domainSet = {};

function loadFile() {
  var files = document.querySelector('input[type=file]').files; 
  data = [];
  domain = [];

  d3.select("svg")
	.attr("height", 80 * files.length + "px");
  height = +document.body.getElementsByTagName('svg')[0].getBoundingClientRect().height - margin.top - margin.bottom; 
  y = d3.scaleBand()			// x = d3.scaleBand()	
		.rangeRound([0, height])	// .rangeRound([0, width])
		.paddingInner(0.7)
		.align(0.1);
  var loadState = [];
  for (var i = 0; i < files.length; i ++) {	  
	  let file = files[i];
	  var reader = new FileReader();
	  reader.onload = (e)=> {
		  	var extension = file.name.match(/\.([0-9a-z]+)$/i)[1];
		  	var fileData;
		  	if (extension == 'bed') {
				fileData = d3.dsvFormat(" ").parseRows(e.target.result, function(d, i){
					var data = {};
					if (d.length != 9) {
						return null;
					}
					data.track = d[0];
					data.start = d[1];
					data.end = d[2];
					data.name = d[3];
					data.file = file.name;
					var rgb = d[8].split(',');
					data.color = rgbToHex(parseInt(rgb[0]), parseInt(rgb[1]), parseInt(rgb[2]));
					return data;
				});
			} else if (extension == 'gff' || extension == 'gff3') {
				fileData = d3.dsvFormat("\t").parseRows(e.target.result, function(d, i){
					var data = {};
					if (d.length != 9) {
						return null;
					}
					data.track = d[0];
					data.start = d[3];
					data.end = d[4];
					data.file = file.name;
					data.color = '#6f6f6f'
					return data;
				});		
			}
		    data = data.concat(fileData);
		    loadState.push(true);
		    if (loadState.length == files.length) {
				buildSelector(data);
				removeConnection();
				visualize(data);
			}
	  };
	  if (file) {
		reader.readAsText(file);
	  }
  }
}

function buildSelector(data) {
	var nestedData = d3.nest().key(function(d) { return d.track}).entries(data);
	var select = d3.select("#inputGroupSelect01")
	select.selectAll("option").remove()
	select.selectAll("option")
		.data(nestedData)
		.enter()
		.append("option")
		.attr("value", function(d) {return d.key})
		.text(function(d) {return d.key;});
}
function visualize(data) {
	d3.select('select')
  		.on('change', function() {
			removeConnection();
	    	visualize(data);
		});
	
	var displayKey = d3.select('select').property('value');
	var filtered = data.filter(function(d) {
			 return d.track === displayKey; 
		  });
	
	if (domain.length == 0) {
		domainSet = {};
		filtered.forEach(t => domainSet[t.file] = true);
		domain = Object.keys(domainSet);
		y.domain(domain);
	}
    x.domain([0, d3.max(filtered, function(d) { return +d.end; })]).nice();	// y.domain...
	
	
	g.selectAll("*").remove();
	d3.select('svg').selectAll(".rowName").remove();
	
	g.append("g")
	.selectAll("g")
	.data(filtered)
	.enter()
	.append("rect")
		.attr("y", function(d) { return y(d.file); })	    //.attr("x", function(d) { return x(d.data.State); })
		.attr("x", function(d) { return x(+d.start); })			    //.attr("y", function(d) { return y(d[1]); })	
		.attr("width", function(d) { return x(+d.end) - x(+d.start); })	//.attr("height", function(d) { return y(d[0]) - y(d[1]); })
		.attr("height", y.bandwidth())
		.attr("fill", function(d) {
			return d.color;
		})
		.attr("track", function(d) {return d.name})
		.on("click", function(d) {
			connect(filtered, d.name);
		})
		.on("mouseover", function() { tooltip.style("display", null); })
		.on("mouseout", function() { tooltip.style("display", "none"); })
		.on("mousemove", function(d) {
			xPosition = d3.mouse(this)[0] + margin.left + document.body.getElementsByTagName('svg')[0].getBoundingClientRect().left - (50 * scale)/2 ;
			yPosition = d3.mouse(this)[1] + margin.top + 15;

			tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ") scale(" + scale + ",1)");
			tooltip.select("text").text(d.name);
		});
	
	var nestedData = d3.nest().key(function(d) { return d.file}).entries(filtered);
	
	d3.selectAll("polygon").remove();
	d3.select('svg')
		.append('g')
		.selectAll("text")
		.data(nestedData)
		.enter()
		.append("g")
		.append("text")
		.attr("x", 3 )
		.attr("y", d=> {return margin.top + y(d.key) + y.bandwidth()/2})
		.attr("dy", "5")
	    .attr("font-size", "13px")
	    .attr("font-weight", "bold")
		.attr("class", "rowName")
		.text(d=>d.key)
		.select(function() { return this.parentNode; })
		.append("polygon")
		.attr("fill", "red")
		.attr("stroke", "blue")
		.attr("stroke-width","1") 
		.attr("points", d=> {
			var index = domain.indexOf(d.key);
			if (index > 0) {
				var topY = +(margin.top + y(d.key) + y.bandwidth()/2) - 30
				return "15," +topY + " 3," + (topY+11) + " 27," + (topY+11) 
			}
		})
		.on('click', (d)=> {
			var index = domain.indexOf(d.key);
			swapArrayElements(domain, index, index - 1);
			y.domain(domain);
			visualize(data);
		}) 
		.select(function() { return this.parentNode; })
		.append("polygon")
		.attr("fill", "red")
		.attr("stroke", "blue")
		.attr("stroke-width","1") 
		.attr("points", d=> {
			var index = domain.indexOf(d.key);
			if (index < domain.length - 1) {
				var topY = +(margin.top + y(d.key) + y.bandwidth()/2) + 30
				return "15," +topY + " 3," + (topY-11) + " 27," + (topY-11) 
			}
		})
		.on('click', (d)=> {
			var index = domain.indexOf(d.key);
			swapArrayElements(domain, index, index + 1);
			y.domain(domain);
			visualize(data);
		});
	d3.select('#search-button')
		.on('click', function() {
		connect(filtered, d3.select('#search-input').node().value);
	})
}

function connect(data, name) {
	if (name == null) {
		return;
	}
	removeConnection();
	var rectToConnect = data.filter(function(d) {
			 return d.name == name
		  }).map(function(d) {
				var svgBound = document.body.getElementsByTagName('svg')[0].getBoundingClientRect();
				return {   
						d1: {
								x: x((+d.start + (+d.end))/2) + svgBound.left + margin.left,
								y: y(d.file) + svg.attr('y') + margin.top
						}, d2: { 
								x: x((+d.start + (+d.end))/2) + svgBound.left + margin.left,
								y: (y(d.file) + y.bandwidth()) + margin.top
						}
				}});
	rectToConnect.sort((t1, t2) => {return t1.d2.y - t2.d2.y})
	var links = [];
	for (var i=1; i<rectToConnect.length; i++) {
		links.push([rectToConnect[i-1].d2, rectToConnect[i].d1])
	}
	svg.append("g")
			.attr("class", "pathG")
		.selectAll("g")
		.data(links)
		.enter()
		.append("path")
			.attr("d", function(d) {return "M" + d[0].x + "," + d[0].y + "L" + d[1].x + "," + d[1].y})
			.attr("class", "link");
	
	d3.selectAll("rect")
				.filter(d => {return d!=null && d.name == name})
				.each(function(d,i) {d3.select(this).attr("class", "connected")});
	
	d3.select("svg").on("click",function(){
		var outside = d3.selectAll("rect")
				.filter(d => {return d!=null && d.name == name})
				.filter(equalToEventTarget).empty();
		if (outside) {
			removeConnection();
		}
	});
}

function removeConnection() {
	d3.selectAll("rect")
			.filter(function(d,i) {return d3.select(this).attr("class") == "connected"})
			.each(function(d,i) {d3.select(this).attr("class", "")});
	d3.selectAll(".pathG").remove();
}

function equalToEventTarget() {
    return this == d3.event.target;
}

function swapArrayElements(arr, indexA, indexB) {
  var temp = arr[indexA];
  arr[indexA] = arr[indexB];
  arr[indexB] = temp;
}

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}