document.addEventListener("DOMContentLoaded", function () {
    var scanBtn = document.createElement("button");
    scanBtn.type = "button";
    scanBtn.textContent = "Scan Network for Printers";
    scanBtn.style.margin = "10px 0";

    var ipField = document.getElementById("id_ip_address");
    var nameField = document.getElementById("id_name");
    var portField = document.getElementById("id_port"); // assuming there's a field with this ID

    var select = document.createElement("select");
    select.style.marginTop = "10px";
    select.style.display = "none";

    // Helper to parse IP and port from URI
    function extractIpAndPort(uri) {
        try {
            var url = new URL(uri);
            return {
                ip: url.hostname,
                port: url.port || (url.protocol === "https:" ? "443" : "80")
            };
        } catch (e) {
            console.error("Invalid URI:", uri);
            return { ip: "", port: "" };
        }
    }

    scanBtn.onclick = function () {
        scanBtn.disabled = true;
        scanBtn.textContent = "Scanning...";
        fetch(window.location.origin + "/admin/printers/printer/scan-printers/")
            .then(function (response) { return response.json(); })
            .then(function (data) {
                select.innerHTML = "<option value=''>-- Select a printer --</option>";
                data.forEach(function (printer) {
                    const { ip, port } = extractIpAndPort(printer.device_uri);
                    var option = document.createElement("option");
                    option.value = printer.device_uri;
                    option.textContent = `${printer.name} (${ip}:${port})`;
                    option.setAttribute("data-name", printer.name);
                    option.setAttribute("data-ip", ip);
                    option.setAttribute("data-port", port);
                    select.appendChild(option);
                });
                select.style.display = "block";
                scanBtn.disabled = false;
                scanBtn.textContent = "Scan Network for Printers";
            })
            .catch(function (error) {
                console.error("[Scan Error]", error);
                scanBtn.disabled = false;
                scanBtn.textContent = "Scan Network for Printers";
            });
    };

    select.onchange = function () {
        var selected = select.options[select.selectedIndex];
        if (selected) {
            ipField.value = selected.getAttribute("data-ip") || "";
            if (portField) {
                portField.value = selected.getAttribute("data-port") || "";
            }
            if (selected.getAttribute("data-name") && nameField.value.trim() === "") {
                nameField.value = selected.getAttribute("data-name");
            }
        }
    };

    ipField.parentElement.appendChild(scanBtn);
    ipField.parentElement.appendChild(select);
});
