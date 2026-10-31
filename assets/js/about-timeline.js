/* About Timeline — Horizontal Gantt-style layout with D3.js v7 */
/* Simplified from cv-timeline.js for location history */

(function () {
  "use strict";

  if (!window.locationData || !window.locationData.length) return;

  // Parse date strings as noon local time to avoid timezone-related off-by-one-day shifts
  function parseDate(s) {
    if (!s) return null;
    var parts = s.split("-");
    return new Date(+parts[0], +parts[1] - 1, +parts[2], 12, 0, 0);
  }

  var dataset = window.locationData.slice().sort(function (a, b) {
    return d3.ascending(a.startdate, b.startdate);
  });

  var container = d3.select("#about-timeline");
  if (container.empty()) return;

  var LANE_HEIGHT = 28;
  var LANE_PAD = 4;
  var AXIS_HEIGHT = 24;
  var MIN_BAR_WIDTH = 8;
  var MARGIN = { top: 10, right: 20, bottom: AXIS_HEIGHT + 10, left: 20 };
  var x, svg, tooltip;
  var PRESENT = new Date(new Date().getFullYear() + 1, 0, 1);

  /* ---- Palette: read once from the design tokens (tokens.css) ---- */
  var tokens = getComputedStyle(document.documentElement);
  function token(name) { return tokens.getPropertyValue(name).trim(); }
  var RED = token("--red"), YELLOW = token("--yellow"), BLUE = token("--blue");
  var BLACK = token("--black"), WHITE = token("--white");

  /* Label ink: black on yellow, white on everything else, so text stays legible. */
  function inkOn(fill) { return fill === YELLOW ? BLACK : WHITE; }
  /* Places cycle red, yellow, blue, black, as on the generated lifeline. */
  function laneColor(d) {
    return [RED, YELLOW, BLUE, BLACK][dataset.indexOf(d) % 4];
  }

  /* ---- Assign swim lanes so overlapping bars stack ---- */
  function assignLanes() {
    var laneEnds = [];
    dataset.forEach(function (d) {
      var start = parseDate(d.startdate);
      var end = d.enddate ? parseDate(d.enddate) : PRESENT;
      var placed = false;
      for (var i = 0; i < laneEnds.length; i++) {
        if (start >= laneEnds[i]) {
          d._lane = i;
          laneEnds[i] = end;
          placed = true;
          break;
        }
      }
      if (!placed) {
        d._lane = laneEnds.length;
        laneEnds.push(end);
      }
    });
    return laneEnds.length;
  }

  function barWidth(d) {
    var end = d.enddate ? parseDate(d.enddate) : PRESENT;
    return Math.max(x(end) - x(parseDate(d.startdate)), MIN_BAR_WIDTH);
  }

  function getDate(d) {
    var fmtYear = d3.timeFormat("%Y");
    var start = parseDate(d.startdate);
    var sy = fmtYear(start);
    if (!d.enddate) return sy + " \u2013 Present";
    var end = parseDate(d.enddate);
    var ey = fmtYear(end);
    if (sy === ey) return sy;
    return sy + " \u2013 " + ey;
  }

  function tickInterval() {
    var minDate = d3.min(dataset, function (d) { return parseDate(d.startdate); });
    var yearSpan = PRESENT.getFullYear() - minDate.getFullYear();
    return yearSpan > 30 ? 5 : yearSpan > 15 ? 2 : 1;
  }

  /* ---- Draw ---- */
  function draw() {
    var numLanes = assignLanes();
    var containerNode = container.node();
    var containerWidth = containerNode.parentElement.clientWidth || containerNode.clientWidth || 600;
    var svgWidth = containerWidth;
    var width = svgWidth - MARGIN.left - MARGIN.right;
    var height = numLanes * (LANE_HEIGHT + LANE_PAD) + MARGIN.top + MARGIN.bottom;

    var minDate = d3.min(dataset, function (d) { return parseDate(d.startdate); });
    var maxDate = PRESENT;

    x = d3.scaleTime().domain([minDate, maxDate]).range([0, width]);

    svg = container.append("svg")
      .attr("width", svgWidth)
      .attr("height", height)
      .attr("class", "timeline-svg");

    var g = svg.append("g")
      .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")");

    // Year grid lines
    var years = d3.timeYears(minDate, maxDate);
    g.selectAll(".grid-line")
      .data(years)
      .enter()
      .append("line")
      .attr("class", "grid-line")
      .attr("x1", function (d) { return x(d); })
      .attr("x2", function (d) { return x(d); })
      .attr("y1", 0)
      .attr("y2", numLanes * (LANE_HEIGHT + LANE_PAD));

    // Time axis
    var axisG = g.append("g")
      .attr("class", "time-axis")
      .attr("transform", "translate(0," + (numLanes * (LANE_HEIGHT + LANE_PAD) + 4) + ")");

    var fmtYear = d3.timeFormat("%Y");
    var presentYear = PRESENT.getFullYear();
    var interval = tickInterval();
    var axis = d3.axisBottom(x)
      .ticks(d3.timeYear.every(interval))
      .tickFormat(function (d) {
        return d.getFullYear() === presentYear ? "Present" : fmtYear(d);
      })
      .tickSize(4);

    axisG.call(axis);

    // Present marker
    g.append("line")
      .attr("class", "present-line")
      .attr("x1", x(PRESENT))
      .attr("x2", x(PRESENT))
      .attr("y1", 0)
      .attr("y2", numLanes * (LANE_HEIGHT + LANE_PAD));

    // Tooltip
    tooltip = d3.select("body").append("div").attr("class", "tl-tooltip");

    // Bars
    var bars = g.selectAll(".tl-bar")
      .data(dataset)
      .enter()
      .append("g")
      .attr("class", "tl-bar");

    bars.append("rect")
      .attr("class", "bar-rect location")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (LANE_HEIGHT + LANE_PAD); })
      .attr("height", LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return x(parseDate(d.startdate)); })
      .attr("width", 0)
      .on("mouseover", function (event, d) { showTooltip(event, d); highlight(d); })
      .on("mousemove", function (event) { moveTooltip(event); })
      .on("mouseout", function () { hideTooltip(); resetHighlight(); })
      .transition()
      .ease(d3.easeCubicOut)
      .duration(800)
      .delay(function (d, i) { return i * 60; })
      .attr("width", function (d) { return barWidth(d); });

    // Expand button
    addExpandButton();
  }

  /* ---- Tooltip ---- */
  function showTooltip(event, d) {
    tooltip
      .html("<strong>" + d.title + "</strong><br>" + getDate(d))
      .style("opacity", 1);
    moveTooltip(event);
  }

  function moveTooltip(event) {
    var left = event.pageX + 14;
    var top = event.pageY - 14;
    var tipNode = tooltip.node();
    var tipWidth = tipNode.offsetWidth;
    var tipHeight = tipNode.offsetHeight;
    if (left + tipWidth > window.innerWidth - 10) {
      left = event.pageX - tipWidth - 14;
    }
    if (top + tipHeight > window.innerHeight + window.pageYOffset - 10) {
      top = event.pageY - tipHeight - 14;
    }
    tooltip.style("left", left + "px").style("top", top + "px");
  }

  function hideTooltip() {
    tooltip.style("opacity", 0);
  }

  /* ---- Highlight ---- */
  function highlight(d) {
    svg.selectAll(".bar-rect")
      .transition().duration(200)
      .style("opacity", function (dd) { return dd === d ? 1 : 0.25; });
  }

  function resetHighlight() {
    svg.selectAll(".bar-rect")
      .transition().duration(300)
      .style("opacity", null);
  }

  /* ---- Expand button ---- */
  function addExpandButton() {
    container.select(".timeline-expand-btn").remove();
    container.append("button")
      .attr("class", "timeline-expand-btn")
      .text("Expand Timeline")
      .on("click", function () { openModal(); });
  }

  /* ---- Modal ---- */
  function openModal() {
    var MODAL_LANE_HEIGHT = 36;
    var MODAL_LANE_PAD = 4;
    var MODAL_LABEL_PAD = 12;
    var MODAL_MARGIN = { top: 16, right: 30, bottom: AXIS_HEIGHT + 16, left: 30 };

    // Create overlay
    var overlay = d3.select("body").append("div")
      .attr("class", "timeline-modal-overlay");

    var modal = overlay.append("div")
      .attr("class", "timeline-modal");

    modal.append("button")
      .attr("class", "timeline-modal-close")
      .html("&times;")
      .on("click", closeModal);

    // Close on backdrop click
    overlay.on("click", function (event) {
      if (event.target === overlay.node()) closeModal();
    });

    // Close on Escape
    function onEscape(event) {
      if (event.key === "Escape") closeModal();
    }
    document.addEventListener("keydown", onEscape);

    var modalTooltip = d3.select("body").append("div").attr("class", "tl-tooltip");

    // Render expanded timeline
    var numLanes = assignLanes();
    var modalNode = modal.node();
    var modalWidth = modalNode.clientWidth - MODAL_MARGIN.left - MODAL_MARGIN.right;
    var modalSvgWidth = modalNode.clientWidth;
    var modalHeight = numLanes * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD) + MODAL_MARGIN.top + MODAL_MARGIN.bottom;

    var minDate = d3.min(dataset, function (d) { return parseDate(d.startdate); });
    var maxDate = PRESENT;

    var mx = d3.scaleTime().domain([minDate, maxDate]).range([0, modalWidth]);

    function modalBarWidth(d) {
      var end = d.enddate ? parseDate(d.enddate) : PRESENT;
      return Math.max(mx(end) - mx(parseDate(d.startdate)), MIN_BAR_WIDTH);
    }

    var interval = tickInterval();

    var msvg = modal.append("svg")
      .attr("width", modalSvgWidth)
      .attr("height", modalHeight)
      .attr("class", "timeline-svg");

    var mg = msvg.append("g")
      .attr("transform", "translate(" + MODAL_MARGIN.left + "," + MODAL_MARGIN.top + ")");

    // Year grid lines
    var years = d3.timeYears(minDate, maxDate);
    mg.selectAll(".grid-line")
      .data(years)
      .enter()
      .append("line")
      .attr("class", "grid-line")
      .attr("x1", function (d) { return mx(d); })
      .attr("x2", function (d) { return mx(d); })
      .attr("y1", 0)
      .attr("y2", numLanes * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD));

    // Time axis
    var maxisG = mg.append("g")
      .attr("class", "time-axis")
      .attr("transform", "translate(0," + (numLanes * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD) + 4) + ")");

    var fmtYear = d3.timeFormat("%Y");
    var presentYear = PRESENT.getFullYear();
    maxisG.call(
      d3.axisBottom(mx)
        .ticks(d3.timeYear.every(interval))
        .tickFormat(function (d) {
          return d.getFullYear() === presentYear ? "Present" : fmtYear(d);
        })
        .tickSize(4)
    );

    // Present marker
    mg.append("line")
      .attr("class", "present-line")
      .attr("x1", mx(PRESENT))
      .attr("x2", mx(PRESENT))
      .attr("y1", 0)
      .attr("y2", numLanes * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD));

    // Bars
    var mbars = mg.selectAll(".tl-bar")
      .data(dataset)
      .enter()
      .append("g")
      .attr("class", "tl-bar");

    mbars.append("rect")
      .attr("class", "bar-rect location")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD); })
      .attr("height", MODAL_LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return mx(parseDate(d.startdate)); })
      .attr("width", function (d) { return modalBarWidth(d); })
      .on("mouseover", function (event, d) {
        modalTooltip
          .html("<strong>" + d.title + "</strong><br>" + getDate(d))
          .style("opacity", 1);
        modalTooltip.style("left", (event.pageX + 14) + "px").style("top", (event.pageY - 14) + "px");
        msvg.selectAll(".bar-rect")
          .transition().duration(200)
          .style("opacity", function (dd) { return dd === d ? 1 : 0.25; });
      })
      .on("mousemove", function (event) {
        modalTooltip.style("left", (event.pageX + 14) + "px").style("top", (event.pageY - 14) + "px");
      })
      .on("mouseout", function () {
        modalTooltip.style("opacity", 0);
        msvg.selectAll(".bar-rect")
          .transition().duration(300)
          .style("opacity", null);
      });

    // Labels in modal — show if they fit
    var mlabels = mbars.append("text")
      .attr("class", "bar-label")
      .attr("x", function (d) { return mx(parseDate(d.startdate)) + 6; })
      .attr("y", function (d) { return d._lane * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD) + MODAL_LANE_HEIGHT / 2; })
      .attr("dy", "0.35em")
      .style("font-size", "12px")
      .style("fill", function (d) { return inkOn(laneColor(d)); })
      .style("pointer-events", "none")
      .style("user-select", "none")
      .text(function (d) { return d.shorttitle; });

    mlabels.each(function (d) {
      var textWidth = this.getComputedTextLength();
      var bw = modalBarWidth(d);
      if (textWidth + MODAL_LABEL_PAD > bw) {
        d3.select(this).remove();
      }
    });

    function closeModal() {
      document.removeEventListener("keydown", onEscape);
      modalTooltip.remove();
      overlay.remove();
    }
  }

  /* ---- Resize / Redraw ---- */
  function redraw() {
    container.select("svg").remove();
    container.select(".timeline-expand-btn").remove();
    if (tooltip) tooltip.remove();

    var numLanes = assignLanes();
    var containerNode = container.node();
    var containerWidth = containerNode.parentElement.clientWidth || containerNode.clientWidth || 600;
    var svgWidth = containerWidth;
    var width = svgWidth - MARGIN.left - MARGIN.right;
    var height = numLanes * (LANE_HEIGHT + LANE_PAD) + MARGIN.top + MARGIN.bottom;

    var minDate = d3.min(dataset, function (d) { return parseDate(d.startdate); });
    var maxDate = PRESENT;

    x = d3.scaleTime().domain([minDate, maxDate]).range([0, width]);

    svg = container.append("svg")
      .attr("width", svgWidth)
      .attr("height", height)
      .attr("class", "timeline-svg");

    var g = svg.append("g")
      .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")");

    var years = d3.timeYears(minDate, maxDate);
    g.selectAll(".grid-line")
      .data(years)
      .enter()
      .append("line")
      .attr("class", "grid-line")
      .attr("x1", function (d) { return x(d); })
      .attr("x2", function (d) { return x(d); })
      .attr("y1", 0)
      .attr("y2", numLanes * (LANE_HEIGHT + LANE_PAD));

    var axisG = g.append("g")
      .attr("class", "time-axis")
      .attr("transform", "translate(0," + (numLanes * (LANE_HEIGHT + LANE_PAD) + 4) + ")");

    var fmtYearR = d3.timeFormat("%Y");
    var presentYearR = PRESENT.getFullYear();
    var interval = tickInterval();
    axisG.call(
      d3.axisBottom(x)
        .ticks(d3.timeYear.every(interval))
        .tickFormat(function (d) {
          return d.getFullYear() === presentYearR ? "Present" : fmtYearR(d);
        })
        .tickSize(4)
    );

    g.append("line")
      .attr("class", "present-line")
      .attr("x1", x(PRESENT))
      .attr("x2", x(PRESENT))
      .attr("y1", 0)
      .attr("y2", numLanes * (LANE_HEIGHT + LANE_PAD));

    tooltip = d3.select("body").append("div").attr("class", "tl-tooltip");

    var bars = g.selectAll(".tl-bar")
      .data(dataset)
      .enter()
      .append("g")
      .attr("class", "tl-bar");

    bars.append("rect")
      .attr("class", "bar-rect location")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (LANE_HEIGHT + LANE_PAD); })
      .attr("height", LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return x(parseDate(d.startdate)); })
      .attr("width", function (d) { return barWidth(d); })
      .on("mouseover", function (event, d) { showTooltip(event, d); highlight(d); })
      .on("mousemove", function (event) { moveTooltip(event); })
      .on("mouseout", function () { hideTooltip(); resetHighlight(); });

    addExpandButton();
  }

  /* ---- Init ---- */
  container.html(""); // replaces the generated static lanes
  draw();

  var resizeTimer;
  d3.select(window).on("resize.about", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(redraw, 150);
  });

})();
