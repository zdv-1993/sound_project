var myModal = document.getElementById('searchModal')
var myInput = document.getElementById('searchButton')

myModal.addEventListener('shown.bs.modal', function () {
  myInput.focus()
})