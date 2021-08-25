import * as d3 from "d3"

function init(results) {

	var data = results["sheets"]['data']

	console.log(data)
  
	var dataKeys = Object.keys(data[0])

	var xVar = dataKeys[4]
	var yVar = dataKeys[0]
	var seventies = dataKeys[3]

	const container = d3.select("#graphicContainer")
	const context = d3.select("#State-lollipops")

	var today = new Date();

	var options = { day: 'numeric', month: 'long', year: 'numeric' };

	var formatted_date = today.toLocaleString('en-AU', options)

	context.select("#chartTitle").html(`How many days until <b style="color:#d61d00">70%</b> and <b style="color:#e6711b">80%</b> of the 16+ population are fully vaccinated`)
	context.select("#subTitle").html(`Based on the current seven day average of second doses for each state or territory. Last updated ${formatted_date}.`)
	context.select("#sourceText").html('| Sources: CovidLive.com.au, Guardian analysis')

	var isMobile;
	var windowWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);

	var line_stroke_width = 10
	var lolli_r = 10
	var days_offset = 15	
	var circle_stroke_width = 3
	var font_size = 10

	if (windowWidth < 610) {
			isMobile = true;
	}	

	if (windowWidth >= 610){
			isMobile = false;
	}


	if (isMobile == true){
		line_stroke_width = line_stroke_width/3
		lolli_r = lolli_r/3
		days_offset = days_offset/3
		circle_stroke_width = circle_stroke_width/3
		font_size = font_size/2
	}

	var width = document.querySelector("#graphicContainer").getBoundingClientRect().width
	var height = width*0.6				
	var margin = {top: 0, right: 50, bottom: 20, left: 30}

	width = width - margin.left - margin.right;
	height = height - margin.top - margin.bottom;

	
    context.select("#graphicContainer svg").remove();
    
    var chartKey = context.select("#graphicContainer").select("#chartKey");
	chartKey.html("");

	var svg = context.select("#graphicContainer").append("svg")
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
	


	var x = d3.scaleTime()
	.range([0, width])
	.domain([today, dateMax])


	const xTicks = isMobile ? 4 : 6

	var xAxis;

	if (isMobile) {
		xAxis = d3.axisBottom(x)
		.ticks(xTicks)
		.tickFormat(d3.timeFormat('%b'))
	}

	else {
		xAxis = d3.axisBottom(x)
		.ticks(xTicks)
		.tickFormat(d3.timeFormat('%b'))
	}



	features.append("g")
	.attr("class","x")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis)
	.selectAll("text")
	// .attr("transform", "translate(-10,0)rotate(-45)")
	.style("text-anchor", "middle");

	// Y axis
	var y = d3.scaleBand()
	.range([0, height])
	.domain(data.map((d) => d[yVar]))
	.padding(1);

	// var thingo = data.map((d) => d[yVar])

	// console.log(thingo)

	features.append("g")
	.attr("class","y")
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
		.attr("stroke-width",line_stroke_width)


	features.selectAll("mycircle")
		.data(data)
		.enter()
		.append("circle")
		.attr("cx", function(d) { return x(d[xVar]); })
		.attr("cy", function(d) { return y(d[yVar]); })
		.attr("r", lolli_r.toString())
		.style("fill", "#e6711b")
		.attr("stroke", "#94b1ca")
		.attr("stroke-width",circle_stroke_width)


	features.selectAll("mycircle")
		.data(data)
		.enter()
		.append("circle")
		.attr("cx", function(d) { return x(d[seventies]); })
		.attr("cy", function(d) { return y(d[yVar]); })
		.attr("r", lolli_r.toString())
		.style("fill", "#d61d00")
		.attr("stroke", "#94b1ca")
		.attr("stroke-width",circle_stroke_width)


data.forEach(function (d) {
	features.append("text")
	.attr("x", x(d[seventies]))
	.attr("text-anchor", "middle")
	.attr("y", y(d[yVar]) - days_offset)
	// .attr("class", "keyLabel").text(Math.round(min))
	.attr("class", "keyLabel").text(d["70days"])
	.attr("font-size", font_size);

	features.append("text")
	.attr("x", x(d[xVar]))
	.attr("text-anchor", "middle")
	.attr("y", y(d[yVar]) - days_offset)
	// .attr("class", "keyLabel").text(Math.round(min))
	.attr("class", "keyLabel").text(d["80days"])
	.attr("font-size", font_size);

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

