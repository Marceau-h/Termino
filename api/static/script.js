function prevPage() {
    const img_url = document.getElementById('original').src;
    const img_path = img_url.split('/').slice(0, -1).join('/');
    const img_suffix = img_url.split('/').pop().split('.')[1];
    let img_id = img_url.split('/').pop().split('.')[0];
    img_id = parseInt(img_id);
    if (img_id > 1) {
        img_id -= 1;
        document.getElementById('original').src = img_path + '/' + img_id + '.' + img_suffix;
    }
}

function nextPage() {
    const img_url = document.getElementById('original').src;
    const img_path = img_url.split('/').slice(0, -1).join('/');
    const img_suffix = img_url.split('/').pop().split('.')[1];
    let img_id = img_url.split('/').pop().split('.')[0];
    img_id = parseInt(img_id);
    if (img_id < 10) {
        img_id += 1;
        document.getElementById('original').src = img_path + '/' + img_id + '.' + img_suffix;
    }
}
