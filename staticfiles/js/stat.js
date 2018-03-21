 
function makeVisible(tableId, button) {
    document.getElementById(tableId).style.display = 'table';
    button.style.display='none';
}

function getUniqueKeys(data) {
    var unique = []
    for (var d in data) {
        unique.push(d);
    }
    return unique;
}

function drawCrimeReport(xName, countData, divName) {
    var data = new google.visualization.DataTable();
    
    data.addColumn('string', xName);
    data.addColumn('number', 'CPD Crime Reports');
    data.addRows(countData);

    var chart = new google.visualization.AreaChart(document.getElementById(divName));
    chart.draw(data, {height: 240, title: 'CPD Crime Reports Per ' + xName,
                      hAxis: {title: xName, titleTextStyle: {color: 'red'}, slantedText: 0},
                      vAxis: {title: 'Count', titleTextStyle: {color: 'red'}}
                     });
}

function drawFeed(feedNames, items, counts, xName, divName) {

    var data = new google.visualization.DataTable();
    
    data.addColumn('string', xName);
    for (var f = 0; f < feedNames.length; f++) {
        data.addColumn('number', feedNames[f]);
    }
    data.addRows(items.length);
    
    items.sort();
    for (var m = 0; m < items.length; m++) {
        data.setValue(m, 0, items[m]);
        for (var f = 0; f < feedNames.length; f++) {
            var key = feedNames[f] + "-" + items[m];
            if (key in counts) {
                data.setValue(m, f + 1, counts[key]);
            } else {
                data.setValue(m, f + 1, 0);
            }
        }
    }

    var chart = new google.visualization.AreaChart(document.getElementById(divName));
    chart.draw(data, {height: 240, title: 'Feeds Per ' + xName,
                      hAxis: {title: xName, titleTextStyle: {color: 'red'}},
                      vAxis: {title: 'Count', titleTextStyle: {color: 'red'}}
                     });
}