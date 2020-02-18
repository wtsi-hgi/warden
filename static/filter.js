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
    fetch('/create/'.concat('', group));
}

function destroyInstance(group) {
    fetch('/destroy/'.concat('', group));
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

    row.cells[2].textContent = "";
    row.cells[2].appendChild(button);
    row.cells[2].appendChild(text);
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
    fetch('/update')
        .then(function(response) {
            return response.json();
        })
        .then(function(result) {
            let groups = result;
            let table = document.getElementById("groupTable");
            let rows = table.rows;

            if (groups === "OK") {
                // database hasn't changed, no need to update
                return false;
            }

            for (let i = 0; i < rows.length; i++) {
                let name_cell = rows[i].cells[0];
                let name = name_cell.textContent;

                if (Object.keys(groups).includes(name)) {
                    if (groups[name]["status"] === "up") {
                        modifyUpRowContents(groups[name], rows[i]);
                    } else if (groups[name]["status"] === "down") {
                        modifyDownRowContents(groups[name], rows[i]);
                    }
                }
            }
        });
}

setInterval(updateGroupTable, 1000);
