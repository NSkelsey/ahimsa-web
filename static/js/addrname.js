
function addrname(selection) {
/* Returns an svg box mapping a color to the addr. The selection is a d3
 * DOM element, which is used to extract the relevant data.
 * */
    var w = 15, // width
        h = 15, // height
        r = 2;  // radius

    var addr = selection.select('a').attr('href').split('/')[2];

    selection.append('svg')
        .attr('width', w)
        .attr('height', h)
      .append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('rx', r)
        .attr('ry', r)
        .attr('width', w)
        .attr('height', h)
        .attr('fill', colorAddr(addr));
}

function colorAddr(address) {
/* Takes a bitcoin address and returns a rgb() color, the hash algorithm used is 
 * MD5. We compress the output of MD5 even further to map it into the rgb colorspace.
 * The current function takes the md5 of the bitcoin address and maps the last 8 bits
 * of each word into values for red, green and blue.
 * */ 

    var hash = CryptoJS.MD5(address), 
        words = $.map(hash.words, function(w) { return Math.abs(w) });
 
    // TODO replace me with a better function!
    var red   = words[0] % 256,
        blue  = words[1] % 256,
        green = words[2] % 256;

    return 'rgb(' + red + ', ' + green + ', ' + blue + ')'
}
