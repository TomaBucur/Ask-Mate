// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {

    if (sortDirection === "asc") {
        items.sort((a, b) => a.Description.localeCompare(b.Description))
    } else {
        items.sort((a, b) => b.Description.localeCompare(a.Description))
    }

    return items
}

function getFilteredItems(items, filterValue) {

    let result = []

    for (let i=0; i<items.length; i++) {
        if (filterValue.startsWith('!Description:')) {
            if (!items[i].Description.includes(filterValue.replace('!Description:', ''))) {
                result.push(items[i])
            }
        } else if (filterValue[0] === '!') {
            if (!items[i].Title.includes(filterValue.substr(1))) {
                result.push(items[i])
            }
        } else if (filterValue.startsWith('Description:')){
            if (items[i].Description.includes(filterValue.replace('Description:', ''))) {
                result.push(items[i])
            }
        } else {
            if (items[i].Title.includes(filterValue)) {
                result.push(items[i])
            }
        }
    }

    return result
}

function toggleTheme() {
   const bodyElement = document.querySelector('body');
   const tabel_element = document.querySelector("table");
   let style = window.getComputedStyle(bodyElement).getPropertyValue('background-color');
   if (style === "rgba(0, 0, 0, 0)") {
       bodyElement.style.backgroundColor = 'rgba(0, 0, 0, 1)';
       bodyElement.style.color = 'rgb(255, 255, 255)';
       tabel_element.style.color = 'rgb(255, 255, 255)'
   } else {
       console.log("yee")
       bodyElement.style.backgroundColor = 'rgba(0, 0, 0, 0)'
       bodyElement.style.color = 'rgb(0, 0, 0)';
       tabel_element.style.color = 'rgb(0, 0, 0)'
   }
}

function increaseFont() {
    // console.log("increaseFont")
    const bodyElement = document.querySelector('table');
    let style = window.getComputedStyle(bodyElement).getPropertyValue('font-size');
    let currentSize = parseFloat(style);
    if (currentSize < 15) bodyElement.style.fontSize = (currentSize + 1) + 'px'
}

function decreaseFont() {
    // console.log("decreaseFont")
    const bodyElement = document.querySelector('table');
    let style = window.getComputedStyle(bodyElement).getPropertyValue('font-size');
    let currentSize = parseFloat(style)
    if (currentSize > 3) bodyElement.style.fontSize = (currentSize - 1) + 'px'
}
