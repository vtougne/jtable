// var tables = document.getElementsByTagName('table');
const tables = document.querySelectorAll("table");
top_search_box = "<input type='text' id='top-search-container' onkeyup='filterAllTables()' placeholder='filter on all tables'>\n"

let selectedTable = null; // Variable pour stocker la table sélectionnée

// Écouteur pour détecter le clic sur une table
tables.forEach(table => {
  table.addEventListener("click", function () {
    selectedTable = table; // Met à jour la table actuellement sélectionnée
  });
});

// Écouteur d'événement pour intercepter Ctrl + A
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "a" && selectedTable) {
    event.preventDefault(); // Empêche la sélection de toute la page

    // Création d'une sélection pour la table sélectionnée en excluant le header
    const selection = window.getSelection();
    selection.removeAllRanges(); // Vidage de la sélection actuelle

    const range = document.createRange();

    // Vérifie s'il y a au moins une ligne dans le tbody
    if (selectedTable.tBodies[0]?.rows.length > 1) {
      // Sélection de toutes les lignes sauf la première
      range.setStartBefore(selectedTable.tHead.rows[1]);
      range.setEndAfter(selectedTable.tBodies[0].rows[selectedTable.tBodies[0].rows.length - 1]);

      selection.addRange(range); // Ajout de la sélection du contenu de la table sélectionnée
    }
  }
});


$(top_search_box).prependTo("body");
// console.log(top_search_box);
let table_id = 0;
for (const table of tables) {
  let prepa_search_boxes = "<tr>\n";
  let column_id = 0;
  table.id = table_id;

  for (const cell of table.tHead.rows.item(0).cells) {
    cell.onclick = (function (table_id, column_id) {
      return function () {
        sortTable(table_id, column_id);
      };
    })(table_id, column_id);
    prepa_search_boxes = prepa_search_boxes + "<th><input type='text' class='search-container' onkeyup='filterTable(" +
      table_id + "," + column_id + ")' placeholder='filter by " + cell.innerText + "'></th>\n";
    column_id++;
  }
  prepa_search_boxes = prepa_search_boxes + "</tr>";
  $(table.tHead).prepend(prepa_search_boxes);
  table_id++;

}
function filterAllTables() {
  var search_input = $("#top-search-container").val().toUpperCase();
  tableId = 0;
  for (const table of tables) {
    filterTable(tableId);
    tableId++;
  }
}

function filterTable(table_id, column = 0) {
  // filterAllTables()
  var top_search_input = $("#top-search-container").val().toUpperCase();

  var table = document.getElementById(table_id);
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);

  rows.forEach(function (row) {
    var cellText = row.textContent.toUpperCase();
    if (cellText.indexOf(top_search_input) > -1) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });

  let columnId = 0;
  for (const column of table.rows[0].cells) {
    input = column.querySelector("input").value;
    filterColumn(table_id, columnId);
    columnId++;
  }
}


function filterColumn(table_id, column) {
  var table = document.getElementById(table_id);
  // var input = table.rows[0].cells[column].querySelector("input");
  var input = table.rows[0].cells[column].querySelector("input");
  var filterText = input.value.toUpperCase();
  var rows = Array.prototype.slice.call(table.tBodies[0].rows).filter(row => row.style.display !== "none");
  rows.forEach(function (row) {
    var cellText = row.cells[column].textContent.toUpperCase();
    if (cellText.indexOf(filterText) > -1) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}



function sortTable(table_id, column) {
  var table = document.getElementById(table_id);
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);
  var isAscending = table.tHead.rows[0].cells[column].classList.toggle("ascending");
  var multiplier = isAscending ? 1 : -1;
  rows.sort(function (a, b) {
    var aVal = a.cells[column].textContent;
    var bVal = b.cells[column].textContent;
    if (!isNaN(aVal) && !isNaN(bVal)) {
      aVal = Number(aVal);
      bVal = Number(bVal);
      return multiplier * (aVal - bVal);
    } else {
      return multiplier * aVal.localeCompare(bVal);
    }
  });
  table.tBodies[0].innerHTML = "";
  rows.forEach(function (row) {
    table.tBodies[0].appendChild(row);
  });
}