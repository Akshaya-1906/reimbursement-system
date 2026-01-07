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

    // clear rows except header
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    bills.forEach((bill, index) => {
        let row = table.insertRow();
        row.innerHTML = `
            <td>${bill.name}</td>
            <td><input required></td>
            <td>
                <input type="number" min="0" step="0.01"
                       oninput="calculateGrandTotal()" required>
            </td>
            <td><input class="name" readonly></td>
            <td><input class="account" readonly></td>
            <td><input class="ifsc" readonly></td>
            <td><input class="branch" readonly></td>
        `;
    });

    calculateGrandTotal()
}


function syncCommon() {
    document.querySelectorAll(".name")
        .forEach(e => e.value = custName.value);
    document.querySelectorAll(".account")
        .forEach(e => e.value = account.value);
    document.querySelectorAll(".ifsc")
        .forEach(e => e.value = ifsc.value);
    document.querySelectorAll(".branch")
        .forEach(e => e.value = branch.value);
}

function prepareData() {
    if (bills.length === 0) {
        alert("Please upload at least one bill");
        return false;
    }

    let table = document.getElementById("dataTable");
    let rows = [];

    for (let i = 1; i < table.rows.length; i++) {
        let cells = table.rows[i].querySelectorAll("input");
        let row = [
            bills[i - 1].name,   // bill file
            cells[0].value,     // shop
            cells[1].value,     // bill amount
            cells[2].value,     // name
            cells[3].value,     // account
            cells[4].value,     // ifsc
            cells[5].value,     // branch
                 
        ];
        rows.push(row);
    }

    document.getElementById("tableData").value = JSON.stringify({
        rows: rows,
        grandTotal: document.getElementById("grandTotal").innerText
    });

    // attach selected bills to form
    let dt = new DataTransfer();
    bills.forEach(b => dt.items.add(b));
    document.getElementById("billInput").files = dt.files;

    return true;
}

function calculateGrandTotal() {
    let table = document.getElementById("dataTable");
    let total = 0;

    for (let i = 1; i < table.rows.length; i++) {
        let amountInput = table.rows[i].cells[2].querySelector("input");
        total += parseFloat(amountInput.value) || 0;
    }

    document.getElementById("grandTotal").innerText = total.toFixed(2);
}


