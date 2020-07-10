let width = +document.body.getElementsByTagName('canvas')[0].getBoundingClientRect().width;
let height = +document.body.getElementsByTagName('canvas')[0].getBoundingClientRect().height;
const textWidth = 140;
let xDomain, yDomain, x, y, data, filtered, context, toLink, dataContainer;
let windowLeft, windowRight, oriLeft, oriRight, selectedData, interval, canvas, dragIndex, dataBinding;
let horizontalDragging = false;
let verticalDragging = false;
let horizontalStart;
let horizontalEnd;
data = [];
yDomain = [];
let globalFiles = [];


CanvasRenderingContext2D.prototype.fillPolygon = function (pointsArray, fillColor, strokeColor) {
    if (pointsArray.length <= 0) return;
    this.moveTo(pointsArray[0][0], pointsArray[0][1]);
    for (var i = 0; i < pointsArray.length; i++) {
        this.lineTo(pointsArray[i][0], pointsArray[i][1]);
    }
    if (strokeColor != null && strokeColor != undefined)
        this.strokeStyle = strokeColor;

    if (fillColor != null && fillColor != undefined) {
        this.fillStyle = fillColor;
        this.fill();
    }
}

function parseFileData(file, extension, fileName) {
  let format = {
    "bed": {
      "delimiter": "\t",
      "parser": function(d, i) {
          var row = {};
					if (d.length != 9) {
						return null;
					}
          row.strand = d[5];
					row.track = d[0];
					row.start = d[1];
					row.end = d[2];
					row.name = d[3];
					row.file = fileName;
					var rgb = d[8].split(',');
					row.color = rgbToHex(parseInt(rgb[0]), parseInt(rgb[1]), parseInt(rgb[2]));
					return row;
      }
    },
    "gff3": {
      "delimiter": "\t",
      "parser": function(d, i) {
					var row = {};
					if (d.length != 9 || d[2] != 'gene') {
						return null;
					}
					row.track = d[0];
          if (d[8].includes("Name=")) {
            var arr = d[8].split("Name=");
            row.name = arr[arr.length-1];
          }
					row.start = d[3];
					row.end = d[4];
          row.strand = d[6];
					row.file = fileName;
					row.color = '#6f6f6f'
					return row;
      }
    }
  };
  let fileData = d3.dsvFormat(format[extension].delimiter)
                   .parseRows(file, format[extension].parser);
  return fileData;
}

function loadFiles() {
  let files = document.querySelector('input[type=file]').files;
  let loaded = new Array(files.length).fill(false);
  for (let i = 0; i < files.length; i ++) {	  
    let file = files[i];
    let reader = new FileReader();
    yDomain.push(file.name);
    reader.onload = (e)=> {
        let fileExtension = file.name.match(/\.([0-9a-z]+)$/i)[1];
        let fileData= parseFileData(e.target.result, fileExtension, file.name);
        data = data.concat(fileData);
        loaded[i] = true;
        globalFiles = globalFiles.concat(file.name);
        if (loaded.every(t => t === true)) {
          loadFilesCallback(data);
        }
    }
    if (file) {
		  reader.readAsText(file);
	  }
  }
  clear();
  addLoader();
}

function clearFiles() {
  data = [];
  yDomain = [];
  xDomain = [];
  globalFiles = [];
  clear();
  addLoader();
  loadFilesCallback(data);
}

function clear() {
  if (canvas) {
    context.fillStyle = "#fff";
    context.fillRect(0,0, width, height);
  }
  d3.selectAll("svg").selectAll("*").remove();
}

function addLoader() {
  d3.select("#loader-container")
    .append("div")
    .attr("class", "spinner-border")
    .attr("role", "status")
    .style("width", "300px")
    .style("height", "300px")
    .select("span")
    .append("span")
    .attr("class", "sr-only")
    .attr("value", "Loading...");
}

function loadFilesCallback(data) {
  resetWindow();
  buildSelector(data);
  bindData(data);
  bindButtons(data);
  draw();
}

function resetWindow() {
  d3.selectAll(".spinner-border").remove();
  toLink = null;
  selectedData = null;
  windowLeft = null;
  windowRight = null;
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
  
  select.on('change', function() {
      resetWindow();
      bindData(data);
      draw();
  });
}

