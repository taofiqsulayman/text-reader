document
    .getElementById("uploadForm")
    .addEventListener("submit", async function (event) {
        event.preventDefault();

        const fileInput = document.getElementById("fileInput");
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        console.log(result);

        document.getElementById("extractedText").innerText =
            result.extracted_text || "No text extracted.";

        const tablesContainer = document.getElementById("extractedTables");
        tablesContainer.innerHTML = ""; // Clear previous results
        if (result.extracted_tables && result.extracted_tables.length > 0) {
            result.extracted_tables.forEach((tableJson, index) => {
                const table = JSON.parse(tableJson);
                const tableElement = document.createElement("table");
                const headerRow = document.createElement("tr");

                table.columns.forEach((column) => {
                    const th = document.createElement("th");
                    th.innerText = column;
                    headerRow.appendChild(th);
                });
                tableElement.appendChild(headerRow);

                table.data.forEach((row) => {
                    const rowElement = document.createElement("tr");
                    row.forEach((cell) => {
                        const td = document.createElement("td");
                        td.innerText = cell || ""; // Fill empty cells with an empty string
                        rowElement.appendChild(td);
                    });
                    tableElement.appendChild(rowElement);
                });

                tablesContainer.appendChild(tableElement);
            });
        } else {
            tablesContainer.innerText = "No tables extracted.";
        }
    });
