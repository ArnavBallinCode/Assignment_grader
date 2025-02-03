// JavaScript code for handling file upload and grading
function uploadFile() {
    const fileInput = document.getElementById('pptFile');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a PPT file.");
        return;
    }

    const formData = new FormData();
    formData.append('ppt', file);

    fetch('/grade', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const resultTable = document.getElementById('resultTable');
            resultTable.innerHTML = '';

            Object.entries(data.scores).forEach(([criteria, score]) => {
                resultTable.innerHTML += `
                    <tr>
                        <td>${criteria}</td>
                        <td>${score}</td>
                    </tr>
                `;
            });

            document.getElementById('result').style.display = 'block';
        })
        .catch(err => {
            alert('Error grading the PPT. Please try again.');
            console.error(err);
        });
}