function bindButtons(data) {
  d3.select("#clear")
        .on("click", function(e){
          clearFiles();
      });
  d3.select("#zoomIn")
      .on("click", function(e){
        if (windowRight - windowLeft > 1000) {
          let range = windowRight - windowLeft;
          windowRight = windowLeft + range / 2;
          bindData(data);
          draw();
        }
      });
  d3.select("#zoomOut")
    .on("click", function(e){
        if ((windowRight - windowLeft < Number.MAX_SAFE_INTEGER / 2) && (windowRight - windowLeft < (oriRight - oriLeft) * 3 / 4)) {
          let range = windowRight - windowLeft;
          windowRight = windowLeft + range * 2;
          bindData(data);
          draw();
        }
    });
  d3.select("#moveLeft")
    .on("click", function(e){
      let range = windowRight - windowLeft;
      let step = Math.max(0, Math.min(range / 10, windowLeft));
      windowLeft = windowLeft - step;
      windowRight = windowRight - step;
      bindData(data);
      draw();
    });
  d3.select("#moveRight")
    .on("click", function(e){
      let range = windowRight - windowLeft;
      let step = Math.max(0, Math.min(range / 10, oriRight - windowRight));
      windowLeft = windowLeft + step;
      windowRight = windowRight + step;
      bindData(data);
      draw();
    });
  d3.select("#reset")
    .on("click", function(e) {
      windowRight = oriRight;
      windowLeft = oriLeft;
      bindData(data);
      draw();
  })
  d3.select("#windowLeft")
    .on("change", function(e) {
      windowLeft = Math.min(Math.max(oriLeft, +d3.select('#windowLeft').property('value')), windowRight - 1);
      bindData(data);
      draw();
    })
  d3.select("#windowRight")
    .on("change", function(e) {
      windowRight = Math.max(windowLeft, Math.min(oriRight, +d3.select('#windowRight').property('value')));
      bindData(data);
      draw();
    })
  
  d3.select("#search-input")
    .on("change", function(e) {
      selectedData = filtered.filter(function(d) {
        return d.name != null && d3.select("#search-input").property("value") != null 
        && d.name.toLowerCase() == d3.select("#search-input").property("value").toLowerCase();
      })[0];
      var foundSet = {};
      data.forEach(d => {
        if (d.name != null && d3.select("#search-input").property("value") != null 
        && d.name.toLowerCase() == d3.select("#search-input").property("value").toLowerCase()) {
          foundSet[d.track] = 1;
        }
      })
      if (Object.keys(foundSet).length > 0) {
        alert("Gene found in: " + Object.keys(foundSet).join(","));
      }
      if (selectedData != null) {
        toLink = filtered.filter(function(d) {
          return d.name === selectedData.name;                             
        });
      }
      bindData(data);
      draw();
  })
}

function bindData(data) {
  var displayKey = d3.select('select').property('value');
	filtered = data.filter(function(d) {
			 return d.track === displayKey && (windowLeft == null || d.end > windowLeft) && (windowRight == null || d.start < windowRight); 
  });
  
  var detachedContainer = document.createElement("custom");

  // Create a d3 selection for the detached container. We won't
  // actually be attaching it to the DOM.
  dataContainer = d3.select(detachedContainer);
  
  if (windowLeft == null) {
    windowLeft = 0;
    oriLeft = 0;
  }
  if (windowRight == null) {
    windowRight = d3.max(filtered, function(d) { return +d.end; });
    oriRight = windowRight;
  }
  xDomain = [windowLeft, windowRight];	// y.domain...
  
  d3.select("#windowLeft").property("value", Math.round(windowLeft));
  d3.select("#windowRight").property("value", Math.round(windowRight));
  
  y = d3.scaleBand()			// x = d3.scaleBand()	
    .rangeRound([0, Math.min(height, 100 * yDomain.length)])	// .rangeRound([0, width])
    .paddingInner(0.7)
    .align(0.1)
    .domain(yDomain);

  x = d3.scaleLinear()		// y = d3.scaleLinear()
    .domain(xDomain)
    .range([textWidth, width - textWidth]).nice();	// .rangeRound([height, 0]);
  
  dataBinding = dataContainer.selectAll("custom.rect")
  .data(filtered, function(d) { return d; });

  dataBinding.enter()
    .append("custom")
    .classed("rect", true)
    .attr("strand", function(d) {return d.strand;})
    .attr("x", function(d) { return x(+d.start);})
    .attr("y", function(d) { return y(d.file);} )
    .attr("width", function(d) { return x(+d.end) - x(+d.start);})
    .attr("height", function(d) { return y.bandwidth()})
    .attr("fillStyle", function(d) {return d.color});
}

function resize() {
  
}

