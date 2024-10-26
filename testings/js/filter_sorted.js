var tables = document.getElementsByTagName('table');
top_search_box = "<input type='text' id='top-search-container' onkeyup='filterAllTables()' placeholder='filter on all tables'>\n"
$(top_search_box).prependTo("body");
// console.log(top_search_box);
let table_id = 0;
for (const table of tables) {
    let prepa_search_boxes = "<tr>\n";
    let column_id = 0;
    table.id = table_id;

    for (const cell of table.tHead.rows.item(0).cells) {
      cell.onclick = (function(table_id, column_id) {
          return function() {
              sortTable(table_id, column_id);
          };
      })(table_id, column_id);
      prepa_search_boxes = prepa_search_boxes + "<th><input type='text' class='search-container' onkeyup='filterTable(" +
        table_id + "," + column_id + ")' placeholder='filter by " + cell.innerText   + "'></th>\n";
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

  function filterTable(table_id,column=0) {
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
      filterColumn(table_id,columnId);
      columnId++;
    }
  }


  function filterColumn(table_id,column) {
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



  function sortTable(table_id,column) {
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