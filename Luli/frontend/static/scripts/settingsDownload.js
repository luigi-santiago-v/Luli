// Function to handle button click
function handleDownloadSettings(buttonElement) {
    console.log('Button Element:', buttonElement);
    console.log('Outer HTML:', buttonElement.outerHTML);
    const friendId = buttonElement.getAttribute('data-friend-id');
    console.log('FRIEND ID: ', friendId)
    fetch(`/download_settings/${friendId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Failed to download settings: ' + data.error);
            } else {
                console.log('Downloaded settings:', data);
                applySettings(data);
            }
        })
        .catch(error => console.error('Error downloading settings:', error));
}