function draw() {
  //clear svg
  let width = +document.body.getElementsByTagName('canvas')[0].getBoundingClientRect().width;
  let height = +document.body.getElementsByTagName('canvas')[0].getBoundingClientRect().height;
  d3.selectAll("svg").selectAll("*").remove();
  
  drawXAxis();
  drawTooltip();
  
  if (selectedData != null) {
    d3.select("#search-input").property("value", selectedData.name);
  } else {
    d3.select("#search-input").property("value", "");
  }
  
  canvas = d3.select("canvas")
        .attr("width", width)
        .attr("height", height)
        .style("transform", "translate(0,60px)");
  
  // clear canvas
  context = canvas.node().getContext("2d");
  context.fillStyle = "#fff";
  context.fillRect(0,0, width, height);
  
  var elements = dataContainer.selectAll("custom.rect");
  elements.each(function(d) {
    var node = d3.select(this);
    context.beginPath();
    //context.fillStyle = node.attr("fillStyle");
    var pstyle = node.attr("fillStyle");
    var px = Number(node.attr("x"));
    var py = Number(node.attr("y"));
    var pwidth = Number(node.attr("width"));
    var pheight = Number(node.attr("height"));
    var pangle = Math.min(20, Math.min(pwidth, 20));
    //(oriRight - oriLeft) / (windowRight - windowLeft)
    var parr;
    if (node.attr("strand") == "-") {
      parr = [[px, py + pheight/2], [px + pangle, py],[px+pwidth, py],[px+pwidth, py+pheight],[px + pangle, py+pheight]];
    } else if (node.attr("strand") == "+") {
      parr = [[px, py], [px + pwidth - pangle, py],[px + pwidth, py + pheight / 2],[px + pwidth - pangle, py + pheight],[px, py + pheight]];
    } else {
      parr = [[py, py],[px + pwidth, py],[px + pwidth, py + pheight],[px, py + pheight]];
    }
    context.fillPolygon(parr, pstyle, pstyle);
//    context.fillStyle = node.attr("fillStyle");
//    context.fillRect(node.attr("x"), node.attr("y"), node.attr("width"), node.attr("height"));
    context.closePath();
  });
  
  if (toLink) {
    link(toLink);
  }
  
  context.fillStyle = "#fff";
  context.fillRect(0,0, textWidth, height);
  
  context.fillStyle = "#fff";
  context.fillRect(x(windowRight),0, width, height);
  
  yDomain.forEach(t => {
    context.font = "12px Helvetica Neue";
    context.fillStyle = "black";
    context.fillText(t, 20, y(t) + y.bandwidth()/2 + 6, textWidth);
  })

  canvas.on("click", onClick);
  canvas.on("mousedown", onMouseDown);
  canvas.on("mouseup", onMouseUp);
  canvas.on("mouseout", onMouseUp);
  window.addEventListener("resize", draw);
}

function drawTooltip() {
  if (selectedData != null && selectedData.name != null) {
    var posY = y(selectedData.file) + y.bandwidth() + 60 + 2;
    var posX = (x(+selectedData.start) + x(+selectedData.end)) / 2 - 50/2;
    var tooltip = d3.select("#tooltip-svg")
      .attr("width", 120)
      .attr("height", 30)
      .attr("transform", "translate(" + posX + "," + posY + ")")
      .append("g")
      .attr("class","tippy")
    
    var tooltipRect = tooltip.append("rect")
      .attr("width", 120)
      .attr("height", 30)
      .attr("fill", "white")
      .style("stroke", "black")
      .style("fill-opacity", 0.5)
      .style("stroke-width", 1);

    var tooltipText =tooltip.append("text")
      .attr("dy", 30/2)
      .attr("dx", 120/2)
      .style("text-anchor", "middle")
      .attr("font-size", "30px")
      .attr("font-weight", "bold")
      .text(selectedData.name);
  }
}

function link(data) {
   data.sort(function(a, b){return y(a.file) - y(b.file)});
   for (let i = 1; i < data.length; i++) {
      context.beginPath();
      context.moveTo((x(+data[i - 1].start) + x(+data[i - 1].end))/2, y(data[i-1].file) + y.bandwidth());
      context.lineTo((x(+data[i].start) + x(+data[i].end))/2, y(data[i].file));
      context.stroke();
      context.closePath();
   }
}

