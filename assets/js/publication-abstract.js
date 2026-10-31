/**
 * Publication Abstract Toggle
 *
 * Collapses all .pub-abstract elements on page load and injects per-entry
 * "Abstract" toggle buttons. Follows the same pattern as the CV page's
 * "Learn More" button (see assets/js/cv-timeline.js:290-301).
 */

document.addEventListener("DOMContentLoaded", function () {
  // Query .pub-abstract elements only inside publication list items.
  // The posts list page also uses .pub-abstract for descriptions, but its
  // <li> elements have an onclick attribute (from the template) — exclude those.
  var abstracts = document.querySelectorAll(".cv-list li:not([onclick]) .pub-abstract");

  // If no abstracts on this page, this is a no-op (safe for non-publications pages)
  if (abstracts.length === 0) {
    return;
  }

  // For each abstract span, add collapsed class and insert toggle button
  abstracts.forEach(function (abstractSpan) {
    // Add collapsed class to hide the abstract by default
    abstractSpan.classList.add("collapsed");

    // Give the abstract an id for aria-controls
    if (!abstractSpan.id) {
      abstractSpan.id = "abstract-" + Math.random().toString(36).substr(2, 9);
    }

    // Create the toggle button (semantic <button>, not <a>)
    var toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "abstract-toggle";
    toggle.textContent = "Abstract";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", abstractSpan.id);

    // Attach click handler
    toggle.addEventListener("click", function () {
      var isCollapsed = abstractSpan.classList.contains("collapsed");
      abstractSpan.classList.toggle("collapsed");
      this.textContent = isCollapsed ? "Hide abstract" : "Abstract";
      this.setAttribute("aria-expanded", String(isCollapsed));
    });

    // Insert the toggle button before the bib-link (so Abstract appears first),
    // or before the abstract span if no bib-link exists
    var bibLink = abstractSpan.parentNode.querySelector(".bib-link");
    if (bibLink) {
      bibLink.parentNode.insertBefore(toggle, bibLink);
    } else {
      abstractSpan.parentNode.insertBefore(toggle, abstractSpan);
    }
  });
});
