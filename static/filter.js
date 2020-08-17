let stamp = -1;
/**
 * Retrieves the groupTable and filter filterInput
 * Hides cells that have no text in them (filtered out)
 */
function filter() {
    let input = document.getElementById("filterInput");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("groupTable");
    let rows = table.rows;

    for (let i = 0; i < rows.length; i++) {
        let cell = rows[i].cells[0];
        if (cell) {
            let cell_value = cell.textContent;

            if (cell_value.toLowerCase().indexOf(filter) > -1) {
                rows[i].hidden = false;
            } else {
                rows[i].hidden = true;
            }
        }
    }
}
/**
 * Fetches URL '/treeserve/create/<group>'
 * @Param group A UNIX group
 */
function startInstance(group) {
    fetch('/treeserve/create/'.concat('', group),
        {method: 'POST'});
}

/**
 * Fetches URL '/treeserve/destroy/<group>'
 * @Param group A UNIX group
 */
function destroyInstance(group) {
    fetch('/treeserve/destroy/'.concat('', group),
        {method: 'POST'});
}

/**
 * Changes the layout for instances that are "Up"
 * @Param groups A list of information about groups
 * @Param row  A list columns in a row and their contents
 */
function modifyUpRowContents(groups, row) {
    row.cells[1].innerHTML = "Estimated build time: " + groups['build_time']
    + "<br>Status: " + groups['status'];

    let button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.setAttribute('class', 'btn btn-primary')
    button.setAttribute('onclick', "destroyInstance(\""
    + groups['group_name'] + "\")");
    button.textContent = "Destroy";

    let text = document.createElement('div');
    text.innerHTML = "Prune time: " + groups['prune_time'] + "<br>Created: "
    + groups['creation_time'];

    let link = document.createElement('div');
    if (groups['status'] === "up") {
        link.innerHTML = '<a href="/treeserve/view/' + groups['group_name'] + '/index.html" target="_blank" rel="noopener noreferrer">View Lustretree</a>'
    }

    row.cells[2].textContent = "";
    row.cells[2].appendChild(button);
    row.cells[2].appendChild(text);
    if (groups['status'] === "up") {
        row.cells[2].appendChild(link)
    }
}

/**
 * Changes the layout for instances that are "Down"
 * @Param groups A list of information about groups
 * @Param row  A list columns in a row and their contents
 */
function modifyDownRowContents(groups, row) {
    row.cells[1].innerHTML = "Estimated build time: " + groups['build_time']
    + "<br>Status: " + groups['status'];

    let button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.setAttribute('class', 'btn btn-primary')
    button.setAttribute('onclick', "startInstance(\""
    + groups['group_name'] + "\")");
    button.textContent = "Launch";

    row.cells[2].textContent = "";
    row.cells[2].appendChild(button);
}

/**
 * Modifies the group table dependent on status of the group
 */
function updateGroupTable() {
    fetch('/treeserve/update?stamp='.concat('', stamp))
        .then(function(response) {
            return response.json();
        })
        .then(function(result) {
            if (result === "OK") {
                return false;
            }

            stamp = result['stamp'];
            let groups = result['groups']
            let table = document.getElementById("groupTable");
            let rows = table.rows;

            for (let i = 0; i < rows.length; i++) {
                let name_cell = rows[i].cells[0];
                let name = name_cell.textContent;

                if (Object.keys(groups).includes(name)) {
                    if (groups[name]["status"] === "up") {
                        modifyUpRowContents(groups[name], rows[i]);
                    } else if (groups[name]["status"] === "building"){
                        modifyUpRowContents(groups[name], rows[i])
                    } else if (groups[name]["status"] === "down") {
                        modifyDownRowContents(groups[name], rows[i]);
                    }
                }
            }
        });
}

fetch('/treeserve/status')
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result != "up") {
            let warning = document.getElementById("warning");
            warning.style.visibility = "visible";
        }
    })

setInterval(updateGroupTable, 2000);
