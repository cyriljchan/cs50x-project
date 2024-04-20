// Pass passed python data to js script
function toJs(myVar) {
    return myVar;
}

// Add license number input for dvm registration
function dvmlicense() {
    let type = document.getElementById("type").value;
    if (type == "dvm") {
        document.getElementById("divtype").className = "col-md-2";
        document.getElementById("divuser").className = "col-md-2";
        document.getElementById("divlicense").className = "col-md-2";
    }
    else {
        document.getElementById("divtype").className = "col-md-3";
        document.getElementById("divuser").className = "col-md-3";
        document.getElementById("divlicense").className = "d-none col-md-2";
    }
}

// Load available timeslots for each date
function loadtime(timeslots) {
    let date = document.getElementById("date").value;
    let select = document.getElementById("time");
    let title = document.createElement("option");
    title.innerHTML = "Select Time";
    title.setAttribute('disabled', '');
    title.setAttribute('selected', '');

    select.innerHTML = "";
    select.appendChild(title);
    for (let time of timeslots[date]) {
        let opt = document.createElement("option");
        opt.value = time;
        opt.innerHTML = time;
        select.appendChild(opt);
    }
    return;
}
