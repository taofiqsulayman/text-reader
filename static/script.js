document.addEventListener("DOMContentLoaded", function () {
    const extractForm = document.getElementById("extractForm");
    const analyzeForm = document.getElementById("analyzeForm");

    extractForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(extractForm);
        fetch("/upload", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    document.getElementById("extractedData").innerHTML = `<p>Error: ${data.error}</p>`;
                } else {
                    // Display extracted text
                    let content = `<h3>Extracted Text</h3><pre>${data.extracted_text}</pre>`;

                    // Display extracted tables
                    content += `<h3>Extracted Tables</h3>`;
                    const tablesContainer = document.createElement("div");
                    if (data.extracted_tables && data.extracted_tables.length > 0) {
                        data.extracted_tables.forEach((tableJson, index) => {
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
                                    td.innerText = cell;
                                    rowElement.appendChild(td);
                                });
                                tableElement.appendChild(rowElement);
                            });
                            tablesContainer.appendChild(tableElement);
                        });
                    } else {
                        tablesContainer.innerHTML = "<p>No tables extracted.</p>";
                    }
                    content += tablesContainer.outerHTML;

                    // Display extracted information
                    content += `<h3>Extracted Information</h3><pre>${JSON.stringify(data.extracted_info, null, 2)}</pre>`;

                    // Update the DOM
                    document.getElementById("extractedData").innerHTML = content;
                }
            })
            .catch((error) => {
                document.getElementById("extractedData").innerHTML = `<p>Error: ${error}</p>`;
            });
    });

    analyzeForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(analyzeForm);
        fetch("/analyze", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    document.getElementById(
                        "analysisResult"
                    ).innerHTML = `<p>Error: ${data.error}</p>`;
                } else {
                    document.getElementById("analysisResult").innerHTML = `
                    <h3>Job Description</h3>
                    <pre>${data.job_description}</pre>
                    <h3>Extracted Information</h3>
                    <pre>${JSON.stringify(data.extracted_info, null, 2)}</pre>
                    <h3>Match Percentage</h3>
                    <p>${data.match_percentage}%</p>
                    <h3>Matching Skills</h3>
                    <pre>${JSON.stringify(data.matching_skills, null, 2)}</pre>
                `;
                }
            })
            .catch((error) => {
                document.getElementById(
                    "analysisResult"
                ).innerHTML = `<p>Error: ${error}</p>`;
            });
    });
});
