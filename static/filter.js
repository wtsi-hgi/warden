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
    fetch('/create/'.concat('', group))
}

function destroyInstance(group) {
    fetch('/destroy/'.concat('', group))
}
