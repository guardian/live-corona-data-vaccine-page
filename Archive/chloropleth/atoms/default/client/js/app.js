import * as topojson from "topojson"
import * as d3 from "d3"
import { color } from "d3";





var target = "#graphicContainer";

function makeMap(world, feed) {
	/// Insert chart title, standfirst, source etc.

    var dates = feed.map(a => a.date)

    var latest_date = d3.max(dates)

    var final = {}
    var country_lookup = {}
    feed.forEach(d => final[d.iso_code] = d.total_vaccinations_per_hundred)
    feed.forEach(d => country_lookup[d.iso_code] = d.location)

    var mapped = feed.map(a => a.total_vaccinations_per_hundred)

    var max = d3.max(mapped)
    var min = d3.min(mapped)
    

	d3.select(".interactive-wrapper")
	.style("background-color", 'white')

	d3.select("#chartTitle").text("The global vaccine rollout")

	d3.select("#subTitle").text(`Countries are grouped into quantiles by the number of vaccinations per hundred people.
    Last updated ${latest_date}.`)

	d3.select("#sourceText").text("| Source: Our World in Data")

	var countries = topojson.feature(world, world.objects.countries);

	var isMobile;
	var windowWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);

	if (windowWidth < 610) {
			isMobile = true;
	}	

	if (windowWidth >= 610){
			isMobile = false;
	}

	var width = document.querySelector(target).getBoundingClientRect().width
	var height = width * 0.65;					
	var margin = {top: 10, right: 10, bottom: 10, left:10};

	width = width - margin.left - margin.right,
    height = height - margin.top - margin.bottom;
   
	var projection = d3.geoMercator()
                .center([0,27])
                .scale(width * 0.15)
                // .rotate([-155,-10])
				.translate([width/2,height/2+ 40]); 
 
	var path = d3.geoPath(projection);
		

	d3.select("#graphicContainer svg").remove();

	var svg = d3.select(target).append("svg")
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
				.attr("id", "svg")
				.attr("overflow", "hidden");					

	var features = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var tipText = `Hover over country for data.`


var tooltip = d3.select(target).append("div")
.attr("class", "tooltip")
.style("position", "absolute")
.style("visibility", "hidden")
.style("top", "10px")
.style("left", "170px");

	const g= features.append("g");
    let mouseOver = function(d, i) {
        console.log(d)
        console.log(i)
        d3.selectAll(".Country")
          .transition()
          .duration(200)
          .style("opacity", .5)
        d3.select(this)
          .transition()
          .duration(200)
          .style("opacity", 1)
          .style("stroke", "black")
        if (country_lookup[i.properties.ADM0_A3] == null){
            d3.select(".tooltip").html("No data available").style("visibility", "visible")
        } else {
            d3.select(".tooltip").html(`<b>${country_lookup[i.properties.ADM0_A3]}</b>: ${final[i.properties.ADM0_A3]} per hundred`).style("visibility", "visible").style("stroke", "none")};
           }
    
      let mouseLeave = function(d) {
        d3.selectAll(".Country")
          .transition()
          .duration(200)
          .style("opacity", .8)
        d3.select(this)
          .transition()
          .duration(200)
          .style("stroke", "transparent")
        d3.select(".tooltip").style("visibility", "hidden")
      }


    var colorScale = d3.scaleSequentialQuantile([...mapped.values()], d3.interpolateBlues)

	g.append("g")
	.selectAll("path")
	.data(countries.features)
	.enter()
	.append("path")
	.attr("d", path)
    .attr("class",function(d){ return "Country" })
    .attr("Vaccinations", function(d){ 
        var count = final[d.properties.ADM0_A3] || 0
        return count })
    .attr("Name", function(d){
        var name = country_lookup[d.properties.ADM0_A3]
        return name})
	// .attr("title", d => d.properties.ISO_A3)
	// .attr("fill", "lightgrey")
    .attr("fill", function(d){
        var count = final[d.properties.ADM0_A3] || 0
        // console.log(d.properties.ADM0_A3)

        return colorScale(count)

        // console.log(d.properties.ADM0_A3)
        // d.total = feed.get(d.properties.ADM0_A3)
        // console.log(d.total)
    })
    .on("mouseover", mouseOver )
    .on("mouseleave", mouseLeave );

	g.append("path")
	.datum(topojson.mesh(world, world.objects.countries, (a, b) => a !== b))
	.attr("fill", "none")
	.attr("stroke", "white")
	.attr("stroke-linejoin", "round")
    
	.attr('d', path)




    // box.append("rect")
    // .attr("fill", "pink")
    // .attr("opacity", 0.5);

    // features.append("text")
    // .attr("x", width)
    // .attr("text-anchor", "end")
    // .attr("y", 20)
    // .text(tipText);

    // var quantiles = d3.quantile(colorScale.domain())

    // console.log(colorScale.domain())

    // console.log(d3.quantile(mapped, 0))
    // console.log(d3.quantile(mapped, 0.25))
    // console.log(d3.quantile(mapped, 0.5))
    // console.log(d3.quantile(mapped, 0.75))
    // console.log(d3.quantile(mapped, 1))

    var keyColours = [colorScale(d3.quantile(mapped, 0)), colorScale(d3.quantile(mapped, 0.25)),
        colorScale(d3.quantile(mapped, 0.5)), colorScale(d3.quantile(mapped, 0.75)), colorScale(d3.quantile(mapped, 1))]

    
    
    
    var keyWidth = 150
    var keySvg = features.append("svg")
    .attr("width", keyWidth)
    .attr("height", "40px")
    .attr("id", "keySvg")
    // .attr("transform", "translate(" + margin.left + "," + height + ")")

    var keySquare = keyWidth / 5;

    keyColours.forEach(function(d, i) {

    keySvg.append("rect")
        .attr("x", (keySquare * i) + 2) 
        .attr("y", 0)
        .attr("width", keySquare)
        .attr("height", 7)
        .attr("fill", d)
        .attr("stroke", "#dcdcdc")
})

    keySvg.append("text")
        .attr("x", 0)
        .attr("text-anchor", "start")
        .attr("y", 20)
        // .attr("class", "keyLabel").text(Math.round(min))
        .attr("class", "keyLabel").text("Less")

    keySvg.append("text")
        .attr("x", keyWidth)
        .attr("text-anchor", "end")
        .attr("y", 20)
        // .attr("class", "keyLabel").text(Math.round(max))
        .attr("class", "keyLabel").text("More")


}



var q = Promise.all([d3.json("<%= path %>/countries@1.json"),
					d3.json("https://interactive.guim.co.uk/covidfeeds/world-vaccine-chloropleth")])

					.then(([countries, feed]) => {
						
						makeMap(countries, feed)
						var to=null
						var lastWidth = document.querySelector(target).getBoundingClientRect()
						window.addEventListener('resize', function() {
							var thisWidth = document.querySelector(target).getBoundingClientRect()
							if (lastWidth != thisWidth) {
								window.clearTimeout(to);
								to = window.setTimeout(function() {

										makeMap(countries, feed)

									}, 500)
				}
			})
        });