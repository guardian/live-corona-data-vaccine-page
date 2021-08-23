import * as d3 from "d3"

function init(results) {

	var data = results["sheets"]['data']

	console.log(data)
  
	var dataKeys = Object.keys(data[0])

	var xVar = dataKeys[4]
	var yVar = dataKeys[0]
	var seventies = dataKeys[3]

	const container = d3.select("#graphicContainer")
	const context = d3.select("#graphicContainer")

	var isMobile;
	var windowWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);

	if (windowWidth < 610) {
			isMobile = true;
	}	

	if (windowWidth >= 610){
			isMobile = false;
	}

	var width = document.querySelector("#graphicContainer").getBoundingClientRect().width
	var height = width*0.6				
	var margin = {top: 20, right: 50, bottom: 50, left:50}

	width = width - margin.left - margin.right;
	height = height - margin.top - margin.bottom;

	
    context.select("#graphicContainer svg").remove();
    
    var chartKey = context.select("#chartKey");
	chartKey.html("");

	var svg = context.append("svg")
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
				.attr("id", "svg")
				.attr("overflow", "hidden");	
				


	var features = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");


	var parseTime = d3.timeParse("%d/%m/%Y")

	var regExp = /\(([^)]+)\)/;
	
	data.forEach(function (d) {
		if (typeof d[xVar] == "string") {
			d["70days"] = d[seventies].split("(")[0].trim();
		}
	  })

	  data.forEach(function (d) {
		if (typeof d[xVar] == "string") {
			d["80days"] = d[xVar].split("(")[0].trim();
		}
	  })
	

	data.forEach(function (d) {
	  if (typeof d[xVar] == "string") {
		var matches = regExp.exec(d[xVar])[1];
		d[xVar] = parseTime(matches)
	  }
	})

	data.forEach(function (d) {
		if (typeof d[seventies] == "string") {
		  var matches = regExp.exec(d[seventies])[1];
		  d[seventies] = parseTime(matches)
		}
	  })

	console.log("data", data)

	const duration = 1000

	var allDates = data.map((d) => d[xVar])

	var dateMax = d3.max(allDates)
	var today = new Date();
	// console.log(today)



	var x = d3.scaleTime()
	.range([0, width])
	.domain([today, dateMax])



	features.append("g")
	.attr("class", "xThingo")
	.attr("transform", "translate(0," + height + ")")
	.call(d3.axisBottom(x))
	.selectAll("text")
	.attr("transform", "translate(-10,0)rotate(-45)")
	.style("text-anchor", "end");

	// Y axis
	var y = d3.scaleBand()
	.range([0, height])
	.domain(data.map((d) => d[yVar]))
	.padding(1);

	// var thingo = data.map((d) => d[yVar])

	// console.log(thingo)

	features.append("g")
	.call(d3.axisLeft(y))


	features.selectAll("myline")
		.data(data)
		.enter()
		.append("line")
		.attr("class", "liners")
		.attr("x1", function(d) { return x(d[xVar]); })
		.attr("x2", x(today))
		.attr("y1", function(d) { return y(d[yVar]); })
		.attr("y2", function(d) { return y(d[yVar]); })
		.attr("stroke", "#94b1ca")
		.attr("stroke-width",10)


	features.selectAll("mycircle")
		.data(data)
		.enter()
		.append("circle")
		.attr("cx", function(d) { return x(d[xVar]); })
		.attr("cy", function(d) { return y(d[yVar]); })
		.attr("r", "10")
		.style("fill", "#e6711b")
		.attr("stroke", "#94b1ca")
		.attr("stroke-width",2)




features.selectAll("mycircle")
.data(data)
.enter()
.append("circle")
.attr("cx", function(d) { return x(d[seventies]); })
.attr("cy", function(d) { return y(d[yVar]); })
.attr("r", "10")
.style("fill", "#d61d00")
.attr("stroke", "#94b1ca")
.attr("stroke-width",2)


data.forEach(function (d) {
	features.append("text")
	.attr("x", x(d[seventies]))
	.attr("text-anchor", "middle")
	.attr("y", y(d[yVar]) - 15)
	// .attr("class", "keyLabel").text(Math.round(min))
	.attr("class", "keyLabel").text(d["70days"]);

	features.append("text")
	.attr("x", x(d[xVar]))
	.attr("text-anchor", "middle")
	.attr("y", y(d[yVar]) - 15)
	// .attr("class", "keyLabel").text(Math.round(min))
	.attr("class", "keyLabel").text(d["80days"]);
  })






}



Promise.all([
	d3.json('https://interactive.guim.co.uk/yacht-charter-data/oz-live-corona-state-vax-table_test.json')
	])
	.then((results) =>  {
		init(results[0])
		var to=null
		var lastWidth = document.querySelector("#graphicContainer").getBoundingClientRect()
		window.addEventListener('resize', function() {
			var thisWidth = document.querySelector("#graphicContainer").getBoundingClientRect()
			if (lastWidth != thisWidth) {
				window.clearTimeout(to);
				to = window.setTimeout(function() {
					    init(results[0])
					}, 100)
			}
		
		})

	});

