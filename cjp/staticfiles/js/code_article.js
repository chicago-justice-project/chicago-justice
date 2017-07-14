var Locs = []; //array for location dictionaries

var locationsSelector = "#locsHiddenInput";
var articleBodySelector = ".articleBody";

function updateForm() {
    locsJSON = JSON.stringify(Locs);
    $(locationsSelector).attr("value", locsJSON);
}

function getSelectionCharOffsets() {
  // Get and return the start and end points of the selected text, using the
  // length of the selection to get the end rather than the range property
  // `endOffset`
  if (typeof window.getSelection != "undefined") {
    selection = window.getSelection();
    text = selection.toString();
    range = selection.getRangeAt(0);
    start = range.startOffset;
    end = start + text.length;
  }
  return {
    start: start,
    end: end,
  };
}

function updateHighlights(locsDict, element) {
  // First we need to consruct an array of ranges from Loc dictionaries as
  // markRanges() requires an array of starts and lengths
  locRanges = [];
  for (var arr in locsDict){
    locStart = locsDict[arr]["start"];
    locEnd = locsDict[arr]["end"];
    locLength = locEnd - locStart;
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
  targetObj = -1; // Number to store location of target in Locs array

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
    alert("Location could not be found in Locs");
  }
}

// Load and display any location data sent from server
$(document).ready(function(){
  Locs = JSON.parse($(locationsSelector).val());
  $(articleBodySelector).unmark(); // Make sure there are no marks
  updateHighlights(Locs, $(articleBodySelector));
  setupListeners();
});

function setupListeners() {

  $(document).on("click", "#btnRemove", function(){
    // Get ID of <div> element that is the parent of the remove button
    // which is also the data-target of the corresponding <mark> element
    btnId = $(this).closest('.webui-popover').attr('id');

    // Get ID of corresponding <mark> element. This ID is the start integer
    // of the location string that has been marked
    markId = $('mark[data-target=' + btnId + ']').attr('id');
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

  $(articleBodySelector).mouseup(function(){
    // Get selected text
    selection = window.getSelection();
    locText = selection.toString();

    // Check if selection overlaps something already marked
    overlap = false;
    // Get all the marks in the document
    marks = document.getElementsByTagName("mark");
    // If something is actually selected and there are marks, loop through them to see if the selection contains any of them
    if (locText && marks){
      for (var i = 0; i < marks.length; i++){
        if (selection.containsNode(marks[i], true)){
          overlap = true;
          break; // An overlap has been found, so we can exit loop
        } else {
          continue;
        }
      }
    }

    // If there is selected text and it doesn't contain a mark node, let's roll
    if (locText && !overlap) {
      // Confirm that the user actually wants to add the location
      if (confirm("Add the following location?\n\n" + locText) == true){
        $(this).unmark(); // Make sure any previous marks do not interfere
        locStart = getSelectionCharOffsets().start;
        locEnd = getSelectionCharOffsets().end;
        Locs.push({'start': locStart, 'end': locEnd, 'text': locText});
        updateForm();
        updateHighlights(Locs, $(this));
      } else{ // "Cancel" is selected in confirmation popup
        // Don't do anything
      }
    } else if (overlap) { // If there is an overlap, throw an error message
      alert("Error!\n\nPlease make sure your selection does not overlap any part of an already marked location.");
    }
  });

}