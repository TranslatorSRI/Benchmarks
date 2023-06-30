export const capitalizeFirstLetter = (string) => {
  if(!string)
    return '';

  let newString = string.toLowerCase();
  return newString.charAt(0).toUpperCase() + newString.slice(1);
}

export const capitalizeAllWords = (string) => {
  if(!string)
    return '';

  let newString = string.toLowerCase();
  return newString.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
}