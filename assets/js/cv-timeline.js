/* CV Timeline — Horizontal Gantt-style layout with D3.js v7 */
/* Adapted from martisak/resume (MIT) for Hugo + Coder theme */

(function () {
  "use strict";

  if (!window.timelineData || !window.timelineData.length) return;

  // Parse date strings as noon local time to avoid timezone-related off-by-one-day shifts
  function parseDate(s) {
    if (!s) return null;
    var parts = s.split("-");
    return new Date(+parts[0], +parts[1] - 1, +parts[2], 12, 0, 0);
  }

  var dataset = window.timelineData.slice().sort(function (a, b) {
    return d3.ascending(a.startdate, b.startdate);
  });

  var container = d3.select("#timeline");
  var LANE_HEIGHT = 28;
  var LANE_PAD = 4;
  var AXIS_HEIGHT = 24;
  var MIN_BAR_WIDTH = 8; // minimum bar width so tiny periods are still hoverable
  var MARGIN = { top: 10, right: 20, bottom: AXIS_HEIGHT + 10, left: 20 };
  var x, svg, tooltip;
  var PRESENT = new Date(new Date().getFullYear() + 1, 0, 1); // Jan 1 next year = "Present"

  /* ---- Palette: read once from the design tokens (tokens.css) ---- */
  var tokens = getComputedStyle(document.documentElement);
  function token(name) { return tokens.getPropertyValue(name).trim(); }
  var RED = token("--red"), YELLOW = token("--yellow"), BLUE = token("--blue");
  var BLACK = token("--black"), WHITE = token("--white");

  /* Label ink: black on yellow, white on everything else, so text stays legible. */
  function inkOn(fill) { return fill === YELLOW ? BLACK : WHITE; }
  /* Education is blue, work red, side work (writing, advising, tutoring) yellow. */
  function laneColor(d) {
    if (d.type === "education") return BLUE;
    return d.lane === "side" ? YELLOW : RED;
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
    var fmtMonth = d3.timeFormat("%b");
    var fmtYear = d3.timeFormat("%Y");
    var start = parseDate(d.startdate);
    var sm = fmtMonth(start), sy = fmtYear(start);

    if (!d.enddate) return sm + " " + sy + " \u2013 Present";

    var end = parseDate(d.enddate);
    var em = fmtMonth(end), ey = fmtYear(end);

    if (sy === ey) return sm + " \u2013 " + em + " " + sy;
    return sm + " " + sy + " \u2013 " + em + " " + ey;
  }

  function scrollToEntry(d) {
    var idx = dataset.indexOf(d);
    var target = document.getElementById("target_" + idx);
    if (!target) return;
    var top = target.getBoundingClientRect().top + window.pageYOffset - 20;
    window.scrollTo({ top: top, behavior: "smooth" });
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

    x = d3.scaleTime()
      .domain([minDate, maxDate])
      .range([0, width]);

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

    // Time axis — every year if wide enough
    var axisG = g.append("g")
      .attr("class", "time-axis")
      .attr("transform", "translate(0," + (numLanes * (LANE_HEIGHT + LANE_PAD) + 4) + ")");

    var fmtYear = d3.timeFormat("%Y");
    var presentYear = PRESENT.getFullYear();
    var axis = d3.axisBottom(x)
      .ticks(d3.timeYear.every(1))
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

    // Tooltip (appended to body so it's not clipped by overflow)
    tooltip = d3.select("body").append("div").attr("class", "tl-tooltip");

    // Bars
    var bars = g.selectAll(".tl-bar")
      .data(dataset)
      .enter()
      .append("g")
      .attr("class", "tl-bar");

    bars.append("rect")
      .attr("class", "bar-rect")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (LANE_HEIGHT + LANE_PAD); })
      .attr("height", LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return x(parseDate(d.startdate)); })
      .attr("width", 0)
      .on("click", function (event, d) { scrollToEntry(d); })
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

    // Detail sections
    buildSection("#experience", "job");
    buildSection("#education", "education");

    // Move honors/publications into the education column (honors first)
    var eduCol = document.getElementById("education");
    var honors = document.getElementById("honors");
    if (honors && eduCol) eduCol.appendChild(honors);
    var pubs = document.getElementById("publications");
    if (pubs && eduCol) eduCol.appendChild(pubs);

    observeEntries();
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

    // Keep tooltip on screen
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

  /* ---- Detail sections ---- */
  function buildSection(selector, type) {
    var filtered = dataset
      .filter(function (d) { return d.type === type; })
      .sort(function (a, b) { return d3.descending(a.startdate, b.startdate); });

    var section = d3.select(selector);
    var entries = section.selectAll("div.cv-entry")
      .data(filtered)
      .enter()
      .append("div")
      .attr("class", "cv-entry");

    var title = entries.append("h3")
      .attr("id", function (d) { return "target_" + dataset.indexOf(d); });

    var logoLink = title.append("a")
      .attr("href", function (d) { return d.url; })
      .attr("target", "_blank")
      .attr("rel", "noopener noreferrer");

    logoLink.append("img")
      .attr("class", "cv-entry-logo")
      .attr("src", function (d) { return "/" + d.logo; })
      .attr("alt", function (d) { return d.shorttitle + " logo"; })
      .attr("width", 20)
      .attr("height", 20);

    title.append("b").html(function (d) { return getDate(d); });
    title.append("a")
      .attr("href", function (d) { return d.url; })
      .attr("target", "_blank")
      .attr("rel", "noopener noreferrer")
      .html(function (d) { return d.title; });

    entries.each(function (d) {
      if (d.summary) {
        d3.select(this).append("p")
          .attr("class", "cv-summary")
          .text(d.summary);
      }
    });

    entries.append("div")
      .attr("class", "description collapsed")
      .html(function (d) { return d.description; });

    entries.append("button")
      .attr("class", "learn-more")
      .attr("type", "button")
      .attr("aria-expanded", "false")
      .text("Learn more")
      .on("click", function () {
        var entry = this.parentNode;
        var desc = entry.querySelector(".description");
        var isCollapsed = desc.classList.contains("collapsed");
        desc.classList.toggle("collapsed");
        this.textContent = isCollapsed ? "Show less" : "Learn more";
        this.setAttribute("aria-expanded", String(isCollapsed));
      });
  }

  /* ---- Expand button ---- */
  function addExpandButton() {
    container.select(".timeline-expand-btn").remove();
    var btn = container.append("button")
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
        .ticks(d3.timeYear.every(1))
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
      .attr("class", "bar-rect")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (MODAL_LANE_HEIGHT + MODAL_LANE_PAD); })
      .attr("height", MODAL_LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return mx(parseDate(d.startdate)); })
      .attr("width", function (d) { return modalBarWidth(d); })
      .on("click", function (event, d) {
        closeModal();
        scrollToEntry(d);
      })
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

  /* ---- Resize ---- */
  function resize() {
    // Remove old elements
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

    svg = container.insert("svg", ":first-child")
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
    axisG.call(
      d3.axisBottom(x).ticks(d3.timeYear.every(1)).tickFormat(function (d) {
        return d.getFullYear() === presentYearR ? "Present" : fmtYearR(d);
      }).tickSize(4)
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
      .attr("class", "bar-rect")
      .style("fill", function (d) { return laneColor(d); })
      .attr("y", function (d) { return d._lane * (LANE_HEIGHT + LANE_PAD); })
      .attr("height", LANE_HEIGHT)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("x", function (d) { return x(parseDate(d.startdate)); })
      .attr("width", function (d) { return barWidth(d); })
      .on("click", function (event, d) { scrollToEntry(d); })
      .on("mouseover", function (event, d) { showTooltip(event, d); highlight(d); })
      .on("mousemove", function (event) { moveTooltip(event); })
      .on("mouseout", function () { hideTooltip(); resetHighlight(); });

    addExpandButton();
  }

  /* ---- Scroll-triggered fade-in ---- */
  function observeEntries() {
    if (!("IntersectionObserver" in window)) {
      document.querySelectorAll(".cv-entry, #honors, #publications").forEach(function (el) {
        el.classList.add("visible");
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".cv-entry, #honors, #publications").forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ---- Init ---- */
  container.html(""); // replaces the generated static lanes
  draw();
  var resizeTimer;
  d3.select(window).on("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 150);
  });
})();
