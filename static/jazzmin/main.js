var jazzmin_version = document.querySelector('footer div');
jazzmin_version.className = 'd-none';

window.onload = function() {
  var imageLink = document.querySelector('.field-image a');

  const imageUrl = imageLink.getAttribute('href');
  const img = new Image();
  img.src = imageUrl;
  img.width = 250; // set the width to 250 pixels
  img.style.display = "block"
  imageLink.innerHTML = ''; // clear the link's contents
  imageLink.appendChild(img); // add the image to the link
};
