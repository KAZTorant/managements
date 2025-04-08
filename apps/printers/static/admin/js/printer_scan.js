// printers/static/admin/js/printer_scan.js

document.addEventListener("DOMContentLoaded", function () {
    // Create a scan button
    var scanBtn = document.createElement("button");
    scanBtn.type = "button";
    scanBtn.textContent = "Scan Network for Printers";
    scanBtn.style.margin = "10px 0";

    // Locate the IP address and name fields
    var ipField = document.getElementById("id_ip_address");
    var nameField = document.getElementById("id_name");

    // Create a dropdown select element for discovered printers
    var select = document.createElement("select");
    select.style.marginTop = "10px";
    select.style.display = "none";

    // When the scan button is clicked, fetch the list of available printers
    scanBtn.onclick = function () {
        scanBtn.disabled = true;
        scanBtn.textContent = "Scanning...";
        // Use a relative URL based on the current admin URL.
        // Adjust if your admin URL structure differs.
        fetch(window.location.pathname + "printers/scan-printers/")
            .then(function (response) { return response.json(); })
            .then(function (data) {
                select.innerHTML = "<option value=''>-- Select a printer --</option>";
                data.forEach(function (printer) {
                    var option = document.createElement("option");
                    option.value = printer.ip;
                    option.textContent = printer.name + " (" + printer.ip + ")";
                    option.setAttribute("data-name", printer.name);
                    select.appendChild(option);
                });
                select.style.display = "block";
                scanBtn.disabled = false;
                scanBtn.textContent = "Scan Network for Printers";
            })
            .catch(function (error) {
                console.log(error)
                // alert("Scan failed.");
                scanBtn.disabled = false;
                scanBtn.textContent = "Scan Network for Printers";
            });
    };

    // When a printer is selected from the dropdown, fill in the IP and, if empty, the name fields.
    select.onchange = function () {
        var selected = select.options[select.selectedIndex];
        ipField.value = selected.value;
        if (selected.getAttribute("data-name") && nameField.value.trim() === "") {
            nameField.value = selected.getAttribute("data-name");
        }
    };

    // Append the scan button and select element after the IP address field's container.
    ipField.parentElement.appendChild(scanBtn);
    ipField.parentElement.appendChild(select);
});
