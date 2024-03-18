function showForm(userType) {
            document.getElementById('admin-form').style.display = userType === 'admin' ? 'block' : 'none';
            document.getElementById('student-form').style.display = userType === 'student' ? 'block' : 'none';
        }
 const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            checkboxes.forEach(cb => {
                if (cb !== this) cb.checked = false;
            });
        });
    });
  function showForm(userType) {
            document.getElementById('admin-form').style.display = userType === 'admin' ? 'block' : 'none';
            document.getElementById('student-form').style.display = userType === 'student' ? 'block' : 'none';
        }

   function showForm(userType) {
            document.getElementById('admin-form').style.display = userType === 'admin' ? 'block' : 'none';
            document.getElementById('student-form').style.display = userType === 'student' ? 'block' : 'none';
        }