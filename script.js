// script.js
    document.getElementById('uploadForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];

        if (!file) {
            alert('Please select a file.');
            return;
        }

        // Create a FormData object and append the file
        const formData = new FormData();
        formData.append('file', file);

        // Pinata API credentials (replace with your actual API key and secret)
        const pinataApiKey = '8478db7513b5db5bb605  ';
        const pinataSecretApiKey = '2a1c9a10bec13ef3121298c8b7bdf89d4fb0784ef38bbebe6bbe599dd9caff07';

        try {
            const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
                method: 'POST',
                headers: {
                    'pinata_api_key': pinataApiKey,
                    'pinata_secret_api_key': pinataSecretApiKey
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            const cid = data.IpfsHash;

            // Display the result
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <p>File uploaded successfully!</p>
                <p>CID: ${cid}</p>
                <p><a href="https://salmon-just-kangaroo-237.mypinata.cloud/ipfs/${cid}" target="_blank">View File</a></p>
                <p><a href="https://salmon-just-kangaroo-237.mypinata.cloud/ipfs/${cid}" download>Download File</a></p>
            `;
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Error uploading file. Please try again.');
        }
    });
