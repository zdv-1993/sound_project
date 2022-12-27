var searchField = document.getElementById("searchField");

var tableSearchBody = document.getElementById("tableSearchBody");


var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};


searchField.addEventListener("change", function(){
    let q = searchField.value;
    let url = new URL("http://" + window.location.hostname + ":60000/api/search");
    url.searchParams.set('q', q);
    getJSON(url, 
    function(err, data) {
    if (err !== null) {
        alert('Something went wrong: ' + err);
    } else {
      tableSearchBody.innerHTML = "";
      function appendFoundedTrack(item, data) {
        let audio_elem = document.createElement("audio");
        audio_elem.setAttribute("controls", "");
        audio_elem.setAttribute("src", item.path);
        audio_elem.setAttribute("title", item.name);
        audio_elem.setAttribute("preload", "none");

        let tr_elem = document.createElement("tr");

        let td_elem_title = document.createElement("td");
        td_elem_title.innerHTML = item.name;

        let td_elem_artist = document.createElement("td");
        td_elem_artist.innerHTML = item.artist;

        let td_elem_track = document.createElement("td");
        td_elem_track.appendChild(audio_elem);

        let ld_elem_save = document.createElement("td");
        let a_elem_save = document.createElement("a");
        a_elem_save.setAttribute("href", item.save_url);
        a_elem_save.setAttribute("onclick","saveMusic(this); return false");
        a_elem_save.className = "saveLink";
        a_elem_save.innerHTML = "+";
        ld_elem_save.appendChild(a_elem_save);

        tr_elem.appendChild(td_elem_title);
        tr_elem.appendChild(td_elem_artist);
        tr_elem.appendChild(td_elem_track);
        tr_elem.appendChild(ld_elem_save);


        tableSearchBody.appendChild(tr_elem);
        console.log(item);

      }
      data.forEach(appendFoundedTrack);
    }
    });
  });

function updateMusicFromDb() {
  let music_div_raw = document.getElementById("musicFromDb");
  music_div_raw.innerHTML = "";
  let url = new URL("http://" + window.location.hostname + ":8000/api/tracks");
  getJSON(url, 
    function(err, data) {
    if (err !== null) {
        alert('Something went wrong: ' + err);
    } else {

      function appendSound(item, data) {
        let p_elem = document.createElement("p");
        p_elem.innerHTML = item.title + " " + item.artist;
        let audio_elem = document.createElement("audio");
        audio_elem.setAttribute("controls", "");
        audio_elem.setAttribute("src", item.link);
        audio_elem.setAttribute("title", item.title);

        music_div_raw.appendChild(p_elem);
        music_div_raw.appendChild(audio_elem);

      }
      data.forEach(appendSound);
    }
    });
}

updateMusicFromDb();
 

const saveLink = document.querySelector('.saveLink');


function saveMusic(element){
  //event.preventDefault(); 
  getJSON(element.href, 
    function(err, data) {
    if (err !== null) {
        alert('Something went wrong: ' + err);
    } else {
      alert('Ok');
    }
    });
  return false;

}
  
