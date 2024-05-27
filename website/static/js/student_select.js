document.addEventListener("DOMContentLoaded", function() {
    var branchLinks = document.querySelectorAll('.branch-link');

    branchLinks.forEach(function(link) {
      link.addEventListener('click', function(event) {
        event.preventDefault();
        var branch = link.getAttribute('data-branch');

        var allRows = document.querySelectorAll('.branch-row');
        allRows.forEach(function(row) {
          row.style.display = 'none';
        });

        var branchRows = document.querySelectorAll('.branch-row.' + branch);
        branchRows.forEach(function(row) {
          row.style.display = '';
        });

        var subjects = document.getElementById('subjects');
        var subjectOptions = subjects.querySelectorAll('option');
        subjectOptions.forEach(function(option) {
          option.style.display = 'none';
          if (option.getAttribute('data-branch') === branch) {
            option.style.display = '';
          }
        });

        var firstVisibleSubject = subjects.querySelector('option[data-branch="' + branch + '"][style!="display: none;"]');
        if (firstVisibleSubject) {
          firstVisibleSubject.selected = true;
        }
      });
    });
  });