function onMouseDown() {
  var mouse = d3.mouse(this);
  var xClicked = x.invert(mouse[0]);
  dragIndex = Math.round((mouse[1] / y.step()));
  if (dragIndex >= yDomain.length) {
    return; 
  }
  if (mouse[0] <= 0) {
      return;
  } else if ( mouse[0] <= textWidth) {
    verticalDragging = true;
    d3.select(this).style("cursor", "pointer"); 
  } else if ( mouse[0] <= width) {
    horizontalDragging = true;
    horizontalStart = mouse[0];
    d3.select(this).style("cursor", "pointer"); 
  }
  canvas.on("mousemove", onMouseUpdate);
}

function onMouseUp() {
  var mouse = d3.mouse(this);
  if (verticalDragging) {
    verticalDragging = false;
    canvas.on("mousemove", null);
    var index = Math.min(Math.round((mouse[1] / y.step())), yDomain.length - 1);
    var temp = yDomain[index];
    yDomain[index] = yDomain[dragIndex];
    yDomain[dragIndex] = temp;
    y.domain(yDomain);
    bindData(data);
    draw();
    d3.select(this).style("cursor", "default"); 
  } else if (horizontalDragging) {
    horizontalDragging = false;
    canvas.on("mousemove", null);
    horizontalEnd = mouse[0];
    var step;
    if (horizontalEnd >= horizontalStart) {
      step = Math.min(oriRight - windowRight, (horizontalEnd - horizontalStart) * (windowRight - windowLeft) / width);
    } else if (horizontalEnd < horizontalStart) {
      step = Math.max(-windowLeft, (horizontalEnd - horizontalStart) * (windowRight - windowLeft) / width)
    }
    windowLeft = windowLeft + step;
    windowRight = windowRight + step;
    bindData(data);
    draw();
    d3.select(this).style("cursor", "default"); 
  }
}

function onMouseUpdate() {
  if (verticalDragging) {
    mouse = d3.mouse(this);
    context.fillStyle = "#fff";
    context.fillRect(0,0, textWidth, height);

    yDomain.forEach((t, i) => {
      if (i == dragIndex) {
        context.font = "12px Helvetica Neue";
        context.fillStyle = "black";
        context.fillText(t, 20, mouse[1] + y.bandwidth()/2 + 6, textWidth);
      } else {
        context.font = "12px Helvetica Neue";
        context.fillStyle = "black";
        context.fillText(t, 20, y(t) + y.bandwidth()/2 + 6, textWidth);
      }
    })
  }
}

function onClick() {
    if (horizontalStart && horizontalEnd && horizontalStart != horizontalEnd) {
      return;
    }
    var mouse = d3.mouse(this);
    toLink = null;
    selectedData = null;
    
    // map the clicked point to the data space
    var xClicked = x.invert(mouse[0]);
  
    var eachBand = y.step();
    var index = Math.round((mouse[1] / eachBand));
  
    if (mouse[0] > 0 && mouse[0] < textWidth) {
        return;
    }
    if ((mouse[1]< y(y.domain()[index]))  || (mouse[1] > y(y.domain()[index]) + y.bandwidth())) {
      draw();
      return;
    }
    var yClicked = y.domain()[index];
    
    selectedData = filtered.filter(function(d) {
      return d.file === yClicked && d.start <= xClicked && d.end >= xClicked;
    })[0];
    if (selectedData != null && selectedData.name != null) {
      toLink = filtered.filter(function(d) {
        return d.name === selectedData.name;                             
      });
    }
    draw();
}

function drawXAxis() {
  var svg = d3.select("#axis-svg") 
        .attr("width", width)
        .attr("height", height)
        .append("g");
  
  var xAxis = d3.axisTop(x)
      .ticks(10);
  
  var xAxisSvg = svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,20)')
        .call(xAxis);
}

function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function removeFile(e) {
  clear();
  addLoader();
  xDomain = [];
  yDomain = yDomain.filter(function(t) { return t !== e });
  globalFiles = globalFiles.filter(function(t) { return t !== e });
  data = data.filter(function(d){return d.file != e;});
  loadFilesCallback(data);
  updateModal();
}

function updateModal() {
  let modalBody = d3.select("#remove-modal-body");
  modalHtml = "";
  for (let i = 0; i < globalFiles.length; i ++) {	  
    let file = globalFiles[i];
    modalHtml = modalHtml + '<button type="button" class="btn btn-secondary" onclick="removeFile(' + "'" + file + "'" + ')">' + file + '</button>'
  } 
  modalBody.html(modalHtml);
}

$('#removeModal').on('show.bs.modal', function(d) {
  updateModal();
})


