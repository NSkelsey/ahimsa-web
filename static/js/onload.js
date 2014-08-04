function onload() {
/* Executes when the page has fully loaded and we are ready to add custom JS.
 * Currently this function:
 *  - Styles addressses with colors
 *
 * */
    d3.selectAll('.addr')[0].forEach(function(elem) {
        d3.select(elem).call(addrname);
    });
}
$(document).ready(onload);



