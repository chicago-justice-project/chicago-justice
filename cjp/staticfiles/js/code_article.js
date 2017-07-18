var Locs = []; //array for location dictionaries
var locationsSelector = "#locsHiddenInput";
var articleBodySelector = ".articleBody";
function updateForm() {
    var locsJSON = JSON.stringify(Locs);
    $(locationsSelector).attr("value", locsJSON);
}
// Adapted from: https://stackoverflow.com/questions/4811822/get-a-ranges-start-and-end-offsets-relative-to-its-parent-container
function getSelectionWithin(element) {
  var start = 0; // Start point of selection with relation to `element`
  var end = 0; // End point of selection with relation to `element`
  var collapsed = true; // Whether or not selection contains text
  var overlap = false; // Whether the selection overlaps any current marks
  var text = ''; // Store selected text
  var markNodes = document.getElementsByTagName("mark");
  var doc = element.ownerDocument || element.document;
  var win = doc.defaultView || doc.parentWindow;
  var sel; // To store selection

  if (typeof win.getSelection != "undefined") {
    sel = win.getSelection();
    var range = sel.getRangeAt(0);
    var preCaretRange = range.cloneRange();
    try {
      text = sel.toString().replace(/[\r\n]+/g, " "); // Replace any newlines with a space
    } catch (e) {
      alert("Error!\n\nUnable to get selected text. See console error log for details.");
      console.error(e);
    }
    if (sel.rangeCount > 0){
      // Check for any overlaps if there are marks
      if (markNodes.length > 0){
        try {
          for (var i = 0; i < markNodes.length; i++) {
            if (sel.containsNode(markNodes[i], true)){
              overlap = true;
            }
          }
        } catch (error) { // MSIE--Not as robust as `containsNode` method but should work
          console.warn(error);
          try {
            var rangeContentsFragment = range.cloneContents();
            if (rangeContentsFragment.querySelector("mark")) {
              overlap = true;
            }
          } catch (e) {
            console.error(e);
          }
        }
      }
      preCaretRange.selectNodeContents(element);
      var elementContents = preCaretRange.cloneContents();
      preCaretRange.setEnd(range.startContainer, range.startOffset);
      start = preCaretRange.toString().length;
      preCaretRange.setEnd(range.endContainer, range.endOffset);
      end = preCaretRange.toString().length;
      if (end - start !== 0) {
        collapsed = false;
      }
    }
  }
  return {start: start, end: end, collapsed: collapsed, overlap: overlap, text: text};
}
function updateHighlights(locsDict, element) {
  // First we need to consruct an array of ranges from Loc dictionaries as
  // markRanges() requires an array of starts and lengths
  var locRanges = [];
  for (var arr in locsDict){
    var locStart = locsDict[arr]["start"];
    var locEnd = locsDict[arr]["end"];
    var locLength = locEnd - locStart;
    locRanges.push({'start': locStart, 'length': locLength})
  }
  // Make sure we start from the last highlight by position to the first
  locRanges.sort(function(a, b){ return a.start - b.start });
  locRanges.reverse();
  // Mark the ranges with the class "hilite" and the id corresponding with the
  // start of the highlighted string
  $(element).markRanges(locRanges, {"className": "hilite", "each": function(node, range){
    $(node).attr('id', range['start']);
  }});
}
function removeLoc(start){
  var targetObj = -1; // Number to store location of target in Locs array

  // Traverse Locs array until the dictionary with the target start is found
  for (var key in Locs){
    if (Locs[key]["start"] == start){ // Use == as LHS is number but RHS is string
      targetObj = key;
      break;
    } else {
      continue;
    }
  }

  if (targetObj != -1){ // Target object found
    Locs.splice(targetObj, 1); // Remove target from Locs array
    // Update the locations in the hidden form element and the marked highlights
    updateForm();
    $(articleBodySelector).unmark();
    updateHighlights(Locs, $(articleBodySelector));
  } else { // No target object found
    alert("Error!\n\nLocation could not be found in array of locations.");
  }
}
$(document).ready(function(){
  // Load and display any location data sent from server
  Locs = JSON.parse($(locationsSelector).val());
  $(articleBodySelector).unmark(); // Make sure there are no marks
  updateHighlights(Locs, $(articleBodySelector));
  $(document).on("click", "#btnRemove", function(){
    // Get ID of <div> element that is the parent of the remove button
    // which is also the data-target of the corresponding <mark> element
    var btnId = $(this).closest('.webui-popover').attr('id');

    // Get ID of corresponding <mark> element. This ID is the start integer
    // of the location string that has been marked
    var markId = $('mark[data-target=' + btnId + ']').attr('id');
    // Close popover
    $('#' + markId).webuiPopover('hide');
    // Remove that mark
    removeLoc(markId);
  });

  $(articleBodySelector).on("click", "mark", function(){
    // When highlighted location is clicked create then show popover confirming
    // removal of location
    $(this).webuiPopover({trigger: 'manual', closeable: true, content: '<input id="btnRemove" type="Submit" value="Remove"/>'});
    $(this).webuiPopover('show');
  });

  // Change cursor when beginning to select text in article body
  $(articleBodySelector).mousedown(function(){
    $(this).css('cursor', 'crosshair');
  });

  $(articleBodySelector).mouseup(function(){
    // Get selection
    var locSelection = getSelectionWithin($(this).get(0));

    // If there is no selected text, reset cursor and stop
    if (locSelection.collapsed){
      $(this).css('cursor', '');
      return;
    }

    // If there is selected text and it doesn't contain a mark node, let's roll
    if (!locSelection.collapsed && !locSelection.overlap) {
      if (locSelection.text !== ''){ // Ensure text has been selected
        Locs.push({'start': locSelection.start, 'end': locSelection.end, 'text': locSelection.text});
        updateForm();
        updateHighlights(Locs, $(this));
        // Indicate newly created mark
        $('mark#' + locSelection.start).animate({backgroundColor: '#FFF'}, 500);
        $('mark#' + locSelection.start).animate({backgroundColor: '#FC0'}, 500);
      } else {
      alert("Error!\n\nThere was a problem getting the selected text.")
      }
    } else if (locSelection.overlap) { // If there is an overlap, throw an error message
      alert("Error!\n\nPlease make sure your selection does not overlap any part of an already marked location.");
    } else { // Something went wrong, likely using an unsupported browser
      alert("Error!\n\nThe selection could not be correctly identified.");
      updateHighlights(Locs, $(this));
    }

    // Reset cursor
    $(this).css('cursor', '');
  });
});
