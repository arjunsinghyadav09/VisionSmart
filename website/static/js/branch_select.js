document.addEventListener("DOMContentLoaded", function() {
    var branchLinks = document.querySelectorAll('.branch-link');

    branchLinks.forEach(function(link) {
      link.addEventListener('click', function(event) {
        event.preventDefault();
        var branch = link.getAttribute('data-branch');

        var subjectColumns = document.querySelectorAll('.subject-column');
        subjectColumns.forEach(function(column) {
          column.style.display = 'none';
        });

        var branchSubjectColumns = document.querySelectorAll('.subject-column.' +branch);
        branchSubjectColumns.forEach(function(column) {
          column.style.display = '';
        });
      });
    });
  });