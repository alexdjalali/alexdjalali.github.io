// Mermaid set-up: the palette lives in tokens.css; read it so this file holds no colour literals.
(function() {
  var css = getComputedStyle(document.documentElement);
  function token(name) { return css.getPropertyValue(name).trim(); }
  var red = token('--red'), yellow = token('--yellow'), blue = token('--blue');
  var black = token('--black'), white = token('--white'), grey = token('--ink-3');
  var palette = [blue, red, yellow, black, grey];
  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
      background: 'transparent',
      primaryColor: white,
      primaryTextColor: black,
      primaryBorderColor: black,
      lineColor: black,
      textColor: black,
      pie1: red, pie2: yellow, pie3: blue, pie4: black, pie5: grey,
      pieStrokeColor: white,
      pieOuterStrokeColor: 'transparent',
      pieTitleTextColor: black,
      pieLegendTextColor: black,
      pieSectionTextColor: white,
      pieOpacity: '1',
      xyChart: {
        backgroundColor: 'transparent',
        titleColor: black,
        xAxisLabelColor: black, yAxisLabelColor: black,
        xAxisTitleColor: black, yAxisTitleColor: black,
        xAxisLineColor: black, yAxisLineColor: black,
        xAxisTickColor: black, yAxisTickColor: black,
        plotColorPalette: palette.join(', ')
      },
      quadrant1Fill: white, quadrant2Fill: white, quadrant3Fill: white, quadrant4Fill: white,
      quadrant1TextFill: black, quadrant2TextFill: black, quadrant3TextFill: black, quadrant4TextFill: black,
      quadrantPointFill: red,
      quadrantPointTextFill: black,
      quadrantXAxisTextFill: black, quadrantYAxisTextFill: black,
      quadrantTitleFill: black
    }
  });
})();
