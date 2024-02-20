// function prevPage() {
//     const prev = document.getElementById('page-prev');
//     prev.disabled = true;
//
//     const first_page = parseInt(document.getElementById('first-page').value);
//     const img_url = document.getElementById('original').src;
//     const img_path = img_url.split('/').slice(0, -1).join('/');
//     const img_suffix = img_url.split('/').pop().split('.')[1];
//     let img_id = img_url.split('/').pop().split('.')[0];
//     img_id = parseInt(img_id);
//     if (img_id > first_page) {
//         img_id -= 1;
//         document.getElementById('original').src = img_path + '/' + img_id + '.' + img_suffix;
//     }
//
//     prev.disabled = false;
// }

function prevPage() {
    const prev = document.getElementById('page-prev');
    prev.disabled = true;
    prev.className = "btn nav loading";

    var img = new Image();
    img.onload = function() {
        document.getElementById('original').src = img.src;
        prev.disabled = false;
        prev.className = "btn nav";
    }
    const first_page = parseInt(document.getElementById('first-page').value);
    const img_url = document.getElementById('original').src;
    const img_path = img_url.split('/').slice(0, -1).join('/');
    const img_suffix = img_url.split('/').pop().split('.')[1];
    let img_id = img_url.split('/').pop().split('.')[0];
    img_id = parseInt(img_id);

    if (img_id > first_page) {
        img_id -= 1;
        img.src = img_path + '/' + img_id + '.' + img_suffix;

    }
    else {
        prev.disabled = false;
        prev.className = "btn nav";

    }



}

function nextPage() {
    const next = document.getElementById('page-next');
    next.disabled = true;

    const last_page = document.getElementById('last-page').value;
    const img_url = document.getElementById('original').src;
    const img_path = img_url.split('/').slice(0, -1).join('/');
    const img_suffix = img_url.split('/').pop().split('.')[1];
    let img_id = img_url.split('/').pop().split('.')[0];
    img_id = parseInt(img_id);
    if (img_id < last_page) {
        img_id += 1;
        document.getElementById('original').src = img_path + '/' + img_id + '.' + img_suffix;
    }

    next.disabled = false;
}

function resetForm() {
    really = confirm('Êtes-vous sûr de vouloir réinitialiser votre correction ?\n'
        + 'Toutes les modifications seront perdues. (À jamais !)');
    if (really) {
        document.getElementById('ocr-form').reset();
        alert('Votre correction a bien été réinitialisée.');
    }
}

function submitForm() {
    really = confirm('Êtes-vous sûr de vouloir soumettre votre correction ?');
    if (!really) {
        return;
    }

    document.getElementById('send').disabled = true;

    ocr = document.getElementById('ocr').value;
    ocr_bak = document.getElementById('ocr-original').value;
    if (ocr === ocr_bak) {
        really = confirm('Votre correction ne contient aucune modification.\n'
            + 'Êtes-vous sûr de vouloir soumettre votre correction ?');
        if (!really) {
            document.getElementById('send').disabled = false;
            return;
        }
    }

    const form = document.getElementById('ocr-form');
    const data = new FormData(form);
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/submit', true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            alert('Votre correction a bien été soumise.');
        } else {
            document.getElementById('send').disabled = false;
            alert('Une erreur est survenue lors de la soumission de votre correction.');
        }
    };

    console.log('-----------------\nSending data: ');
    for (const [key, value] of data.entries()) {
        console.log(key, value);
    }
    console.log('-----------------');

    xhr.send(data);

    // Wait for the xhr to be sent
    setTimeout(function () {
        location.reload();
    }, 1000);

}

function bad() {
    alert('Si vous êtes sur une image ne correspondant pas au texte actuel, veuillez naviguer jusqu\'à la bonne page.\n'
        + 'Par la suite, vous pouvez valider la nouvelle page en cliquant sur le bouton "Bonne page".');

    const bad = document.getElementById('bad');
    bad.disabled = true;
    bad.style.display = "none";

    const good = document.getElementById('good');
    good.disabled = false;
    good.style.display = "inline-block";


    document.getElementById('ocr').disabled = true;

    document.getElementById('good-page').value = "NOPE";
}

function good() {
    alert("Nouvelle correspondance enregistrée.");

    const good = document.getElementById('good');
    good.disabled = true;
    good.style.display = "none";

    const bad = document.getElementById('bad');
    bad.disabled = false;
    bad.style.display = "inline-block";

    document.getElementById('ocr').disabled = false;

    const img_url = document.getElementById('original').src;
    const img_id = img_url.split('/').pop().split('.')[0];

    console.log("URL: " + img_url + " ID: " + img_id);

    document.getElementById('corresponding').value = img_id;
}

function passer() {
    ocr = document.getElementById('ocr').value;
    ocr_bak = document.getElementById('ocr-original').value;
    if (ocr !== ocr_bak) {
        really = confirm('Votre correction contient des modifications.\n'
            + 'Êtes-vous sûr de vouloir passer à la page suivante '
            + 'sans soumettre votre correction ?');
        if (!really) {
            return;
        }
    }
    location.reload();
}


window.onbeforeunload = function () {
    ocr = document.getElementById('ocr').value;
    ocr_bak = document.getElementById('ocr-original').value;
    if (ocr !== ocr_bak) {
        return "Attention ! Vous avez des modifications non sauvegardées.";
    }
    return null;
}

function getCookie() {
    xhr = new XMLHttpRequest();
    xhr.open("get", "/read_cookie", false);
    xhr.send();
    return xhr.responseText;

}

function setCookie(cookie) {
    xhr = new XMLHttpRequest();
    xhr.open("get", "/set_cookie", false);
    xhr.send(cookie);
}

function init() {
    cookie = JSON.parse(getCookie());
    mazette = cookie['mazette'];
    if (mazette === null) {
        console.log("Empty cookie, first visit ? ");
        setCookie();
    }
}

init();

