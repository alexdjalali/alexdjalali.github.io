// Filters the Writing index by topic. Each .post-item carries data-topics (space-separated keys);
// each .chip carries data-topic. With JS off every post shows and the chips are hidden by CSS.
(function () {
  'use strict';

  var chips = document.querySelectorAll('.chip[data-topic]');
  var items = document.querySelectorAll('.post-item');
  var count = document.getElementById('topic-count');
  if (!chips.length || !items.length) return;

  var NUMERALS = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'],
                  [50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']];

  function roman(n) {
    if (n === 0) return '0';
    var out = '';
    NUMERALS.forEach(function (pair) {
      while (n >= pair[0]) { out += pair[1]; n -= pair[0]; }
    });
    return out;
  }

  function select(topic) {
    var shown = 0;
    items.forEach(function (item) {
      var topics = (item.getAttribute('data-topics') || '').split(' ');
      var match = topic === 'all' || topics.indexOf(topic) !== -1;
      item.hidden = !match;
      if (match) shown += 1;
    });
    chips.forEach(function (chip) {
      chip.setAttribute('aria-pressed', chip.getAttribute('data-topic') === topic ? 'true' : 'false');
    });
    if (count) count.textContent = roman(shown) + ' of ' + roman(items.length) + ' shown';
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () { select(chip.getAttribute('data-topic')); });
  });
  select('all');
})();
