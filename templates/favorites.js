function getValue(link) {
   var xhr = new XMLHttpRequest();
   xhr.open("GET", "/analysis/get_value1/" + link + "/" , true);
   xhr.onreadystatechange = function () {
      if (xhr.readyState == 4 && xhr.status == 200) {
          btn.innerHTML = "Получено";
          btn.style.backgroundColor = "green";
          btn.style.color = "white";
      }
  }
  xhr.send();
}

function toggleStatus(id) {
  var button = document.getElementById("FavoritesButton" + id);
  if (button.className === "green-button") {
      button.className = "red-button";
      fetch(`/analysis/update_favorites/${id}`)
           .then(response => response.json())
           .then(data => console.log(data));
  } else {
      button.className = "green-button";
      fetch(`/analysis/update_favorites/${id}`)
           .then(response => response.json())
           .then(data => console.log(data));
  }
}

function navigateToValue(offset) {
 window.location.href = `/analysis/${offset}/`;
}
