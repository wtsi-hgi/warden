let stamp = -1;

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

function startInstance(group) {
    fetch('/treeserve/create/'.concat('', group),
        {method: 'POST'});
}

function destroyInstance(group) {
    fetch('/treeserve/destroy/'.concat('', group),
        {method: 'POST'});
}

function modifyUpRowContents(groups, row) {
    row.cells[1].innerHTML = "Estimated build time: " + groups['build_time']
    + "<br>Status: " + groups['status'];

    let button = document.createElement('button');
    button.setAttribute('type', 'button');
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

function modifyDownRowContents(groups, row) {
    row.cells[1].innerHTML = "Estimated build time: " + groups['build_time']
    + "<br>Status: " + groups['status'];

    let button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.setAttribute('onclick', "startInstance(\""
    + groups['group_name'] + "\")");
    button.textContent = "Launch";

    row.cells[2].textContent = "";
    row.cells[2].appendChild(button);
}

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
