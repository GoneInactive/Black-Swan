const fs = require('fs');
const path = require('path');

const imagesDir = __dirname;
const supportedExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'];

fs.readdir(imagesDir, (err, files) => {
  if (err) {
    console.error('Failed to read directory:', err);
    return;
  }

  const imageFiles = files.filter(file => 
    supportedExtensions.includes(path.extname(file).toLowerCase())
  );

  imageFiles.forEach(image => {
    const imgPath = path.join(imagesDir, image);
    const relativePath = `./${image}`;
    console.log(`<img src="${relativePath}" alt="${path.basename(image, path.extname(image))}" width="300">`);
  });
});
