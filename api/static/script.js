function prevANDnext() {
    const prev = document.getElementById('page-prev');
    const next = document.getElementById('page-next');
    return [prev, next];
}

function disableButton(button) {
    button.disabled = true;
    button.className = "btn nav disabled";
}

function enableButton(button) {
    button.disabled = false;
    button.className = "btn nav active";
}

function pageLoading() {
    const [prev, next] = prevANDnext();
    disableButton(prev);
    disableButton(next);
}

function pageCharged() {
    const [prev, next] = prevANDnext();
    enableButton(prev);
    enableButton(next);
}

function pageChange() {
    pageLoading();

    const img = new Image();
    img.onload = function () {
        document.getElementById('original').src = img.src;

        pageCharged();
    }
    return img;
}

function getConsts() {
    const first_page = parseInt(document.getElementById('first-page').value);
    const last_page = parseInt(document.getElementById('last-page').value);
    const img_url = document.getElementById('original').src;
    const img_path = img_url.split('/').slice(0, -1).join('/');
    const img_suffix = img_url.split('/').pop().split('.')[1];
    let img_id = img_url.split('/').pop().split('.')[0];
    img_id = parseInt(img_id);
    return [first_page, last_page, img_path, img_suffix, img_id];
}

function newSrc(img_path, img_suffix, img_id) {
    return img_path + '/' + img_id + '.' + img_suffix;

}

function prevPage() {
    const img = pageChange();

    const [first_page, _, img_path, img_suffix, img_id] = getConsts();

    if (img_id > first_page) {
        img.src = newSrc(img_path, img_suffix, img_id - 1);
    } else {
        pageCharged();
    }
}

function nextPage() {
    const img = pageChange();

    const [_, last_page, img_path, img_suffix, img_id] = getConsts();

    if (img_id < last_page) {
        img.src = newSrc(img_path, img_suffix, img_id + 1);

    } else {
        pageCharged();
    }
}

function resetForm() {
    const really = confirm('Êtes-vous sûr de vouloir réinitialiser votre correction ?\n' +
        'Toutes les modifications seront perdues. (À jamais !)');
    if (really) {
        document.getElementById('ocr-form').reset();
        alert('Votre correction a bien été réinitialisée.');
    }
}

function submitForm() {
    let really = confirm('Êtes-vous sûr de vouloir soumettre votre correction ?');
    if (!really) {
        return;
    }

    document.getElementById('send').disabled = true;

    const ocr = document.getElementById('ocr').value;
    const ocr_bak = document.getElementById('ocr-original').value;
    if (ocr === ocr_bak) {
        really = confirm('Votre correction ne contient aucune modification.\n' +
            'Êtes-vous sûr de vouloir soumettre votre correction ?');
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

    // console.log('-----------------\nSending data: ');
    // for (const [key, value] of data.entries())
    // {
    // 	console.log(key, value);
    // }
    // console.log('-----------------');

    xhr.send(data);

    // Wait for the xhr to be sent
    setTimeout(function () {
        location.reload();
    }, 1000);

}

function bad() {
    const really = confirm('Si vous êtes sur une image ne correspondant pas au texte actuel, veuillez naviguer jusqu\'à la bonne page.\n' +
        'Par la suite, vous pouvez valider la nouvelle page en cliquant sur le bouton "Bonne page".');
    if (!really) {
        return;
    }

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
    const ocr = document.getElementById('ocr').value;
    const ocr_bak = document.getElementById('ocr-original').value;
    if (ocr !== ocr_bak) {
        const really = confirm('Votre correction contient des modifications.\n' +
            'Êtes-vous sûr de vouloir passer à la page suivante ' +
            'sans soumettre votre correction ?');
        if (!really) {
            return;
        }
    }
    location.reload();
}


window.onbeforeunload = function () {
    const ocr = document.getElementById('ocr').value;
    const ocr_bak = document.getElementById('ocr-original').value;
    if (ocr !== ocr_bak) {
        return "Attention ! Vous avez des modifications non sauvegardées.";
    }
    return null;
}

function getCookie() {
    const xhr = new XMLHttpRequest();
    xhr.open("get", "/read_cookie", false);
    xhr.send();
    return xhr.responseText;

}

function setCookie(cookie) {
    const xhr = new XMLHttpRequest();
    xhr.open("get", "/set_cookie", false);
    xhr.send(cookie);
}

function setPreviousCookie(cookie, uuid) {
    const xhr = new XMLHttpRequest();
    xhr.open("get", "/set_cookie/" + uuid, false);
    xhr.send(cookie);
}


function init() {
    var search = location.search.substring(1);
    if (search !== null && search !== '') {
        search = JSON.parse('{"' + decodeURI(search).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g, '":"') + '"}')
        const uuid = search['uuid'];
        if (uuid !== null) {
            console.log('UUID found, setting cookie...');
            setPreviousCookie(null, uuid);
            return;
        }
    }


    const cookie = JSON.parse(getCookie());
    if (cookie['mazette'] === null) {
        console.log("Empty cookie, first visit ? ");
        setCookie();
    }
}

init();
