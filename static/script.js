    let bills = [];   // stores File objects

    document.addEventListener("DOMContentLoaded", () => {
        document.getElementById("billInput")
            .addEventListener("change", handleBills);
    });

    function handleBills(event) {
        for (let file of event.target.files) {
            if (!bills.some(b => b.name === file.name)) {
                bills.push(file);
            }
        }
        event.target.value = ""; // reset input
        renderBills();
    }

    function removeBill(index) {
        bills.splice(index, 1);
        renderBills();
    }

    function renderBills() {
        renderBillList();
        renderTable();
        syncCommon();
    }

    function renderBillList() {
        let div = document.getElementById("billList");
        div.innerHTML = "";

        bills.forEach((bill, index) => {
            let item = document.createElement("div");
            item.innerHTML = `
                ${bill.name}
                <button type="button" onclick="removeBill(${index})">❌</button>
            `;
            div.appendChild(item);
        });
    }

    function renderTable() {
    let table = document.getElementById("dataTable");

    // remove old rows
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    if (bills.length === 0) return;

    bills.forEach((bill, index) => {
        let row = table.insertRow();

        row.innerHTML = `
            <td>${index + 1}</td>
            <td><input required></td>
            <td><input type="number" min="0" required></td>
        `;

        // ONLY FIRST ROW → show merged inputs
        if (index === 0) {
            row.innerHTML += `
                <td rowspan="${bills.length}">
                    <input type="number" id="payAmount" required>
                </td>
                <td rowspan="${bills.length}">
                    <input id="bankField" readonly>
                </td>
                <td rowspan="${bills.length}">
                    <input id="ifscField" readonly>
                </td>
                <td rowspan="${bills.length}">
                    <input id="branchField" readonly>
                </td>
            `;
        }
    });

    syncCommon();
}


    function syncPayAmount(value) {
        document.querySelectorAll("#dataTable tr td:nth-child(4) input")
            .forEach(i => i.value = value);
    }

    function syncCommon() {
    let bankText = custName.value + " / " + account.value;

    let bank = document.getElementById("bankField");
    let ifscF = document.getElementById("ifscField");
    let branchF = document.getElementById("branchField");

    if (bank) bank.value = bankText;
    if (ifscF) ifscF.value = ifsc.value;
    if (branchF) branchF.value = branch.value;
}



    function prepareData() {
    if (bills.length === 0) {
        alert("Please upload at least one bill");
        return false;
    }

    let table = document.getElementById("dataTable");
    let rows = [];

    let payAmount = document.getElementById("payAmount").value;
    let bank = document.getElementById("bankField").value;
    let ifscVal = document.getElementById("ifscField").value;
    let branchVal = document.getElementById("branchField").value;

    for (let i = 1; i < table.rows.length; i++) {
        let inputs = table.rows[i].querySelectorAll("input");

        rows.push([
            i,                  // S. No
            inputs[0].value,    // Description
            inputs[1].value,    // Bill Amount
            payAmount,          // To Pay Amount (same)
            bank,               // Name & Acc
            ifscVal,            // IFSC
            branchVal           // Branch
        ]);
    }

    document.getElementById("tableData").value = JSON.stringify({
        rows: rows
    });

    // attach bills
    let dt = new DataTransfer();
    bills.forEach(b => dt.items.add(b));
    document.getElementById("billInput").files = dt.files;

    return true;
}




